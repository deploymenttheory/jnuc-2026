// Builds the deck downloads - one Keynote and one PowerPoint per deck - from
// the deck's own HTML. Both formats come out of a SINGLE capture pass, so the
// two downloads are the same pixels; nobody gets a second-class version.
//
// This cannot run in CI. GitHub's runners have no Keynote, and a Linux capture
// would render the decks in substitute fonts, so both files are built on a Mac
// by hand and both ARE committed. Rebuild and commit them in the same change as
// any deck edit, or the downloads on the landing page go stale.
//
//   npm run build            both formats (one capture pass)
//   npm run build:key        Keynote only  (needs Keynote installed)
//   npm run build:pptx       PowerPoint only (no Keynote needed)
//
// Every slide becomes a full-bleed image. That is the whole trick and it is
// deliberate: these decks are hand-built HTML with SVG, gradients and absolute
// positioning, none of which survives a translation into Keynote or PowerPoint
// shapes. Speaker notes are the exception - they are real text in the notes.

import { execFile } from 'node:child_process';
import { mkdir, mkdtemp, readFile, rm, stat, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { promisify } from 'node:util';
import { chromium } from 'playwright';
import PptxGenJS from 'pptxgenjs';

const execFileP = promisify(execFile);

const ROOT = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const DECKS_DIR = path.join(ROOT, 'presentations');

// Both decks scale their stage to a 1920x1080 design grid, so capturing at that
// size is a 1:1 read of the layout rather than a resample.
const VIEWPORT = { width: 1920, height: 1080 };

// Both decks change slides by swapping an .active class with a CSS transition.
// This is the settle time before the shutter; neither deck animates longer.
const SETTLE_MS = 400;

// Filenames are fixed here because presentations/index.html hardcodes them;
// changing one means changing both. The two names per deck share a stem so the
// pair reads as one download in two formats.
const DECKS = [
  {
    dir: 'migrating_an_instance',
    key: 'from-clicks-to-code-jnuc2026.key',
    pptx: 'from-clicks-to-code-jnuc2026.pptx',
    title: 'From Clicks to Code',
    subject: 'Migrating Jamf Pro to Terraform at Lloyds Banking Group',
  },
  {
    dir: 'training_a_team',
    key: 'ClickOps_to_GitOps.key',
    pptx: 'ClickOps_to_GitOps.pptx',
    title: 'ClickOps to GitOps',
    subject: 'Learning journey',
  },
];

// On-screen affordances that mean nothing in a downloaded file. The slide
// counters and the timeline strip are deliberately NOT here - the counter is
// useful on paper and the timeline is deck content, not chrome.
const HIDE_WHILE_CAPTURING = [
  '#help { display: none !important; }',
  // A <video> exports as its poster frame - nobody can press play in a .key or a
  // .pptx - so the controls are an affordance the file cannot offer. They also carry
  // Chrome's loading spinner, which sits over the poster long enough to be caught by
  // the settle below and shipped as a smudge on the slide.
  'video::-webkit-media-controls { display: none !important; }',
].join('\n');

// Runs in the page. Covers both decks without per-deck config: one keeps its
// notes in <aside class="notes">, the other in a data-notes attribute.
const readNotes = () =>
  Array.from(document.querySelectorAll('section.slide')).map((slide) => {
    const aside = slide.querySelector('aside.notes');
    const text = aside ? aside.textContent : slide.getAttribute('data-notes');
    return (text || '').replace(/\s+/g, ' ').trim();
  });

const activeIndex = () =>
  Array.from(document.querySelectorAll('section.slide')).findIndex((slide) =>
    slide.classList.contains('active'),
  );

// Screenshots go to disk rather than staying in memory: AppleScript can only
// place an image it can open by path, and the PowerPoint writer reads the same
// files back, so one pass feeds both.
async function capture(page, deck, shotsDir) {
  // file:// rather than a local server: the decks load ../_shared/speakers.js
  // with a classic script tag precisely so they work off disk.
  const url = pathToFileURL(path.join(DECKS_DIR, deck.dir, 'index.html')).href;
  await page.goto(url, { waitUntil: 'load' });
  await page.addStyleTag({ content: HIDE_WHILE_CAPTURING });
  await page.evaluate(() => document.fonts.ready);

  const notes = await page.evaluate(readNotes);
  if (notes.length === 0) throw new Error(`${deck.dir}: found no section.slide elements`);

  const shots = [];
  for (let i = 0; i < notes.length; i += 1) {
    if (i > 0) await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(SETTLE_MS);

    // Driving the deck by keypress is only safe if the keypress landed. Without
    // this check a deck that stops advancing yields N copies of one slide and
    // the failure is invisible until someone opens the download.
    const at = await page.evaluate(activeIndex);
    if (at !== i) throw new Error(`${deck.dir}: expected slide ${i + 1}, deck is showing ${at + 1}`);

    const shot = path.join(shotsDir, `slide-${String(i + 1).padStart(3, '0')}.png`);
    await page.screenshot({ type: 'png', path: shot });
    shots.push(shot);
  }

  return { notes, shots };
}

// AppleScript string literals only need backslashes and double quotes escaped.
const asString = (text) => `"${text.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`;

// Keynote's default theme names its empty master "Blank"; the first slide of a
// new document is reused, every other slide is appended. Images are placed at
// the origin and stretched to the full 1920x1080 canvas.
function keynoteScript({ notes, shots }, outPath) {
  const lines = [
    // Saving a 20-odd-slide document outlasts the default AppleEvent reply
    // timeout, so give the whole build a generous one.
    'with timeout of 900 seconds',
    'tell application "Keynote"',
    '  set theDoc to make new document with properties {width:1920, height:1080}',
    '  tell theDoc',
  ];

  shots.forEach((shot, i) => {
    if (i === 0) {
      lines.push('    set targetSlide to slide 1 of theDoc');
      lines.push('    set base slide of targetSlide to master slide "Blank" of theDoc');
    } else {
      lines.push(
        '    set targetSlide to make new slide at end of slides with properties {base slide:master slide "Blank" of theDoc}',
      );
    }
    lines.push('    tell targetSlide');
    lines.push(`      set theImage to make new image with properties {file:POSIX file ${asString(shot)}}`);
    lines.push('      set width of theImage to 1920');
    lines.push('      set position of theImage to {0, 0}');
    if (notes[i]) lines.push(`      set presenter notes to ${asString(notes[i])}`);
    lines.push('    end tell');
  });

  lines.push('  end tell');
  lines.push(`  save theDoc in POSIX file ${asString(outPath)}`);
  lines.push('  close theDoc saving no');
  lines.push('end tell');
  lines.push('end timeout');
  return lines.join('\n');
}

async function writeKeynote(deck, captured, workDir) {
  const out = path.join(DECKS_DIR, deck.dir, deck.key);
  // Save over an existing .key by removing it first: Keynote's `save in` will
  // not silently replace a package it did not open.
  await rm(out, { force: true, recursive: true });

  const scriptPath = path.join(workDir, `${deck.dir}.applescript`);
  await writeFile(scriptPath, keynoteScript(captured, out));
  try {
    await execFileP('osascript', [scriptPath]);
  } catch (err) {
    // Keynote occasionally drops the Apple-event connection (-609) under a
    // long scripted build. One clean relaunch and retry before giving up.
    console.warn(`${deck.dir}: osascript failed (${err.message.trim()}), relaunching Keynote and retrying once`);
    await execFileP('osascript', ['-e', 'tell application "Keynote" to quit']).catch(() => {});
    await new Promise((resolve) => setTimeout(resolve, 3000));
    await startKeynote();
    await rm(out, { force: true, recursive: true });
    await execFileP('osascript', [scriptPath]);
  }

  await assertPlausible(out, deck.key, deck.dir);
  return out;
}

async function writePptx(deck, { notes, shots }) {
  const pptx = new PptxGenJS();
  pptx.layout = 'LAYOUT_16x9';
  pptx.title = deck.title;
  pptx.subject = deck.subject;

  for (const [i, shot] of shots.entries()) {
    const slide = pptx.addSlide();
    const png = await readFile(shot);
    slide.addImage({
      data: `image/png;base64,${png.toString('base64')}`,
      x: 0,
      y: 0,
      w: '100%',
      h: '100%',
    });
    if (notes[i]) slide.addNotes(notes[i]);
  }

  const out = path.join(DECKS_DIR, deck.dir, deck.pptx);
  await pptx.writeFile({ fileName: out });
  await assertPlausible(out, deck.pptx, deck.dir);
  return out;
}

// A download made of 20-odd full-bleed screenshots is megabytes. Anything much
// smaller means the capture or the assembly quietly produced an empty deck.
async function assertPlausible(out, name, dir) {
  const { size } = await stat(out);
  if (size < 100_000) throw new Error(`${dir}: ${name} is implausibly small (${size} bytes)`);
}

// An AppleScript `launch` inside the tell block errors with -600 when Keynote
// is not already running, so start it the LaunchServices way and wait until it
// answers Apple events before building anything.
async function startKeynote() {
  await execFileP('open', ['-ga', 'Keynote']);
  for (let tries = 0; ; tries += 1) {
    try {
      await execFileP('osascript', ['-e', 'tell application "Keynote" to get version']);
      return;
    } catch (err) {
      if (tries >= 30) throw new Error(`Keynote did not become scriptable: ${err.message}`);
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }
}

// No arguments means both, so a bare `node tools/build-downloads.mjs` gives you
// everything the landing page links to.
const requested = new Set(process.argv.slice(2).length ? process.argv.slice(2) : ['key', 'pptx']);
for (const format of requested) {
  if (format !== 'key' && format !== 'pptx') {
    throw new Error(`unknown format "${format}" - expected key, pptx, or nothing for both`);
  }
}

const workDir = await mkdtemp(path.join(os.tmpdir(), 'jnuc-decks-'));
// Only when Keynote is actually needed: the PowerPoint build runs on any Mac.
if (requested.has('key')) await startKeynote();
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: VIEWPORT });
  for (const deck of DECKS) {
    const shotsDir = path.join(workDir, deck.dir);
    await mkdir(shotsDir, { recursive: true });
    const captured = await capture(page, deck, shotsDir);

    const written = [];
    if (requested.has('key')) written.push(await writeKeynote(deck, captured, workDir));
    if (requested.has('pptx')) written.push(await writePptx(deck, captured));

    const withNotes = captured.notes.filter(Boolean).length;
    console.log(
      `${deck.dir}: ${captured.shots.length} slides, ${withNotes} with notes -> ${written
        .map((out) => path.relative(ROOT, out))
        .join(', ')}`,
    );
  }
} finally {
  await browser.close();
  await rm(workDir, { force: true, recursive: true });
}
