// Builds one PowerPoint per deck from the deck's own HTML, so the download on
// the landing page always matches the site that just deployed. The deploy
// workflow runs this before `aws s3 sync`; the .pptx files it writes are build
// output and are gitignored on purpose - the HTML is the source of truth.
//
// Every slide becomes a full-bleed image. That is the whole trick and it is
// deliberate: these decks are hand-built HTML with SVG, gradients and absolute
// positioning, none of which survives a translation into PowerPoint shapes.
// Speaker notes are the exception - they are real text in the notes pane.

import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { chromium } from 'playwright';
import PptxGenJS from 'pptxgenjs';

const ROOT = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const DECKS_DIR = path.join(ROOT, 'presentations');

// Both decks scale their stage to a 1920x1080 design grid, so capturing at that
// size is a 1:1 read of the layout rather than a resample.
const VIEWPORT = { width: 1920, height: 1080 };

// Both decks change slides by swapping an .active class with a CSS transition.
// This is the settle time before the shutter; neither deck animates longer.
const SETTLE_MS = 400;

const DECKS = [
  {
    dir: 'migrating_an_instance',
    file: 'from-clicks-to-code-jnuc2026.pptx',
    title: 'From Clicks to Code',
    subject: 'Migrating Jamf Pro to Terraform at Lloyds Banking Group',
  },
  {
    dir: 'training_a_team',
    file: 'ClickOps_to_GitOps.pptx',
    title: 'ClickOps to GitOps',
    subject: 'Learning journey',
  },
];

// On-screen affordances that mean nothing in a downloaded file. The slide
// counters and the timeline strip are deliberately NOT here - the counter is
// useful on paper and the timeline is deck content, not chrome.
const HIDE_WHILE_CAPTURING = '#help { display: none !important; }';

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

async function capture(page, deck) {
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

    shots.push(await page.screenshot({ type: 'png' }));
  }

  return { notes, shots };
}

async function write(deck, { notes, shots }) {
  const pptx = new PptxGenJS();
  pptx.layout = 'LAYOUT_16x9';
  pptx.title = deck.title;
  pptx.subject = deck.subject;

  shots.forEach((png, i) => {
    const slide = pptx.addSlide();
    slide.addImage({
      data: `image/png;base64,${png.toString('base64')}`,
      x: 0,
      y: 0,
      w: '100%',
      h: '100%',
    });
    if (notes[i]) slide.addNotes(notes[i]);
  });

  const out = path.join(DECKS_DIR, deck.dir, deck.file);
  await pptx.writeFile({ fileName: out });
  return out;
}

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: VIEWPORT });
  for (const deck of DECKS) {
    const captured = await capture(page, deck);
    const out = await write(deck, captured);
    const withNotes = captured.notes.filter(Boolean).length;
    console.log(
      `${deck.dir}: ${captured.shots.length} slides, ${withNotes} with notes -> ${path.relative(ROOT, out)}`,
    );
  }
} finally {
  await browser.close();
}
