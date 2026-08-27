# Deck feedback workflow

How feedback on the JNUC 2026 decks turns into deployed changes. The orchestrator (the Claude
session Joseph is talking to) reads this file at the start of every round and follows it.
Feedback itself arrives in chat, never in this file. `AGENTS.md` is the reference for the
repo and the decks; this file only covers the loop. The file is committed (the deploy's
`*.md` exclude keeps it off the site); edit it in the same commit as any change to the
process. Last revised 2026-08-27.

## Standing rules

- Feedback comes in chat, usually as a list of slides with comments. This file is the
  process, not a change list - do not append requests here.
- Every change gets three alternative implementations on the sandbox, with significant
  and worthy differences, unless Joseph says otherwise for that change. He picks one in
  chat, or asks for another set. Pure deletions and wording swaps with no design dimension
  can go straight into the deck, but if in doubt offer options rather than decide.
- Work from `main`, push to `main`, deploy on every push. Do not ask.
- Fan out: one Sonnet agent per slide, each with an explicit self-contained brief, each
  delivering a PR. The orchestrator merges the PRs, consolidates, verifies and deploys. The
  orchestrator's own consolidation work is done inline - it is small and speed matters.
- The orchestrator is Joseph's point of contact and does not do slide work itself. The chat
  stays idle while agents work: every message from Joseph that contains feedback is
  dispatched straight away, without waiting for anything already in flight, and the
  orchestrator's reply is the dispatch confirmation. Results are reported as they land.
- Do not rebuild the Keynote `.key` until Joseph says so.
- Commits are authored by Joseph Little (the global git identity) with no `Co-Authored-By`
  trailer, plain human subjects, British English. No emojis, no em or en dashes anywhere.
- `AGENTS.md` is updated in the same commit as anything that makes it stale.

## Roles

**Orchestrator** - the main session. Turns chat feedback into per-slide work items,
dispatches and briefs the slide agents, verifies their PRs, merges and consolidates locally,
pushes `main` once per round, confirms the deploy, and reports back in chat with the sandbox
links. Owns the files no agent may touch: `AGENTS.md`, `presentations/sandbox/index.html`,
`presentations/sandbox/sandbox.css`, the deck tokens block, and `tools/`.

**Slide agent** - a Sonnet agent, one per slide, working in its own git worktree on its own
branch. Edits exactly one slide (its section, its CSS block, its `presenter.json` entry),
creates that slide's sandbox page, verifies with screenshots, opens a PR, reports the PR
number and evidence. Never touches another slide, the orchestrator-owned files, or `.key`.

**Verifier** - a Sonnet agent, one per PR, read-only. Checks the PR against its brief and
the checklist below and reports pass or fail with evidence. Run in parallel with the other
verifiers.

## Continuous mode

Rounds are not batched. Each feedback message is its own round: parse it, dispatch one agent
per slide it mentions, reply with what was dispatched (slide, branch name, agent), and stop.
When a PR lands, verify, merge, consolidate and deploy it on its own - do not hold it for
siblings still running unless two land within a minute of each other. Keep the "In flight"
list in the Log at the bottom of this file current at every dispatch and every merge; it is
the recovery point if the session is lost.

If Joseph's message is a decision ("slide 3, option B") rather than new feedback, it is an
acceptance round for that slide - same flow with the acceptance brief. If it is a question
or a comment with no action, answer it and stay idle.

## A round, start to finish

1. **Parse.** Turn the chat feedback into one work item per slide. Map the visible slide
   number to the section id using the "Current slide order" list in `AGENTS.md` (slide 2 is
   `#s01`, slide 3 is `#s02`; the ids are not the numbers). Several comments on one slide
   are one item. Note the speaker for each slide from the same list. Decide per item which
   parts are deterministic edits and which need three options.
2. **Dispatch.** One `Agent` call per slide, all in one message so they run in parallel:
   `subagent_type: "general-purpose"`, `model: "sonnet"`, `isolation: "worktree"`, prompt
   built from the brief template below with every placeholder filled. Never bundle two
   slides into one agent.
3. **Collect.** Each agent returns a PR number, branch name, the screenshot paths and lint
   output. If an agent returns without a PR, read its report, fix the brief, and re-dispatch
   that slide only.
4. **Verify.** One verifier agent per PR, in parallel, using the verifier brief below. Small
   failures (a stray dash, a note left stale) the orchestrator fixes on the branch itself;
   anything larger goes back to the slide agent via `SendMessage` with the verifier's report.
5. **Merge and consolidate locally** (commands below): fetch, merge each branch into `main`
   with `--no-ff` in slide order, resolve any conflict, then make one consolidation commit:
   sandbox index entries for the new pages, the `AGENTS.md` slide list and "Current pages"
   line, and anything the presenter check flags.
6. **Verify the whole.** Screenshot every touched slide from the merged `main`, plus any
   slide that shares a class with a touched one. Dash lint. Presenter sync check.
7. **Push and deploy.** Push `main` once. Confirm the deploy run, `curl` the live URLs for
   each sandbox page, delete the remote branches, prune worktrees.
8. **Report in chat.** One line per slide: the sandbox link and a few words on each of A,
   B and C. Nothing else - Joseph will reply with choices.
9. **Acceptance round.** Joseph names an option per slide in chat. Same pipeline with the
   acceptance brief: the agent writes the option into the deck as the net result, removes
   markup it makes redundant, deletes its sandbox page, and opens a PR. The orchestrator
   consolidates (index entries become non-linked `.done` lines with date and choice;
   `AGENTS.md` slide list and "Current pages" updated), pushes, confirms the deploy. A single
   accepted slide can be done inline by the orchestrator instead of dispatching.

Merging locally rather than with `gh pr merge` is deliberate: one push means one deploy for
the round instead of one per PR, and GitHub still marks each PR as merged once its head
commit is reachable from `main`.

## Slide-agent brief (template)

Fill every `{{...}}`. Send the whole thing; the agent has no other context.

```
You are editing one slide of a conference deck. Work only on this slide. Do not spawn
sub-agents. Report back with evidence, not claims.

REPO AND BRANCH
- You are in a git worktree of /Users/josephlittle/Github/jnuc-2026, checked out from main.
  Run `git rev-parse --show-toplevel` and use that path as the repo root for every command.
- Create and work on branch `feedback/{{SLIDE_ID}}-{{SLUG}}`.
- Read AGENTS.md first: the "House rules for every deck", the "Deck: presentations/
  migrating_an_instance" section, and the "Sandbox" section. They are binding.

THE SLIDE
- Deck: presentations/migrating_an_instance/index.html. One file holding tokens, CSS,
  markup and script. The deck must keep working opened straight off disk.
- Your slide: visible number {{SLIDE_NUMBER}}, section id `#{{SLIDE_ID}}`, title
  "{{SLIDE_TITLE}}", speaker {{SPEAKER}}. Its CSS lives in the block commented
  `/* ==== {{CSS_BLOCK_LABEL}} ==== */` (search for the id to confirm).
- Its speaker notes are the `<aside class="notes">` at the end of the section and are
  mirrored, word for word, in presentations/migrating_an_instance/presenter.json under the
  same id. If you change one, change the other.

THE FEEDBACK (verbatim from Joseph)
{{FEEDBACK_TEXT}}

WHAT TO DO
1. Apply the deterministic parts of the feedback directly to the slide:
   {{DETERMINISTIC_EDITS or "none"}}
2. For the part that has a design dimension - {{DESIGN_QUESTION}} - produce three options
   with significant, worthy differences (not three sizes of the same idea). Option A is the
   deck as it will ship from this PR (after step 1) and injects nothing; B and C are CSS
   layered on top.
3. Build the sandbox page: copy tools/sandbox-template.html to
   presentations/sandbox/{{SLIDE_ID}}-{{SLUG}}.html and replace every {{PLACEHOLDER}}.
   DECK_DIR is migrating_an_instance, DECK_TITLE is "From Clicks to Code". Each option gets
   a name, a paragraph on what it does and why someone would pick it, and its CSS. Variant
   CSS must be scoped to `#{{SLIDE_ID}}`, use only the deck's existing tokens (`--sp-*`,
   `--fs-*`, `--c-*`, `--bw-*`, `--radius*`), and never hardcode a colour, font or size. If
   an option truly needs a markup change, do it in the `load` handler on the iframe document,
   keep it minimal, and describe the equivalent deck edit in the option's paragraph.
4. Reread the slide's speaker notes after your edits. If a note points at something you
   removed or renamed, fix the note and presenter.json together.

DO NOT TOUCH
- Any other slide's markup or CSS, the `:root` token block, shared classes used by other
  slides (scope new rules by `#{{SLIDE_ID}}` instead; check with grep before styling a
  class), AGENTS.md, presentations/sandbox/index.html, presentations/sandbox/sandbox.css,
  tools/, package files, or any .key file. The orchestrator owns those.

STYLE
- British English, no emojis, no em or en dashes (plain hyphens only), no colon-glued or
  clever titles, no invented facts - anything unconfirmed gets
  `<span class="todo">TODO: ...</span>`.
- Keep `aria-label` on the section equal to the visible title.
- Anything near the bottom of the slide must clear the timeline strip.

VERIFY (all four, paste the output into your report and the PR)
a. Slide screenshot from disk:
   OUT=$(mktemp -d) && "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --window-size=1920,1080 --hide-scrollbars --virtual-time-budget=3000 --screenshot="$OUT/{{SLIDE_ID}}.png" "file://$(git rev-parse --show-toplevel)/presentations/migrating_an_instance/index.html#{{SLIDE_ID}}" 2>/dev/null; echo "$OUT/{{SLIDE_ID}}.png"
   Open the PNG with the Read tool and check for overflow, collisions and the timeline strip.
b. Sandbox screenshot over HTTP (pick a free port; kill the server in the same command):
   cd "$(git rev-parse --show-toplevel)/presentations" && OUT=$(mktemp -d) && (python3 -m http.server {{PORT}} >/dev/null 2>&1 & echo $! > "$OUT/srv.pid") && sleep 1 && "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --window-size=1400,3000 --hide-scrollbars --virtual-time-budget=8000 --screenshot="$OUT/sandbox.png" "http://localhost:{{PORT}}/sandbox/{{SLIDE_ID}}-{{SLUG}}.html" 2>/dev/null; kill "$(cat "$OUT/srv.pid")"; echo "$OUT/sandbox.png"
   Open it (crop with PIL if it is too tall to read) and confirm all three options render
   differently and none pushes content onto the timeline strip.
c. Dash lint - expect no lines before the echo:
   cd "$(git rev-parse --show-toplevel)" && grep -n -e "—" -e "–" presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json presentations/sandbox/{{SLIDE_ID}}-{{SLUG}}.html; echo "dash hits above (expect none)"
d. Scope check - the diff touches only your slide, its CSS block, its presenter.json entry
   and your new sandbox page:
   git diff --stat main && git diff main -- presentations/migrating_an_instance/index.html | grep '^@@'

DELIVER
- Commit on your branch with the global git identity, no Co-Authored-By trailer, subject
  like "Slide {{SLIDE_NUMBER}}: <what changed>", body listing the deterministic edits and
  the three options.
- git push -u origin feedback/{{SLIDE_ID}}-{{SLUG}}
- gh pr create --base main --head feedback/{{SLIDE_ID}}-{{SLUG}} --title "Slide {{SLIDE_NUMBER}}: <what changed>" --body "<the same body, plus the verify outputs and screenshot paths>"
- Your final message is the report: PR number and URL, branch name, the four verify
  outputs, the screenshot paths, and anything you could not do and why. Do not summarise
  the deck or the repo.
```

For an acceptance round, replace WHAT TO DO with:

```
WHAT TO DO
1. Joseph accepted option {{LETTER}} ("{{OPTION_NAME}}") from
   presentations/sandbox/{{SLIDE_ID}}-{{SLUG}}.html. Write it into the deck as the net
   result - one clean block of rules in the slide's CSS block, not the option layered over
   whatever was there - and remove any markup the option makes redundant.
2. git rm the sandbox page. Leave presentations/sandbox/index.html alone.
3. Reread the speaker notes and presenter.json as before.
```

and drop verify step b.

## Verifier brief (template)

```
Read-only review of PR #{{PR_NUMBER}} on /Users/josephlittle/Github/jnuc-2026 (branch
`{{BRANCH}}`). Do not edit anything. Do not spawn sub-agents.

The agent's brief was:
<<<
{{THE FULL SLIDE-AGENT BRIEF}}
>>>

Check, with commands, and report each as PASS or FAIL with the evidence:
1. `gh pr diff {{PR_NUMBER}} --name-only` lists only: presentations/migrating_an_instance/
   index.html, presentations/migrating_an_instance/presenter.json (optional), and
   presentations/sandbox/{{SLIDE_ID}}-{{SLUG}}.html (present for an options round, deleted
   for an acceptance round). Nothing else.
2. Every hunk in index.html sits inside `#{{SLIDE_ID}}`'s section or its CSS block. Hunks
   elsewhere are a FAIL - name them.
3. Every feedback point in the brief is addressed - quote the before and after for each.
4. Three options with real differences (options round): open the sandbox page and read the
   VARIANTS; every rule scoped to `#{{SLIDE_ID}}`; no hardcoded colours, fonts or sizes; no
   rule that would leak onto another slide (grep each styled class across the deck).
5. Speaker notes still make sense after the edits and match presenter.json exactly.
6. Dash lint clean; British English; no emojis; aria-label equals the visible title.
7. Render it yourself: check out the branch in a temporary worktree (`git worktree add`),
   take the disk screenshot from the brief, look at it, and remove the worktree. Report
   any overflow or timeline-strip collision.
Final message: a PASS/FAIL line per check, then the evidence. Nothing else.
```

## Orchestrator commands

Merge and consolidate (from the main checkout, on `main`, clean apart from the known
untracked files):

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git fetch origin && git checkout main && git pull --ff-only
# one per PR, in slide order
git merge --no-ff origin/feedback/<slide-id>-<slug> -m "Merge slide <n>: <what changed> (#<pr>)"
```

Consolidation commit: add the new pages to `presentations/sandbox/index.html` (date, deck,
slide, speaker, "awaiting a decision"), update the `AGENTS.md` slide list entries and the
"Current pages" line in its Sandbox section, update the Log in this file, and run the
presenter check. The main checkout should be clean before and after; if it is not, find out
why before committing.

Presenter sync check (write once to the scratchpad as `check-presenter.mjs`; must print OK):

```js
import fs from 'node:fs';
const html = fs.readFileSync('presentations/migrating_an_instance/index.html', 'utf8');
const pj = JSON.parse(fs.readFileSync('presentations/migrating_an_instance/presenter.json', 'utf8'));
const clean = (s) => s.replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/\s+/g, ' ').trim();
const deck = [...html.matchAll(/<section class="slide[^"]*" id="([^"]+)"[\s\S]*?<aside class="notes">([\s\S]*?)<\/aside>/g)]
  .map((m) => ({ id: m[1], notes: [...m[2].matchAll(/<p>([\s\S]*?)<\/p>/g)].map((p) => clean(p[1])) }));
let bad = 0;
if (deck.length !== pj.slides.length) { console.log('slide count', deck.length, 'deck vs', pj.slides.length, 'presenter.json'); bad++; }
deck.forEach((d, i) => {
  const p = pj.slides[i];
  if (!p || p.id !== d.id) { console.log('order mismatch at', i, d.id, 'vs', p && p.id); bad++; return; }
  if (JSON.stringify(p.notes) !== JSON.stringify(d.notes)) { console.log('notes differ:', d.id); bad++; }
});
const total = pj.slides.reduce((a, s) => a + s.timerSeconds, 0);
if (total !== pj.timeLimitSeconds) { console.log('timers sum to', total, 'not', pj.timeLimitSeconds); bad++; }
console.log(bad ? 'FAIL' : 'OK');
```

Run with `node <scratchpad>/check-presenter.mjs` from the repo root. It must print `OK`
before every push; it was brought to `OK` on 2026-08-27 (order and notes regenerated from
the deck, timers kept), so any failure is from the current round. The deck is the source of
truth for notes - when they differ, `presenter.json` is what gets corrected.

Whole-deck verification:

```sh
# every touched slide, plus any slide sharing a class with one (see gotchas)
OUT="$SCRATCH" && for s in s01 s-today; do "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --window-size=1920,1080 --hide-scrollbars --virtual-time-budget=3000 --screenshot="$OUT/$s.png" "file://$PWD/presentations/migrating_an_instance/index.html#$s" 2>/dev/null; done; ls "$OUT"/*.png
grep -n -e "—" -e "–" AGENTS.md presentations/sandbox/* presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json; echo "dash hits above (expect none)"
```

Push, confirm, clean up:

```sh
git push origin main
# the run can take a few seconds to appear; match on the new commit
gh run list --workflow=deploy.yml --limit 2 --json databaseId,status,conclusion,headSha -q '.[] | "\(.databaseId) \(.status) \(.conclusion) \(.headSha[0:7])"'
gh run watch --exit-status <id>
curl -s -o /dev/null -w "%{http_code}\n" https://d3ga0oyittaf77.cloudfront.net/sandbox/<slide-id>-<slug>.html
git push origin --delete feedback/<slide-id>-<slug>    # one per merged branch
git worktree prune
```

The deploy only triggers on `presentations/**`. A commit that touches only `AGENTS.md` or
`tools/` pushes fine but produces no run - do not wait for one. A missing object on the live
site returns 403, not 404.

## Sandbox

Documented in `AGENTS.md` under "Sandbox"; the short version: `presentations/sandbox/` holds
`index.html` (hand-maintained list, orchestrator-owned), `sandbox.css` (shared,
orchestrator-owned) and one page per slide change named `<slide-id>-<slug>.html`, created
from `tools/sandbox-template.html`. A page embeds the live deck slide three times in iframes
and injects one CSS variant into each on `load`; the options are therefore always the
deployed deck plus a few rules and track deck edits automatically. Injection needs HTTP -
from `file://` the iframes load but every option renders as the plain deck. Live at
https://d3ga0oyittaf77.cloudfront.net/sandbox/ , `noindex`, not linked from the landing page.

## Gotchas

- `.pipe-node` and `.pipeline-label` are shared between `#s01` and `#s-today`, and on `#s01`
  the top caption shares `.pipeline-label` with the band label. Scope by slide id and, where
  a class repeats inside the slide, by container (`#s01 .pipeline-band .pipeline-label`).
  Before styling any class, grep the deck for it and screenshot the other slides that use it.
- Removing something from a slide can orphan a speaker note that points at it. Reread the
  notes after every edit; mirror changes into `presenter.json`.
- Anything near the bottom of a slide must clear the timeline strip. Taller variants push
  content down onto it - always look at the 1920x1080 screenshot.
- Parallel agents all edit `index.html`. Different slides sit in different regions, so
  `--no-ff` merges are clean in practice; the files that do conflict are `presenter.json`
  (adjacent entries) and anything orchestrator-owned, which is why agents may not touch the
  latter. Resolve `presenter.json` conflicts by keeping both agents' entries.
- Slide agents must not rely on the live site: their iframes point at the deck relative to
  the sandbox page, so their local HTTP screenshot shows their branch's deck, and the
  deployed page shows `main`. After the merge those are the same.
- `docs/superpowers/plans/2026-08-27-clicks-to-code-feedback.md` is a superseded plan from
  before the fan-out, kept for its triage table. Do not execute it.

## If the session is lost

A new session finds the pointer in the project memory
(`~/.claude/projects/-Users-josephlittle-Github-jnuc-2026/memory/`), reads this file, and
takes over as PoC without asking Joseph to repeat anything. Reconstruct in-flight state from
the repo, not from memory of the chat:

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git fetch origin --prune
gh pr list --state open --json number,headRefName,title,updatedAt      # PRs awaiting merge
git branch -r | grep feedback/                                          # branches, merged or not
git worktree list                                                       # agents that were mid-work
ls presentations/sandbox/                                               # pages awaiting a decision
git log --oneline origin/main -10
```

Then, in order: merge and deploy any open PR that passes verification; re-dispatch any slide
listed under "In flight" below that has a worktree or branch but no PR (a killed agent - the
brief is reconstructable from the Log entry); update the Log; tell Joseph in one line what
was recovered and what is still waiting on him. Unmerged worktrees from a dead session can be
removed with `git worktree remove --force <path>` once their branch is pushed or abandoned.

## Keynote

Not until Joseph says so. When he does: `npm ci` once, `npm run build:key` on this Mac
(needs Keynote), commit the regenerated
`presentations/migrating_an_instance/from-clicks-to-code-jnuc2026.key`, push. Details in
`AGENTS.md` under "Building the downloads". The `.key` is currently behind the HTML on
purpose.

## Log

### In flight

- slide 2 (#s01) - branch feedback/s01-column-titles - dispatched 2026-08-27 - options - PR #4 merged and deployed, awaiting a decision; option C amended 2026-08-27 (divider at the same height in every panel, subgrid) - feedback: merge secrets+linters, merge peer review+shared source, drop tidy-up, title the three columns Context / Requirements / Constraints.

(Format: `slide N (#id) - branch feedback/<id>-<slug> - dispatched
<date time> - <options|acceptance X> - PR #n or "no PR yet" - feedback: <one line>`.)
Because this file is committed, an in-flight entry is written in the dispatch commit or,
if there is nothing else to commit, left in the working tree until the merge commit picks
it up - either way it is on disk for a recovering session.

### Done

- **2026-08-27, slide 4 (`#s03`) deleted.** "Migration objectives and design decisions"
  removed at Joseph's request: section, its `obj-*` CSS block (used nowhere else) and
  its `presenter.json` entry; its 60 s moved to `s17` (Questions, now 360 s) so the
  timers still sum to 1800. `AGENTS.md` slide list renumbered to 22. PR #5, merged with
  `--no-ff`.
- **Round one, 2026-08-27, slide 2 (`#s01`), run inline before the fan-out existed.**
  Label changed to "Our environment before the migration"; per-tenant annotations, the
  closing "Hold that thought" sentence and the "stale, non-active resources" clause removed;
  three layouts offered on the sandbox; option B (one three-segment chevron arrow) accepted
  and applied. Speaker note and `presenter.json` updated. Commits on `main`: `8612a67`,
  `8198a9d`, `336bc65`, `b757965`, `0f11ade`. Sandbox: no open pages, one `.done` entry.
- **2026-08-27, workflow set up for the fan-out.** This file rewritten as the process
  document, `tools/sandbox-template.html` added and `AGENTS.md` repointed (`6e1e893`).
  Then everything consolidated for a fresh session: this file and the superseded `docs/`
  plan committed, `presenter.json` regenerated to match the deck, working tree clean.
