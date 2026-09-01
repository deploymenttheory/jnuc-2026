# Deck feedback workflow

How feedback on the JNUC 2026 decks turns into deployed changes. The orchestrator (the Claude
session Joseph is talking to) reads this file at the start of every round and follows it.
Feedback itself arrives in chat, never in this file. `AGENTS.md` is the reference for the
repo and the decks; this file only covers the loop. The file is committed (the deploy's
`*.md` exclude keeps it off the site); edit it in the same commit as any change to the
process. Last revised 2026-09-01.

## Standing rules

- Feedback comes in chat, usually as a list of slides with comments. This file is the
  process, not a change list - do not append requests here.
- Every instruction gets an agent: slide feedback, a sandbox tweak, a deletion, an
  acceptance, a wording change, a process change - each one is dispatched to a single agent,
  one per instruction, and that agent returns exactly one PR. Joseph, verbatim: "EVERY
  instruction goes into an agent. That agent returns 1 PR. You JUST MERGE it and handle any
  conflicts with other agents." The orchestrator makes no repo edits of its own, not even a
  two-word fix. Its only exceptions are resolving merge conflicts between agents' PRs and
  deleting untracked files in the repo root once Joseph has said to delete them (see
  Gotchas).
- Every change gets three alternative implementations on the sandbox, with significant
  and worthy differences, unless Joseph says otherwise for that change. He picks one in
  chat, or asks for another set. Pure deletions and wording swaps with no design dimension
  can go straight into the deck, but if in doubt offer options rather than decide. "Do this
  live" means straight into the deck with no options round at all; "no options" or "no abc
  required" means the same.
- When Joseph names an option and also asks for a change to it in the same message ("rename
  X and then have Y in option D"), that whole message is the acceptance of that option -
  apply the change to the deck in the same PR. Do not treat it as a further sandbox tweak;
  that costs a round.
- Work from `main`, push to `main`, deploy on every push. Do not ask.
- Fan out: one agent per instruction, each with an explicit self-contained brief. Sonnet by
  default for mechanical rounds (wording, deletions, renames, acceptances, docs); Opus for a
  design-heavy round where earlier attempts were rejected as generic. Its PR carries the
  slide or sandbox edit, the sandbox page, the deck's `presentations/sandbox/<deck>/
  index.html` entry, any `AGENTS.md` updates the change makes necessary, and the Log entry
  in this file. The orchestrator merges the PR, resolves any conflicts with other agents'
  PRs, pushes and deploys - nothing more.
- Name each agent after what it touches, in the Agent tool's `description`: slide work
  starts with the slide, e.g. "Slide 4 (s-workspace): round three options" or "Slide 7
  (s07): accept option D"; non-slide work gets its own subject, e.g. "Sandbox: split per
  deck" or "Docs: handover update". Refer to agents by that name in chat, never by id.
- The orchestrator is Joseph's point of contact and does not do slide work itself, even when
  it looks quicker. The chat stays idle while agents work: every message from Joseph that
  contains feedback is dispatched straight away, without waiting for anything already in
  flight, and the orchestrator's reply is the dispatch confirmation. Results are reported as
  they land.
- Collaborators push straight to `main`, or open their own PR using this same workflow's
  conventions (git identity varies - ShocOne so far). A direct push to `main` is fine and
  gets rolled in on the next fetch and merge; if it leaves `presenter.json` or `AGENTS.md`
  stale, dispatch an agent to align them. A collaborator's pull request is different: it
  stays open until Joseph names it and says merge it. Joseph, verbatim: "Do not merge any
  PRs you're not told to. Only merge ones your agents make." Mention an open collaborator PR
  in chat in one line when noticed; never merge one on inference, however far along it is.
- Do not rebuild the Keynote `.key` until Joseph says so.
- Commits are authored by Joseph Little (the global git identity) with no `Co-Authored-By`
  trailer, plain human subjects, British English. No emojis, no em or en dashes anywhere.
- `AGENTS.md` is updated inside the same PR as anything that makes it stale - the agent that
  made the change does this, not the orchestrator.

## Roles

**Orchestrator** - the main session. Turns chat feedback into work items, dispatches and
briefs the agents, and otherwise makes no repo edits of its own: when a PR lands it merges
with `--no-ff`, resolves any conflicts with other agents' PRs, pushes `main`, confirms the
deploy, deletes the remote branch, prunes the worktree, and reports back in chat with the
sandbox link. Owns only the files agents may not touch: `tools/`,
`presentations/sandbox/sandbox.css` and the deck's `:root` token block. Its only other repo
edits are deleting untracked files in the repo root once Joseph has said to delete them (see
Gotchas). It merges its own agents' PRs on sight; a PR from a collaborator waits for Joseph
to name it (see Standing rules).

**Slide agent** - one per instruction (a slide, a sandbox tweak, a deletion, an acceptance, a
wording change, a process change), working in its own git worktree on its own branch, named
in the dispatch after what it touches (see Standing rules). Sonnet by default; Opus for a
design-heavy round where earlier attempts were rejected as generic. Delivers everything the
instruction needs in a single PR: the slide or sandbox edit (its section, its CSS block, its
`presenter.json` entry), the sandbox page and its deck's `presentations/sandbox/<deck>/
index.html` entry, any `AGENTS.md` updates the change makes necessary, and the Log entry in
this file. Verifies with screenshots, opens the PR, reports the PR number and evidence.
Never touches another slide's markup or CSS, the `:root` token block, `sandbox.css`,
`tools/`, package files, or any `.key` file.

**Verifier** - optional. A Sonnet agent, read-only, dispatched only when a slide agent's own
evidence is incomplete or inconsistent - speed comes first. In practice a slide agent's own
verify output has been enough since the first round. Checks the PR against its brief and the
checklist below and reports pass or fail with evidence.

## Continuous mode

Rounds are not batched. Each feedback message is its own round: parse it, dispatch one agent
per instruction it contains, reply with what was dispatched (instruction, branch name, agent
name), and stop. When a PR lands, merge, resolve any conflicts, push and deploy it on its
own - do not hold it for siblings still running unless two land within a minute of each
other. Each agent writes its own entry into the Log at the bottom of this file, inside its
PR; the orchestrator does not edit the Log. If the session is lost, recover in-flight state
from `gh pr list`, branches and worktrees (see "If the session is lost"), not from the Log.

If Joseph's message is a decision ("slide 3, option B") rather than new feedback, it is an
acceptance round for that slide - same flow with the acceptance brief. If the message names
an option and also asks for a change to it in the same breath, that is still an acceptance:
the change goes straight into the deck in the same PR, not a further sandbox round (see
Standing rules). If it is a question or a comment with no action, answer it and stay idle.

## A round, start to finish

1. **Parse.** Turn the chat feedback into one work item per instruction (usually a slide).
   Map the visible slide number to the section id using the "Current slide order" list in
   `AGENTS.md` (slide 2 is `#s01`, slide 3 is `#s02`; the ids are not the numbers). Joseph
   always means the number as the deck's counter currently reads it - ids never change but
   numbers shift whenever a slide is inserted or deleted, so re-map from `AGENTS.md` every
   round rather than trusting an earlier mapping. Several comments on one slide are one
   item. Note the speaker for each slide from the same list. Decide per item which parts are
   deterministic edits and which need three options - and whether Joseph has already said
   "do this live" or "no options", which skips the options round entirely.
2. **Dispatch.** One `Agent` call per instruction, all in one message so they run in
   parallel: `subagent_type: "general-purpose"`, `model: "sonnet"` for mechanical work or
   `"opus"` for a design-heavy round (see Standing rules), `isolation: "worktree"`, a
   `description` naming the slide or subject (see Standing rules), prompt built from the
   brief template below with every placeholder filled. Never bundle two instructions into
   one agent.
3. **Collect.** Each agent returns a PR number, branch name, and its evidence: the four
   verify outputs, the deck's sandbox index entry, the `AGENTS.md` diff, the Log entry and
   the presenter check result. If an agent returns without a PR, read its report, fix the
   brief, and re-dispatch that instruction only.
4. **Verify (optional).** Only when an agent's own evidence is incomplete or inconsistent,
   dispatch one verifier agent for that PR using the verifier brief below. Do not verify by
   default - speed comes first.
5. **Merge.** From the main checkout: fetch, then `git merge --no-ff` the branch into `main`
   (commands below). Conflicts are expected on `presentations/sandbox/<deck>/index.html`,
   `AGENTS.md`, this file's Log section and `presenter.json`, because agents edit them
   directly - resolve per the hot-spot rules in Gotchas. Make no other edits. If auto mode
   refuses the `git merge` itself, say so in one line and let Joseph toggle the mode; do not
   work around it.
6. **Push and deploy.** Push `main`. Confirm the deploy run (`presentations/**` changes only
   - a run typically completes in about a minute), `curl` the live URL for the new sandbox
   page, delete the remote branch, prune the worktree.
7. **Report in chat.** One line: the sandbox link and a few words on each of A, B and C (or,
   for an acceptance, confirmation it is live). Nothing else - Joseph will reply with
   choices.
8. **Acceptance round.** Joseph names an option per slide in chat. Same pipeline with the
   acceptance brief: the agent writes the option into the deck as the net result, removes
   markup it makes redundant, deletes its sandbox page, marks the index entry `.done`,
   updates `AGENTS.md` and the Log, and opens a PR. The orchestrator merges it like any other
   PR.

Merging locally rather than with `gh pr merge` is deliberate: it lets the orchestrator
resolve conflicts between agents' PRs before either lands, and GitHub still marks each PR as
merged once its head commit is reachable from `main`.

## Slide-agent brief (template)

Fill every `{{...}}`. Send the whole thing; the agent has no other context.

```
You are editing one slide of a conference deck. Work only on this slide. Do not spawn
sub-agents. Report back with evidence, not claims.

REPO AND BRANCH
- You are in a git worktree of /Users/josephlittle/Github/jnuc-2026, checked out from main.
  Run `git rev-parse --show-toplevel` and use that path as the repo root for every command.
- Start with `git fetch origin && git merge --ff-only origin/main` before anything else. If
  `main` moves again while you work, merge `origin/main` into your branch before pushing and
  resolve locally what you can; leave anything you cannot for the orchestrator.
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
   presentations/sandbox/{{DECK_DIR}}/{{SLIDE_ID}}-{{SLUG}}.html and replace every
   {{PLACEHOLDER}}. DECK_DIR is migrating_an_instance, DECK_TITLE is "From Clicks to Code".
   Each option gets
   a name, a paragraph on what it does and why someone would pick it, and its CSS. Variant
   CSS must be scoped to `#{{SLIDE_ID}}`, use only the deck's existing tokens (`--sp-*`,
   `--fs-*`, `--c-*`, `--bw-*`, `--radius*`), and never hardcode a colour, font or size. If
   an option truly needs a markup change, do it in the `load` handler on the iframe document,
   keep it minimal, and describe the equivalent deck edit in the option's paragraph.
4. Add this page to presentations/sandbox/{{DECK_DIR}}/index.html, in the same hand-written
   style as the existing entries: date, deck, slide, speaker, "awaiting a decision". Match
   the existing entries' format exactly - do not restructure the file.
5. Update AGENTS.md: the slide list entry for {{SLIDE_NUMBER}} if its title or content
   summary changed, the "Current pages" line in the Sandbox section (add your page), and
   anything else your change makes stale (timers, slide count, other cross-references).
6. Reread the slide's speaker notes after your edits. If a note points at something you
   removed or renamed, fix the note and presenter.json together.
7. Run the presenter sync check and paste `OK` into your report (write the script to your
   own worktree's temp dir, not the orchestrator's scratchpad):
   OUT=$(mktemp -d) && cat > "$OUT/check-presenter.mjs" <<'EOF'
   import fs from 'node:fs';
   const html = fs.readFileSync('presentations/migrating_an_instance/index.html', 'utf8');
   const pj = JSON.parse(fs.readFileSync('presentations/migrating_an_instance/presenter.json', 'utf8'));
   const clean = (s) => s.replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/\s+/g, ' ').trim();
   const deck = [...html.matchAll(/<section class="slide[^"]*" id="([^"]+)"[\s\S]*?<aside class="notes">([\s\S]*?)<\/aside>/g)]
     .map((m) => {
       const h1 = m[0].match(/<h1 class="slide-title">([\s\S]*?)<\/h1>/);
       return { id: m[1], notes: [...m[2].matchAll(/<p>([\s\S]*?)<\/p>/g)].map((p) => clean(p[1])), h1: h1 ? h1[1] : null };
     });
   let bad = 0;
   if (deck.length !== pj.slides.length) { console.log('slide count', deck.length, 'deck vs', pj.slides.length, 'presenter.json'); bad++; }
   deck.forEach((d, i) => {
     const p = pj.slides[i];
     if (!p || p.id !== d.id) { console.log('order mismatch at', i, d.id, 'vs', p && p.id); bad++; return; }
     if (JSON.stringify(p.notes) !== JSON.stringify(d.notes)) { console.log('notes differ:', d.id); bad++; }
     if (d.h1 !== null && clean(d.h1) !== p.title) { console.log('title differs:', d.id); bad++; }
   });
   const total = pj.slides.reduce((a, s) => a + s.timerSeconds, 0);
   if (total !== pj.timeLimitSeconds) { console.log('timers sum to', total, 'not', pj.timeLimitSeconds); bad++; }
   console.log(bad ? 'FAIL' : 'OK');
   EOF
   node "$OUT/check-presenter.mjs"
   It must print OK before you commit. The deck is the source of truth for notes - when they
   differ, presenter.json is what gets corrected.
8. Add a bullet to the top of the Log's `### Done` list at the bottom of
   feedback-workflow.md, in the same style as the existing entries, describing what you did.
   For an options round, name the sandbox link and note it awaits a decision. Include your PR
   number once you have one - if you write this before opening the PR, push a short follow-up
   commit to add the number once `gh pr create` returns it.

DO NOT TOUCH
- Any other slide's markup or CSS, the `:root` token block, shared classes used by other
  slides (scope new rules by `#{{SLIDE_ID}}` instead; check with grep before styling a
  class), presentations/sandbox/sandbox.css, tools/, package files, or any .key file. The
  orchestrator owns those.

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
   cd "$(git rev-parse --show-toplevel)/presentations" && OUT=$(mktemp -d) && (python3 -m http.server {{PORT}} >/dev/null 2>&1 & echo $! > "$OUT/srv.pid") && sleep 1 && "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --window-size=1400,3000 --hide-scrollbars --virtual-time-budget=8000 --screenshot="$OUT/sandbox.png" "http://localhost:{{PORT}}/sandbox/{{DECK_DIR}}/{{SLIDE_ID}}-{{SLUG}}.html" 2>/dev/null; kill "$(cat "$OUT/srv.pid")"; echo "$OUT/sandbox.png"
   Open it (crop with PIL if it is too tall to read) and confirm all three options render
   differently and none pushes content onto the timeline strip.
c. Dash lint - expect no lines before the echo:
   cd "$(git rev-parse --show-toplevel)" && grep -n -e "—" -e "–" presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json presentations/sandbox/{{DECK_DIR}}/{{SLIDE_ID}}-{{SLUG}}.html; echo "dash hits above (expect none)"
d. Scope check - the diff touches only your slide, its CSS block, its presenter.json entry
   and your new sandbox page:
   git diff --stat main && git diff main -- presentations/migrating_an_instance/index.html | grep '^@@'

DELIVER
- Commit on your branch with the global git identity, no Co-Authored-By trailer, subject
  like "Slide {{SLIDE_NUMBER}}: <what changed>", body listing the deterministic edits and
  the three options.
- git push -u origin feedback/{{SLIDE_ID}}-{{SLUG}}
- gh pr create --base main --head feedback/{{SLIDE_ID}}-{{SLUG}} --title "Slide {{SLIDE_NUMBER}}: <what changed>" --body "<the same body, plus the verify outputs and screenshot paths>"
- If your Log entry (step 8) did not yet have a PR number, add it now, commit and push again
  - the same PR picks up the new commit.
- Your final message is the report: PR number and URL, branch name, the four verify
  outputs, the screenshot paths, the presenter check result, and anything you could not do
  and why. Do not summarise the deck or the repo.
```

For an acceptance round, replace WHAT TO DO with:

```
WHAT TO DO
1. Joseph accepted option {{LETTER}} ("{{OPTION_NAME}}") from
   presentations/sandbox/{{DECK_DIR}}/{{SLIDE_ID}}-{{SLUG}}.html. Write it into the deck as
   the net result - one clean block of rules in the slide's CSS block, not the option
   layered over whatever was there - and remove any markup the option makes redundant.
2. git rm the sandbox page. In presentations/sandbox/{{DECK_DIR}}/index.html, turn its entry
   into a non-linked `.done` line with the date and the option chosen, in the same style as
   the existing decided entries.
3. Update AGENTS.md: the slide list entry if the title or content summary changed, and the
   "Current pages" and "Decided" lines in the Sandbox section to match.
4. Reread the speaker notes and presenter.json as before.
5. Run the presenter sync check (step 7 of the options brief) and paste OK into your report.
6. Add a Done bullet to the Log (step 8 of the options brief); if this slide had an
   "In flight" line, remove it as part of the same edit - this PR is what closes it out.
```

and drop verify step b.

## Verifier brief (template)

Optional - dispatch only when a slide agent's own evidence is incomplete or inconsistent.

```
Read-only review of PR #{{PR_NUMBER}} on /Users/josephlittle/Github/jnuc-2026 (branch
`{{BRANCH}}`). Do not edit anything. Do not spawn sub-agents.

The agent's brief was:
<<<
{{THE FULL SLIDE-AGENT BRIEF}}
>>>

Check, with commands, and report each as PASS or FAIL with the evidence:
1. `gh pr diff {{PR_NUMBER}} --name-only` lists only: presentations/migrating_an_instance/
   index.html, presentations/migrating_an_instance/presenter.json (optional),
   presentations/sandbox/{{DECK_DIR}}/{{SLIDE_ID}}-{{SLUG}}.html (present for an options
   round, deleted for an acceptance round), presentations/sandbox/{{DECK_DIR}}/index.html,
   AGENTS.md (if the change made it stale) and feedback-workflow.md (the Log entry). Nothing
   else.
2. Every hunk in presentations/migrating_an_instance/index.html sits inside
   `#{{SLIDE_ID}}`'s section or its CSS block. Hunks elsewhere are a FAIL - name them.
3. Every feedback point in the brief is addressed - quote the before and after for each.
4. Three options with real differences (options round): open the sandbox page and read the
   VARIANTS; every rule scoped to `#{{SLIDE_ID}}`; no hardcoded colours, fonts or sizes; no
   rule that would leak onto another slide (grep each styled class across the deck).
5. Speaker notes still make sense after the edits and match presenter.json exactly.
6. Dash lint clean; British English; no emojis; aria-label equals the visible title.
7. The sandbox index entry (or its `.done` line for an acceptance) matches the format of the
   existing entries; any AGENTS.md updates the brief called for are correct; the Log entry
   matches what happened; the presenter check output the agent pasted says OK.
8. Render it yourself: check out the branch in a temporary worktree (`git worktree add`),
   take the disk screenshot from the brief, look at it, and remove the worktree. Report
   any overflow or timeline-strip collision.
Final message: a PASS/FAIL line per check, then the evidence. Nothing else.
```

## Orchestrator commands

Merge (from the main checkout, on `main`, clean apart from the known untracked files):

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git fetch origin && git checkout main && git pull --ff-only
git merge --no-ff origin/feedback/<slide-id>-<slug> -m "Merge slide <n>: <what changed> (#<pr>)"
```

Conflicts are expected on `presentations/sandbox/<deck>/index.html`, `AGENTS.md`, this
file's Log section and `presenter.json` when two agents' PRs both touch them, because agents
now edit those directly. Resolve per the hot-spot rules in Gotchas - never drop either side.
The main checkout should be clean before and after; if it is not, find out why before
pushing. Only merge a PR opened by one of your own agents; a PR from another author is a
collaborator's and stays open until Joseph names it (see Standing rules).

Push, confirm, clean up:

```sh
git push origin main
# the run can take a few seconds to appear; match on the new commit. Today's runs completed
# in about 60-90 seconds once picked up.
gh run list --workflow=deploy.yml --limit 2 --json databaseId,status,conclusion,headSha -q '.[] | "\(.databaseId) \(.status) \(.conclusion) \(.headSha[0:7])"'
gh run watch --exit-status <id>
curl -s -o /dev/null -w "%{http_code}\n" https://d3ga0oyittaf77.cloudfront.net/sandbox/<deck>/<slide-id>-<slug>.html
git push origin --delete feedback/<slide-id>-<slug>    # one per merged branch
git worktree prune
```

The deploy only triggers on `presentations/**`. A commit that touches only `AGENTS.md`,
`feedback-workflow.md` or `tools/` pushes fine but produces no run - do not wait for one. A
missing object on the live site returns 403, not 404.

Presenter-check evidence: keep your own copy of the check script read-only
(`chmod 444`) in the scratchpad and run it from the repo root when double-checking a PR
before push. An `ENOENT` from it means the script went missing (see Gotchas), not that the
deck is broken.

## Sandbox

Documented in `AGENTS.md` under "Sandbox"; the short version: `presentations/sandbox/` holds
one sandbox per deck. `index.html` at the top is a minimal chooser (orchestrator-owned,
static, rarely changes) linking to `migrating_an_instance/` and `training_a_team/`;
`sandbox.css` (shared, orchestrator-owned) also sits at the top. Each deck subdirectory has
its own `index.html` (hand-maintained list, edited by whichever agent's PR adds or resolves
a page) and one page per slide change named `<slide-id>-<slug>.html`, created from
`tools/sandbox-template.html`. A page embeds the live deck slide three times in iframes
(two levels up from the page to `presentations/`, then into the deck) and injects one CSS
variant into each on `load`; the options are therefore always the deployed deck plus a few
rules and track deck edits automatically. Injection needs HTTP - from `file://` the iframes
load but every option renders as the plain deck. Live at
https://d3ga0oyittaf77.cloudfront.net/sandbox/ , `noindex`, linked from a Sandbox button on
each deck card on the landing page.

For a new slide or a full redesign, CSS layered onto nothing rarely works. Ship every option
as a real markup wrapper inside the slide's section instead (`.<id>-opt-a`, `.<id>-opt-b`,
and so on), with one deck CSS rule hiding everything but `-opt-a` by default (`#s-workspace`
carries the pattern). The sandbox page's injected CSS then only needs to flip which wrapper
is visible per option - `tools/sandbox-template.html` and the injection mechanism do not
change. Accepting an option means deleting the other wrappers and their CSS as one clean
block, not layering a further rule on top. Four-option pages are fine: add a fourth
`<section class="option">`, a fourth jump link and a fourth `VARIANTS` entry, matching the
shape of A to C.

Sandbox pages, wherever they sit after the per-deck split (2026-08-27), need: iframe src
`../../<deck>/index.html#<slide-id>` (two levels up to `presentations/`, then into the deck),
stylesheet `../sandbox.css`, and crumb
`<a href="../../">JNUC 2026</a> / <a href="./">Sandbox</a>`.

## Gotchas

- `.pipe-node` and `.pipeline-label` are shared between `#s01` and `#s-today`, and on `#s01`
  the top caption shares `.pipeline-label` with the band label. Scope by slide id and, where
  a class repeats inside the slide, by container (`#s01 .pipeline-band .pipeline-label`).
  Before styling any class, grep the deck for it and screenshot the other slides that use it.
- Removing something from a slide can orphan a speaker note that points at it. Reread the
  notes after every edit; mirror changes into `presenter.json`.
- Anything near the bottom of a slide must clear the timeline strip. Taller variants push
  content down onto it - always look at the 1920x1080 screenshot.
- Parallel agents all edit `presentations/migrating_an_instance/index.html`. Different
  slides sit in different regions, so `--no-ff` merges are clean there in practice. Agents
  also edit `presentations/sandbox/<deck>/index.html`, `AGENTS.md`, this file's Log section
  and `presenter.json` directly, so conflicts on those are expected whenever two agents' PRs
  land close together. Resolution rules per file, never dropping either side:
  - This file's Log: keep both sides' bullets under `### Done`, newest first. Under
    `### In flight`, keep whichever line reflects the later state of that slide (a line
    saying a PR is still pending loses to one showing it merged) and drop the other.
  - `presentations/sandbox/<deck>/index.html`: keep all entries, newest first.
  - `AGENTS.md`'s "Current pages"/"Decided" line in the Sandbox section: the union of both
    sides' pages.
  - `AGENTS.md`'s "Current slide order" list: take the renumbered side (the one reflecting
    an insert or delete), and carry across any title change the other side made.
  - `presenter.json`: adjacent entries from both sides - keep both.
- Slide agents must not rely on the live site: their iframes point at the deck relative to
  the sandbox page, so their local HTTP screenshot shows their branch's deck, and the
  deployed page shows `main`. After the merge those are the same.
- The presenter-check script (in the slide-agent brief) must be written to the agent's own
  worktree's temp dir, never anywhere near the orchestrator's copy. An agent overwrote the
  orchestrator's scratchpad copy twice in one day, once with an absolute path back into its
  own worktree, which made the orchestrator's pre-push check fail with `ENOENT` after that
  worktree was removed - the script, not the deck, had broken. The orchestrator keeps its
  own copy read-only (`chmod 444`) and runs it from the repo root. The check compares notes,
  order, timers and titles (`<h1>` vs `presenter.json` title, since PR #9).
- If auto mode's permission classifier refuses a `git merge` outright, say so in chat in one
  line and let Joseph toggle the mode - do not try to work around it.
- Untracked files Joseph drops in the repo root (photos, other assets) are read by an agent
  from the main checkout's absolute path - never committed from there - and deleted only by
  the orchestrator, only once Joseph has said to.
- `docs/superpowers/plans/2026-08-27-clicks-to-code-feedback.md` is a superseded plan from
  before the fan-out, kept for its triage table. Do not execute it.
- When Joseph's machine sleeps, background agents die mid-task. On resume, check each
  agent's worktree for commits and untracked files before deciding whether to resume it
  (`SendMessage` to the agent) or re-dispatch it fresh - a worktree with nothing committed
  is safe to re-dispatch, one with work in progress is worth resuming instead.
- An in-flight agent can take an amended brief by message before it opens its PR, which
  avoids a second round trip through the sandbox. Used for slide 16's pixel art (upgraded
  to hi-res while the agent was still working) and for By the numbers' date line (corrected
  before the PR went up) - both landed in the same PR as the original brief, not a
  follow-up one.

## If the session is lost

A new session finds the pointer in the project memory
(`~/.claude/projects/-Users-josephlittle-Github-jnuc-2026/memory/`), reads this file, and
takes over as PoC without asking Joseph to repeat anything. Reconstruct in-flight state from
the repo, not from memory of the chat:

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git fetch origin --prune
gh pr list --state open --json number,headRefName,title,author,updatedAt  # PRs awaiting merge
git branch -r | grep feedback/                                          # branches, merged or not
git worktree list                                                       # agents that were mid-work
ls presentations/sandbox/*/*.html                                       # pages awaiting a decision
git log --oneline origin/main -10
git config user.email                                                   # confirm it matches recent commits on main
```

Then, in order: for each open PR, check its author against the git identity on `main`
(`thejoeker12` today) - merge the ones that match (dispatch a verifier first only if its own
evidence looks incomplete), resolving conflicts per Gotchas, then push and deploy each.
Leave any PR from another author alone - it is a collaborator's - and tell Joseph about it
in one line rather than merging it; only merge one when he names it. Re-dispatch any branch
or worktree that has no PR yet (a killed agent - the brief is reconstructable from the
branch name and whatever is already committed on it); tell Joseph in one line what was
recovered and what is still waiting on him. Unmerged worktrees from a dead session can be
removed with `git worktree remove --force <path>` once their branch is pushed or abandoned.

## Keynote

Not until Joseph says so. When he does: `npm ci` once, `npm run build:key` on this Mac
(needs Keynote), commit the regenerated
`presentations/migrating_an_instance/from-clicks-to-code-jnuc2026.key`, push. Details in
`AGENTS.md` under "Building the downloads". The `.key` is currently behind the HTML on
purpose.

## Log

### State at handover (2026-09-01)

A new session taking over should read this before anything else. Per-slide status for
`presentations/migrating_an_instance`, everything touched since the 2026-08-28 handover
(PR #51), cross-checked against the `### Done` bullets below, `git log --oneline
65180db..origin/main`, AGENTS.md's "Current slide order" (still 22 slides) and Sandbox
section, `ls presentations/sandbox/migrating_an_instance/` and `gh pr list --state open`.

Thursday and Friday's orchestrated rounds:

- Slide 16 (`#s-staging`) - wording made plainer and steps-first, three layouts offered on
  the sandbox (PR #40); pixel-art icons drawn for the three rebuild steps (PR #49); option
  B, a numbered run down the left on a rail, accepted (PR #52); the icons redrawn at
  1024px, Pixelforge project `b4001dd6` kept and its spec amended in place, and
  `image-rendering` on `.s-staging-art` changed from `pixelated` to `auto` because the
  smooth downscale is the only one that holds at the 168px display width (PR #58). Settled.
- Slide 9 (`#s-sentinel`) - round one of visual treatments offered (PR #54), rejected
  outright with none of the wrappers kept; round two, three fresh treatments deliberately
  unlike a wall, a staircase or a timeline axis, offered on the sandbox (PR #56). Open -
  see What is pending.
- Slide 12 (`#s11`) - four points on the right with three visual treatments offered
  (PR #53); round one rejected, plain separated-bullet treatments offered instead
  (PR #55); option D, the four points numbered 1 to 4 in mono in an accent gutter,
  accepted (PR #57) - Copilot CLI is no longer named on this slide as a result of the
  point cut in PR #53.
- Slide 15 (`#s14`) - three terminal treatments offered so the `terraform plan` block reads
  as a real terminal (PR #38); option B, the block as a real window with chrome, traffic
  lights and a blinking cursor, accepted (PR #39); gate 2 reworded to say state is stored
  in a remote backend and to say "AI" rather than naming Copilot CLI (PR #42). Settled.
- Slide 17 (`#s-pivot`) - the "It got out of hand" pivot statement removed, three display
  options offered (PR #41); the round closed with no option chosen, live slide kept
  (PR #44). Settled at the time - see the weekend's work below for what replaced it.
- Slide 19 (`#s-today`) - deleted, its 60 seconds moved to Questions, deck renumbered to
  22 slides (PR #43). Settled.
- By the numbers (`#s16b`) - figures refreshed and three visualisations offered on the
  sandbox (PR #46); option C, 900 PRs merged as a hero number with the other four figures
  in a quiet row, accepted, and the date line changed to "Jan 2026 -> Sept 2026" (PR #48).
  Settled on the slide itself - see What is pending for the notes mismatch and the
  1,902-commits figure.
- Non-slide: `docs/timeline-adherence.md` added, one row per slide with a blank "Month
  (fill in)" column for Joseph (PR #45); the sandbox index entries fix, splitting three
  merged `<li>`s back into one each (PR #50); the 2026-08-28 handover doc itself (PR #51).

The weekend's collaborator work, merged by ShocOne (collaborators may push or self-merge
their own PRs under the standing rules; only the orchestrator must not merge a
collaborator's PR unnamed):

- PR #47 (macdeacon99) - gate 4 on the validation slide reworded so UI write access is
  revoked before the import rather than after validation, matching the wave-workflow
  slide's own sequence; Gordon's speaker photo re-cropped to his face.
- PR #59 (ShocOne) - slides 17 and 18 rewritten as one arc around DRY. `#s-pivot` retitled
  "One codebase for every instance": the DRY objective in an accent band over a real
  `jamfpro_static_computer_group` block, its `assigned_computer_ids` the only amber thing
  on the slide. `#s15b` retitled "Getting as close to DRY as we can": six techniques in a
  three by two grid, each with real syntax, under a caution that CLI workspaces share a
  backend; the module tree moved into the reader-mode popover.
- PR #60 (ShocOne) - follow-up to #59: slide 18's Terraform Stacks card replaced with
  configuration as data (per-instance YAML read with `yamldecode`), because Stacks needs
  HCP Terraform or Terraform Enterprise 2.0 on a resource-under-management plan and is
  unreachable by anyone running Terraform CLI.

What is pending, verified today:

- One sandbox page awaiting a decision: `s-sentinel-round2` (slide 9, options B to D;
  PR #56).
- By the numbers' first speaker note still says April 2025 to May 2026 while the slide's
  date line reads Jan 2026 to Sept 2026 (PR #48) - Joseph to reconcile.
- The `1,902` commits figure was not in Joseph's updated stats and is probably stale.
- `docs/timeline-adherence.md`'s "Month (fill in)" column is still empty and its H1 still
  carries a colon ("Timeline adherence: Migrating an instance").
- The timeline doc's table no longer matches the deck after the weekend's slide 17/18
  retitles: row 17 still reads "Growing pains" (now "One codebase for every instance") and
  row 18 still reads "The module structure" (now "Getting as close to DRY as we can").
  Flagged here, not edited in the doc - the doc's `data-when` review is Joseph's to do.
- No open PRs (`gh pr list --state open` returns none). Keynote rebuild not requested.
  Slide 4's speaker still marked TBC (Dafydd).

Commit range: `65180db` (the 2026-08-27 handover doc, PR #28) to `e2cdebb` (current
`origin/main` tip, PR #60's merge). PR numbers #38 to #60, of which #47, #59 and #60 are
collaborator PRs. This docs update is its own PR, #61.

### State at handover (2026-08-28, superseded)

A new session taking over should read this before anything else. Per-slide status for
`presentations/migrating_an_instance`, everything touched since PR #28, cross-checked
against the Done bullets below, `git log --oneline 65180db..origin/main`, AGENTS.md's
"Current slide order" (22 slides) and Sandbox section, `ls presentations/sandbox/
migrating_an_instance/` and `gh pr list --state open`:

- Slide 6 (`#s05`) - a collaborator's PR #26 named the three migration paths and drew each
  as a flow; the control note at the foot of the slide folded into path 03, with four
  layout options offered on the sandbox (PR #33); option D, each path in its own bordered
  panel with the diagram centred inside, applied (PR #36). Settled.
- Slide 10 (`#s10`) - the resource-sequencing diagram's text bumped, three size options
  offered on the sandbox (PR #29); option C, everything bigger and the diagram reflowed,
  applied (PR #34). Settled.
- Slide 11 (`#s08`) - three layouts offered for the empty half of the migration wave
  workflow slide (PR #31); option C, seven full-width bands stepping down the slide,
  applied (PR #35). Settled.
- Slide 14 (`#s13`) - cut back to the policies exception, the dock-items card removed, four
  layouts offered (PR #32); option D, the exception and its reason in large type with
  wording made more human, applied (PR #37). Settled.
- Slide 15 (`#s14`) - three terminal-excerpt treatments offered so the `terraform plan`
  block reads as a real terminal (PR #38); option B, the block as a real window with
  chrome, traffic lights and a blinking cursor, applied (PR #39); gate 2 reworded to say
  state is stored in a remote backend and to drop the Copilot CLI namedrop in favour of
  "AI" (PR #42). Settled on this slide - `#s11` (slide 12) still names Copilot CLI for the
  same underlying fact and was left alone as another slide (see What is pending).
- Slide 16 (`#s-staging`) - wording made plainer and steps-first, three layouts offered on
  the sandbox (PR #40); three 384px pixel-art icons drawn with Pixelforge (project id
  `b4001dd6`, one per rebuild step - wipe, apply, iterate) and embedded in the slide as
  base64 data URIs, with the open sandbox page `s-staging-steps-first` adjusted so the
  icons appear in all four renders (PR #49). Open - the sandbox page awaits a decision
  between options B, C and D; option A, already live, carries the pixel art.
- Slide 17 (`#s-pivot`) - the "It got out of hand" pivot line cut and its TODO chip moved
  onto the code block, three display options offered (PR #41); sandbox closed with no
  option chosen, live slide kept (PR #44). Settled.
- Slide 19 (`#s-today`), deleted - "The estate today" removed, its 60 seconds moved to
  Questions so the timers still sum to 1800, deck renumbered to 22 slides (PR #43).
  Settled.
- By the numbers (`#s16b`, now slide 19) - figures refreshed (35-40 contributors, 900 PRs
  merged, 134 HCL files, 19,000+ lines of code) with three visualisations offered on the
  sandbox (PR #46); option C, 900 PRs merged as a hero number with the other four figures
  in a quiet row, applied, and the date line changed to "Jan 2026 -> Sept 2026" (PR #48).
  Settled on the slide itself - see What is pending for the notes mismatch and the
  1,902-commits figure.
- Non-slide: a collaborator's changes to the training deck and this deck merged together
  (PR #30); `docs/timeline-adherence.md` added, one row per slide with a blank "Month (fill
  in)" column for Joseph (PR #45); the pixel-art source directory
  `presentations/migrating_an_instance/art/` added alongside slide 16's icons, holding the
  Pixelforge spec `s-staging-steps.md` and the three exported PNGs (PR #49, above).

What is pending:

- One sandbox page awaiting a decision: slide 16 `s-staging-steps-first` (options B to D;
  option A is live with the pixel art).
- Collaborator PR #47 (macdeacon99, "Revoke UI write access before the import, not after
  validation", head `main` of their fork) is open - mention it, do not merge it unless
  Joseph names it.
- Two things flagged for Joseph and not actioned: slide 12 `#s11` still names Copilot CLI
  (gate 2 on slide 15 was reworded to say "AI" and "remote backend", PR #42, but the agent
  left `#s11` alone as another slide); and By the numbers' first speaker note still says
  April 2025 to May 2026 while the slide's date line now reads Jan 2026 to Sept 2026 (PR
  #48).
- `docs/timeline-adherence.md` (PR #45) has its "Month (fill in)" column empty, waiting on
  Joseph; its H1 uses a colon ("Timeline adherence: Migrating an instance"), which breaks
  the no-colon-titles rule - noted, not fixed.
- The `1,902` commits figure on By the numbers was not in Joseph's updated stats and is
  probably stale.
- Keynote rebuild not requested; slide 4's speaker still marked TBC (Dafydd).

Commit range for the day: `65180db` (yesterday's handover doc, PR #28) to `1c7023d`
(current `origin/main` tip, PR #49's merge). PR numbers #29 to #49, plus #26, #30 and #47
as collaborator PRs (#27 and #28 were yesterday's). This docs update is its own PR, #51.

### State at handover (2026-08-27, superseded)

A new session taking over mid-day should read this before anything else. Per-slide status
for `presentations/migrating_an_instance`, everything touched today, cross-checked against
the Done bullets below and the git log:

- Slide 2 (`#s01`) - the nine constraint cards consolidated into six, three titled columns
  (Context, Requirements, Constraints) (PR #4); option C, bordered column panels with
  aligned dividers, applied (PR #8). Settled.
- Slide 4 (`#s03`) - "Migration objectives and design decisions" deleted; its 60 seconds
  moved to Questions (PR #5). Settled.
- Slide 4 (`#s-workspace`) - new slide, inserted after slide 3 (the old slide 4, `#s04`,
  moved to slide 5). Three rounds of options: round one (PR #10) and round two (PR #14,
  plus a fourth option added by PR #15) were both rejected as generic. Round three's option
  A was the collaborator's independent rebuild of the slide (PR #21, merged on Joseph's
  "Merge 21"); B to D were a further redesigned set (PR #22); B to D were rejected and A
  was kept as the live slide, its leftover wrapper markup and CSS removed along with the
  round-three sandbox page (PR #27). Settled - nothing pending, no sandbox page open.
  Speaker still marked TBC (Dafydd).
- Slide 5 (`#s04`) - retitled by a collaborator's direct push (`7e1a99b`), not mirrored into
  `presenter.json` at the time; its closing "two more ideas" line removed (PR #7); its
  title, and two other slides' titles (`#s-sentinel`, `#s-today`), aligned across the deck,
  `presenter.json` and `AGENTS.md`, and the presenter check extended to compare titles as
  well as notes (PR #9). Settled.
- Slide 6 (`#s05`) - the left option card's wording rewritten to explain the striped
  approach; the chosen card's closing line removed (PR #11); the option-card blurb's font
  size set explicitly so it clears the timeline strip (PR #12). A collaborator's PR #26
  ("Slide 6: name the three migration paths and draw each as a flow", branch
  `feedback/s05-migration-paths`) is open and unmerged - do not merge it without Joseph
  naming it.
- Slide 7 (`#s07`) - renamed Prerequisites (PR #23); split into two portions, Instance prep
  and Migration prep, sandbox option D applied (PR #24, after an earlier options round PR
  #13 and a fourth option PR #17); the runner line of sight row reworded to Joseph's live
  wording, an "Org-wide policies" row added, and the last two TODO chips on the slide
  removed (PR #25). Settled.
- Slide 8 (`#s-singletons`) - the empty `import {}` block filled with the documented
  singleton id and its provenance (PR #18). Settled.
- Non-slide: Joseph's and Gordon's speaker photos embedded in `_shared/speakers.js` for both
  decks (PR #20); a Sandbox button added to the landing page (PR #16), then split into one
  button per deck card when the sandbox itself split one-per-deck (PR #19);
  `presenter.json` titles aligned and the presenter check extended (PR #9, above); the
  process itself rewritten to one agent, one PR per instruction (PR #6).

What is pending:

- Nothing on slide 4 - PR #27 is merged and deployed.
- No sandbox pages awaiting a decision (`presentations/sandbox/migrating_an_instance/`
  holds only its `index.html`, all entries `.done`; `training_a_team/` has none yet).
- Collaborator PR #26 (ShocOne, branch `feedback/s05-migration-paths`, slide 6) is open -
  mention it, do not merge it unless Joseph names it.
- More collaborator PRs are coming on `training_a_team` - do not merge those either without
  Joseph naming one.
- Keynote rebuild not requested - both `.key` files stay behind the HTML on purpose.
- Slide 4's speaker is still marked TBC (Dafydd).

Commit range for the day: `1a26530` (repo consolidated) to `fa62824` (current `origin/main`
tip, PR #27's merge); PR numbers 4 to 27. This docs update is a separate PR, opened after
that range: PR #28.

### In flight

Nothing.

(Format: `slide N (#id) - branch feedback/<id>-<slug> - dispatched
<date time> - <options|acceptance X> - PR #n or "no PR yet" - feedback: <one line>`.)
Because this file is committed, an in-flight entry is written in the dispatch commit or,
if there is nothing else to commit, left in the working tree until the merge commit picks
it up - either way it is on disk for a recovering session.

### Done

- **2026-09-01, slide 8 (`#s-singletons`) subtitle added.** A `<p class="slide-sub">` under
  the title, matching the deck's existing subtitle pattern (already used on s-workspace,
  s04, s05 and s-pivot): "Settings panes went into state first, imported by default and
  applied only as a fallback." Drawn from the slide's own body copy and notes, no new facts
  added. Speaker notes and presenter.json untouched - the subtitle changes nothing they
  say. AGENTS.md's slide 8 summary checked and still accurate, left unchanged. Screenshot
  confirms no overflow and clearance above the timeline strip. Presenter check fails only
  on a pre-existing `s01` title mismatch (deck says "Landscape prior to the migration",
  presenter.json still says "Context, requirements, constraints") introduced by an earlier
  merge unrelated to this slide - left for the orchestrator. PR TBC.
- **2026-09-01, feedback-workflow.md updated for the handover.** A new "State at handover
  (2026-09-01)" section added covering PRs #38 to #60 (collaborator PRs #47, #59 and #60
  included) since the 2026-08-28 handover: the Thursday/Friday orchestrated rounds on
  slides 16, 9, 12, 15, 17, 19 and By the numbers, the weekend's collaborator work on gate
  4 and the slide 17/18 DRY rewrite plus its Terraform Stacks correction, and what remains
  pending (the `s-sentinel-round2` sandbox decision, the By the numbers notes mismatch, the
  stale `1,902` commits figure, and the timeline-adherence doc's now-stale rows for slides
  17 and 18). The 2026-08-28 section retitled "superseded" and kept unchanged below it.
  `AGENTS.md` checked against the weekend's changes and needed no changes - ShocOne's PRs
  had already brought the slide list and TODO table current. "Last revised" bumped to
  2026-09-01. PR #61.
- **2026-08-28, slides 17 (`#s-pivot`) and 18 (`#s15b`) rewritten as one arc.** Dafydd
  reframed the pair around DRY: the objective was one Terraform codebase applied to every
  Jamf Pro instance, Jamf Pro does not allow it because the same resource type carries
  instance-unique configuration, so the second slide is the techniques for getting as close
  to DRY as the product allows. Six proposals were put on an artifact and Dafydd took slide
  17 from option 1 and slide 18 from option 4. Slide 17 is now the DRY statement in an accent
  band over a real `jamfpro_static_computer_group` block, its `assigned_computer_ids` the only
  amber thing on the slide, beside a shared / unique-to-one-instance breakdown. Slide 18 is
  six techniques in a three by two grid, each carrying real syntax, child modules marked as
  what the estate runs, over a caution that CLI workspaces share a backend. All wording on
  both slides is new; "thin roots", "blast radius" and "divergence is visible, not hidden"
  are gone, Jamf objects use current Jamf names (Volume Purchasing content token, push
  certificate) and Terraform terms are HashiCorp's. The FQDN-conditional TODO chip is retired
  and replaced by one for the rest of the instance-unique list. The module tree moved into
  s15b's reader-mode popover. `presenter.json` mirrored, check prints OK. Collaborator PR,
  raised by ShocOne, not to be merged until Joseph names it.


- **2026-08-28, training_a_team slide 3 (`#3`) confirmed goals TODOs.** The user, on the
  three `.todo` chips on the Goals slide: the TRAINED bar definition and the non-goals
  strip were both confirmed correct as written, so their chips were removed with no content
  change. The "what success looked like" behaviours chip was close but not identical -
  reworded to the confirmed facts: the Mac engineering team became self-sufficient
  committing and reviewing pull requests without assistance, was making architectural
  decisions, and was managing resources in code exclusively. That section's `data-notes`
  updated to match the new wording. `AGENTS.md`'s outstanding-chip count dropped from 6 to
  3, following the same pattern used for the `#5` engineer quote's resolution. Deterministic
  round, no sandbox page; `training_a_team` has no presenter.json so no presenter check.
  PR #1.

- **2026-08-28, slide 16 (`#s-staging`) pixel art redrawn at 1024px.** Joseph: "Re-do 16's
  pixel art with the highest possible res please". The Pixelforge project `s-staging-steps`
  (`b4001dd6`) was kept and its spec amended in place with `update-spec` - `rules.max_canvas`
  and all three deliverables raised to 1024x1024, `export: { scale: 1, expect: [1024, 1024] }`,
  four ramp steps added (31 to 34, still inside the 40 cap), plus a `plate_top` guide and a
  `plate_body` zone on each deliverable so an icon that loses the shared plate now fails lint.
  A canvas cannot be resized, so the three 384px canvases (`3567a054`, `471a30e5`, `c60515d3`)
  were deleted and three 1024px ones created in their place (`705f3e19` wipe, `002f379e` apply,
  `4f41bbd9` iterate). All three were redrawn from scratch at the new size, not scaled up: the
  broom head is eighteen separately toned bristle strands with a ragged drawn tip line, the
  handle carries a specular streak and four grain lines, the ferrule three rivets; the slabs
  and blocks have four-step bevels and engraved configuration rules; the loop is shaded by
  angle in half-degree wedges across nine tones with a lit inner rim; the plate gained a
  specular streak, five panel joins and end bevels. Lint is zero-error on all three (the wipe
  keeps 22 orphan-pixel warnings where the diagonal strand edges meet the outline, and the
  deliberate `banding: info` findings). PNGs: wipe 27,154 B, apply 9,486 B, iterate 27,576 B,
  64,216 B for the set; the deck goes 146,502 -> 210,303 B, 63,432 of that the three data
  URIs and the rest the CSS comment. `image-rendering` on
  `.s-staging-art` changes from `pixelated` to `auto`: at 1024px shown at 168px,
  nearest-neighbour keeps one source pixel in six and visibly fragments the loop's outline and
  the crosses, and Chrome maps `crisp-edges` to the same nearest path (byte-identical
  screenshots), so the smooth downscale is the only one that holds. The display width stays at
  168px. AGENTS.md's `art/` row, Embedded artwork bullet and slide-16 line are updated. The
  presenter check prints OK, the dash lint is clean, and the diff against `main` touches only
  the `#s-staging` CSS block, its three `<img src>` attributes, `art/` and the two docs. PR #58.

- **2026-08-28, slide 12 (`#s11`) option D accepted.** Joseph: "D for 12 is good." Option D
  from the sandbox page `s11-bullets-round2.html` is folded into the deck's `#s11` CSS
  block as one clean set of rules, replacing option A's dashed-list rules rather than
  stacking on them: the four points now read as a numbered list, 1 to 4, the number in mono
  in an accent gutter driven by a CSS counter, the name in the display face, bold, and the
  fourth number and name both in the danger colour for the rejected `-generate-config-out`
  flag. No markup change was needed - option D was pure CSS on the existing list. The
  sandbox page `presentations/sandbox/migrating_an_instance/s11-bullets-round2.html` is
  deleted and its index entry is now a non-linked `.done` line recording the decision.
  AGENTS.md's slide-12 line and the Sandbox section's Current pages/Decided lines are
  updated. The presenter check prints OK, the dash lint is clean, and the diff against
  `main` touches only the `#s11` CSS block, the sandbox index and AGENTS.md. PR #57.

- **2026-08-28, slide 9 (`#s-sentinel`) round one rejected, three fresh treatments
  offered.** Joseph: "9 as well, can we have 3 fresh options?" - read alongside his note on
  slide 12 that he wants things simpler and "nice easily separated". Round one (PR #54) is
  out: the `.s-sentinel-opt-b`, `-opt-c` and `-opt-d` wrappers, their markup and the whole
  S-SENTINEL CSS block are deleted, which leaves the section as the shared `.lead` plus the
  three `.gates-3` cards and no slide-specific rules at all. The live slide screenshots
  byte-identical before and after (`cmp` passes) and `#s14` is unchanged. The new set is
  deliberately different in kind - no wall, no staircase, no timeline axis, no drawn device
  of any sort - and all three are pure CSS on the existing markup, so nothing new ships in
  the deck this round and an accepted option pastes straight in. B turns the cards into
  three tall columns ruled top and bottom, the number large in mono and the only coloured
  thing on the slide (danger, muted, accent), verb at 44px, sentence at body size. C reads
  the three states as one run across the slide: three plain blocks on the card surface
  joined by two arrows in the diagram line colour, verb inside each block. D splits the
  slide down the middle - the lead holds the left half at body size as the setup, the three
  gates stack down the right as a numbered list with a hairline between each. Every sentence
  is verbatim, everything clears the timeline strip and the shared `.lead`, `.gates` and
  `.gate*` rules are untouched. The presenter check prints OK. Sandbox page
  `presentations/sandbox/migrating_an_instance/s-sentinel-round2.html`; the round-one page
  is deleted and its index entry is now a non-linked `.done` line recording that it was
  superseded on 2026-08-28 with no option chosen. AGENTS.md slide list, Current pages and
  Decided lines updated. PR #56, awaiting a decision.

- **2026-08-28, slide 12 (`#s11`) round one rejected, three plain bullet treatments
  offered.** Joseph: "I don't really like the options for 12 - can you re-do them and jsut
  make them nice easily separated bullet points?" Round one (PR #53) is out: the
  `.s11-opt-a` to `.s11-opt-d` wrappers, their markup including the inline-SVG glyphs and
  all their CSS are gone, the right-hand column is plain markup again, and the round one
  sandbox page is deleted with its index entry turned into a non-linked superseded record.
  The wording of the four points is untouched. The three new treatments are pure CSS on the
  same list, nothing cleverer: B separates the points with a hairline rule at full column
  width, C puts each on the deck's navy card surface with the name in a fixed-width left
  column so the four lines align, D numbers them 1 to 4 in mono in a gutter with the name in
  the display face. Option A is the dashed list the deck now ships and injects nothing. The
  rejected fourth point keeps the danger colour on its name in all four, never a
  strike-through. Sandbox: `presentations/sandbox/migrating_an_instance/s11-bullets-round2.html`.
  PR #55, awaiting a decision.

- **2026-08-28, slide 9 (`#s-sentinel`) three visual treatments offered.** Joseph: "Can you
  generate some visual options for 9 please?" A visual round only - no wording or fact
  changes anywhere, and nothing changes in the deck as it ships: option A is the live slide
  (the lead over three shared gate cards) and injects nothing. B, C and D need markup, so
  all three ride along as hidden wrappers inside the section - `.s-sentinel-opt-b`, `-opt-c`,
  `-opt-d` - with one `#s-sentinel` rule hiding them and the sandbox page flipping which one
  shows, the same pattern `#s-workspace` used. B draws the wall: a hatched policy barrier
  down the middle of the slide with the same run meeting it three times, stopping dead
  against it in the danger colour, passing through a dashed temporary opening, then through
  an open one edged in the accent, each lane's sentence beside its own crossing. C drops the
  paragraph for a staircase - three panels sharing a bottom edge and growing taller left to
  right, number in mono, verb at title size, sentence at body size, colour ramping danger to
  cornflower to accent. D keeps the lead, quietened, and lays the three states on an axis
  running Nov 2025 to Jan 2026, the slide's own `data-when` range: a blunt stop at the start,
  a repeating tick band for the exception windows and one accent end marker for the standing
  exception, with a TODO chip because the number of windows is not recorded. All the new CSS
  is one `#s-sentinel`-scoped block next to the other slide blocks; the shared `.lead`,
  `.gates` and `.gate*` rules are untouched and `#s14` screenshots identical. The option A
  render is byte-identical to the same screenshot taken from `main`. The presenter check
  prints OK. Sandbox page
  `presentations/sandbox/migrating_an_instance/s-sentinel-visual.html`, index entry added,
  `AGENTS.md`'s slide-9 line and the Sandbox section's "Current pages" line updated.
  Awaiting a decision. PR #54.
- **2026-08-28, slide 12 (`#s11`) the right-hand points.** Joseph: "Can you give some visual
  options for slide 12, only the right hand side with text. Focus on these 4 points: tidying
  with prune, jamfpy SDK, regex, and the rejecting the generate-config-out." The right-hand
  column goes from seven bullets to those four, in that order, each one a mono name over a
  single line of plain text. The three that came off are already told elsewhere: the
  per-candidate script and the structured map, and the map pasted into a `local` with a
  `for_each` block, are both stages in the pipeline diagram on the left, and AI-assisted
  validation is not a tools point. The "mostly Copilot CLI" mention leaves the slide with
  that last bullet, which suits Joseph's earlier request not to name Copilot; the third
  speaker note pointed straight at it, so it is reworded to say AI use in one line without
  naming the tool and mirrored into `presenter.json`. The other two notes and the left-hand
  SVG are untouched. Three visual treatments of the four points went to the sandbox as
  `s11-right-hand-points.html`, all four shipping as markup wrappers `.s11-opt-a` to
  `.s11-opt-d` inside `#s11` with their rules in the deck, so the sandbox CSS only flips
  which one shows: A (live) the four points as one dashed list; B four cards, the name a
  large monospace tag, the rejected flag struck through behind a danger-coloured edge; C a
  2x2 grid of tiles each carrying an inline-SVG glyph in the `dg-*` style - a bin, an
  angle-bracket mark, a literal `.*` over a rule, a struck-through code block; D a
  used/rejected ledger, three ticks on a rail and the flag alone below a full-width rule.
  Also normalised the SDK's spelling to `jamfpy` in `AGENTS.md` to match the deck, recorded
  as a settled fact. The presenter check prints OK. Awaiting a decision. PR #53.

- **2026-08-28, slide 16 (`#s-staging`): option B accepted.** Joseph: "16 - option B
  please." Folded option B's CSS (a numbered rail of the three steps down the left, verb
  and sentence on one line each, lead and takeaway as a quiet right-hand column) into the
  deck's `#s-staging` block in place of option A's rules, no markup change. The pixel-art
  icons were grown from B's sandbox size of 96px to 168px - the largest width a rail row
  allows before the third row's icon meets the timeline strip. Sandbox page deleted,
  `AGENTS.md` slide list and Sandbox section updated. Presenter check OK, no dash hits. PR
  #52.
- **2026-08-28, feedback-workflow.md updated for the handover.** The stale
  2026-08-27 handover section (PRs 4 to 28, slide 4 as the last thing settled, PR #26 as
  the open collaborator PR) retitled "superseded" and kept below a new "State at handover
  (2026-08-28)" section covering PRs #29 to #49 plus collaborator PRs #26, #30 and #47: a
  per-slide status for slides 6, 10, 11, 14, 15, 16, 17, deleted slide 19 (`#s-today`) and
  By the numbers (`#s16b`), the training-deck collaborator merge (PR #30), the timeline
  adherence doc (PR #45) and the pixel-art asset directory `art/` (PR #49), plus a "What is
  pending" list. Two Gotchas added: background agents dying when the machine sleeps, and
  amending an in-flight agent's brief before it opens its PR. "Last revised" bumped to
  2026-08-28. `AGENTS.md` checked against the new state and needed no changes. PR #51.
- **2026-08-28, sandbox index: split the merged entries.** Joseph: "The sandbox seems to be
  having some visual issues - the entries are merging?" Two merge-conflict resolutions on
  `presentations/sandbox/migrating_an_instance/index.html` had left the first `<li>` holding
  three entries run together with no `</li><li>` between them - slide 19 (done), slide 17
  (done) and slide 16 (link) - rendering as one merged list item. Split into three separate
  `<li>` elements, one entry each, matching every other item in the list; no wording or
  other entries changed. Verified: 14 `<li>` open and close, 14 `.meta` paragraphs,
  `xmllint --html --noout` clean, and a headless-Chrome screenshot over HTTP shows each
  entry as its own spaced item with the slide 16 link on its own line. PR #50.

- **2026-08-28, slide 16 (`#s-staging`) pixel-art icons for the three rebuild steps.**
  Joseph: "Use the pixel art generator to make a good, high quality pixelart for each box on
  16." Three 384px icons drawn with Pixelforge, project id `b4001dd6`, one per step, all
  sharing the same plate at the foot of the canvas so they read as one story: Wipe is a yard
  broom with a banded steel ferrule sweeping coral debris off the plate with two lime blocks
  left standing (APNS and the identity provider); Apply is two lime configuration slabs
  landed on the plate with a third still in the air under a wide off-white arrow; Iterate is
  a shaded loop arrow closing on a lime tick with two coral crosses outside it. Spec and
  exports live at `presentations/migrating_an_instance/art/s-staging-steps.md` plus
  `s-staging-wipe.png`, `s-staging-apply.png` and `s-staging-iterate.png` (16.6KB for the
  three), embedded in the slide markup as base64 data URIs so the deck still opens off disk.
  The card gap drops to `--sp-2` so the 192px icon fits between the number and the verb
  without pushing the takeaway into the timeline strip. The open sandbox page
  `s-staging-steps-first` was adjusted for the art: the icons are in all four renders, B
  sizes them at 96px beside the ring, C at 144px above each node, and D shows only the
  broom, at 120px, because its half-height cards have no room. PR #49.

- **2026-08-28, slide 19 (`#s16b`) option C accepted, date range changed.** Joseph:
  "Option C for the numbers" then "For the date line on the numbers, amend to Jan 2026 to
  Sept 2026 and leave it as that." Option C (900 PRs merged as a hero number, the other four
  figures - 35-40 contributors, 1,902 commits, 134 HCL files, 19,000+ lines of code - in a
  quiet supporting row) applied as the net result: the `.stats` tile grid (option A) and the
  `.s16b-opt-b`/`-opt-d` wrappers removed along with their CSS, the `.s16b-opt-c` wrapper
  unwrapped so it is the slide's plain markup, and one clean block of `#s16b` rules left
  behind; the shared `.slide-centred` rule used by `#s18` was untouched (screenshots of both
  slides confirm it). The date-range figure changed from "Apr 2025 -> May 2026" to "Jan 2026
  -> Sept 2026", label unchanged. Per instruction the speaker notes and `presenter.json` were
  left as they are, so they still build to April 2025 (provider-development start) and May
  2026 (v1.0.0 and handover) - the slide now disagrees with its own notes, flagged in the PR
  for Joseph to resolve rather than fixed here. The presenter check prints OK. The sandbox
  page deleted, its index entry retired to a `.done` line; `AGENTS.md`'s slide list, Sandbox
  section and settled Numbers fact updated to match. PR #48.
- **2026-08-27, slide 19 (`#s16b`) refreshed figures, three visualisations offered.**
  Joseph: "Updated stats for the by the numbers side - 35-40 contributers / 19,000+ lines
  of code / 900 PRs merged / 134 HCL Files Give options, think graphs, or visualisations.
  Keep the currnet layout as A." The figures are deterministic and ship in this PR across
  all four renders: 14+ becomes 35-40 contributors, 526+ pull requests becomes 900 PRs
  merged, 127 Terraform files becomes 134 HCL files, and the lines figure stays at 19,000+
  but takes Joseph's wording, "lines of code" rather than "lines of HCL". The date range
  and the 1,902 commits are untouched because he did not restate them; the slide carries no
  chips on its stat tiles so the stale commit count is flagged in the PR body rather than
  chipped onto the slide, and `AGENTS.md`'s settled Numbers fact now records that it needs
  confirming. The speaker notes needed no change - "approaching a thousand pull requests
  now" still reads correctly against 900, and nothing else in them states a figure - and
  the check prints OK. The visualisation question ships as `s16b-numbers.html`: A, the six
  tiles with the new figures, which is what the deck ships; B, five gauge bars, one per
  countable figure, each scaled to its own next round number and saying so, with 35-40 and
  19,000+ ending in open outlined segments because they are floors rather than counts;
  C, 900 PRs merged as a hero number at roughly four times hero size with the other four
  reduced to a quiet row; D, unit grids of one mark per contributor (the last five outlined,
  which is the range drawn honestly) and one mark per HCL file, under a "Too many to draw"
  rule holding the three figures that will not take that treatment. B, C and D ship as
  `.s16b-opt-b` / `-opt-c` / `-opt-d` wrappers hidden by one `#s16b` rule. Awaiting a
  decision. PR #46.
- **2026-08-27, timeline adherence doc added.** Joseph: "Generate a timeline adhereance
  doc for this deck." `docs/timeline-adherence.md` added: one row per slide of
  `migrating_an_instance` as it stands on `main` (id, title, speaker, timer,
  current `data-when`), a blank "Month (fill in)" column for Joseph, and a "Current
  stops on the strip" summary showing the pile-ups on 2025-11 and 2026-07 and the gap
  at 2026-06. No slide, CSS or `presenter.json` touched. `AGENTS.md`'s file-layout table
  gained one row for the doc. PR #45.
- **2026-08-27, slide 17 (`#s-pivot`) sandbox closed.** Joseph: "Close the slide 17
  sandbox." No option chosen: the live slide (option A) kept. The `.s-pivot-opt-c` and
  `.s-pivot-opt-d` wrappers and their markup removed, along with the CSS that only served
  them; the `.s-pivot-opt-a` wrapper unwrapped so the slide's markup is plain, and the
  `#s-pivot` CSS left as one clean block for the live layout - screenshots before and after
  the edit `cmp` identical. The sandbox page deleted, its index entry retired to a `.done`
  line; `AGENTS.md`'s slide list and Sandbox section updated to match; the presenter check
  prints OK. PR #44.
- **2026-08-27, slide 19 (`#s-today`) deleted.** Joseph: "Remove 19." "The estate today"
  removed at Joseph's request: section (four-tier route to live diagram, Release Please ->
  CalVer cards), its `presenter.json` entry, the `.evolution`/`.evo-title` CSS (used nowhere
  else) and `.pipe-off`/`.pipe-gap` (used only by this section's pipeline row); the shared
  `.pipe-node`/`.pipeline-label`/`.pipeline-band` rules stay, still used by `#s01`, and the
  S01 CSS comment no longer mentions `s-today`. Its 60 s moved to `s17` (Questions, now
  360 s) so the timers still sum to 1800. `AGENTS.md` slide list renumbered to 22, the
  reader-extras list and folded-away-slides note updated. No other slide pointed forward to
  it. PR #43.
- **2026-08-27, slide 15 (`#s14`) gate 2 says remote backend, drops the Copilot namedrop.**
  Joseph: "state should just be storeed in remote backend. Just say use AI, do not
  namedrop copilot." Edited in place: gate 2 becomes "State is stored in a remote backend
  and not locally inspectable - AI-assisted checks confirmed each resource exists with the
  correct dependencies assigned." (was "State is centralised in HCP and not locally
  inspectable - AI-assisted checks (Copilot CLI) confirmed..."), and the matching speaker
  note becomes "State lives in a remote backend and is not locally inspectable, hence the
  AI checks in gate 2." (was "...hence the Copilot CLI checks..."), mirrored into
  `presenter.json`; the check prints OK. `s11` also names Copilot CLI for the same
  underlying fact (spec.md Q8) but is a different slide, out of scope here - left
  untouched. Other "HCP" mentions (`s-workspace`, `s-sentinel`, `s-today`) describe the
  real HCP Terraform tooling, unrelated to this gate's wording - left as is. PR #42.
- **2026-08-27, slide 17 (`#s-pivot`) pivot line cut, four display options on the sandbox.**
  Joseph: "the pivot is too LLM. That line can be removed. Give options on the display."
  Applied deterministically: the `.statement` paragraph ("It got out of hand. The pivot:
  shared modules own the configuration; thin per-instance roots own only what genuinely
  differs.") is gone and its TODO chip moved onto the code block as `.s-pivot-chip`, so the
  reminder survives. `#s-pivot` was the only user of the shared `.statement` rule; the rule
  stays where it is, untouched, per the shared-CSS rule. The second speaker note used the
  same phrasing and is reworded to "Where we ended up: the modules hold the configuration
  and each instance's root only holds what is actually different." - same fact, mirrored
  into `presenter.json`, and the check prints OK. The display question ships as
  `s-pivot-display.html`: A, the lead over the code as one aligned column with the code a
  step up the type scale (what the deck ships from this PR); B, the lead demoted to a
  kicker and the code filling the slide at heading size with the "everywhere" comment turned
  lime as the punchline (pure CSS on A's markup); C, two columns - the code on the left,
  what one URL decided stacked on the right, drawn only from the code block and the notes
  with the TODO chip closing the stack; D, the conditional as an editor window with a
  `terraform/jamfpro/` file tab, a line-number gutter and line 2 picked out with a
  current-line band. C and D ship as `.s-pivot-opt-c` / `-opt-d` wrappers hidden by one
  `#s-pivot` rule. Awaiting a decision. PR #41.
- **2026-08-27, slide 16 (`#s-staging`) plainer wording, steps first, four layouts offered.**
  Joseph asked for the text to be far more human and for the slide to lean on the steps
  rather than the words around them. The rewrite is deterministic and ships in this PR:
  lead "Production was fully code. Staging was still years of drift - importing that drift
  would only have enshrined it. So it was not imported at all." becomes "Production was
  code. Staging was years of drift, so we didn't import it."; the three steps become
  "Wipe. We cleared staging out, keeping APNS and the cloud identity provider.", "Apply. We
  pointed production's configuration at the empty instance." and "Iterate. We fixed the
  errors, pass after pass, until the run came back clean."; the takeaway becomes "Staging
  doesn't claim parity any more. It inherits it, from the same modules." with the month
  chip kept; and the `.slide-note` about the module split is gone from the slide because
  the speaker notes already set up the next two slides. Notes eased the same way and
  mirrored into `presenter.json`; the check prints OK. Same facts throughout. Option A -
  what ships - is the steps-first arrangement: the three cards grow to full-height panels
  with the verb at `--fs-h1` in the card's own colour, the lead drops to muted body text
  and the takeaway to one line, all in a new `#s-staging` CSS block after the S14 gate-card
  block so the shared `.lead`, `.gates` and `.gate*` rules are untouched (`#s14` verified
  unchanged). Sandbox page `s-staging-steps-first.html` offers A plus B (a numbered run
  down the left on a vertical rail, the lead and takeaway as a quiet right-hand column), C
  (one left-to-right flow strip in the deck's diagram style, chevrons between the nodes,
  the lead dropped and the takeaway as the closing statement) and D (the wipe as a
  full-height hero panel at `--fs-hero`, apply and iterate stacked beside it) - all four
  pure CSS on the same markup, so whichever wins pastes straight in. Awaits a decision.
  PR #40.
- **2026-08-27, slide 15 (`#s14`) option B accepted - the terminal as a real window.**
  Joseph picked option B from the `s14-terminal-excerpt` sandbox page: the block becomes a
  window sitting on the stage rather than a card lying flat on it, with a light chrome bar,
  red, amber and lime traffic-light dots, a centred `joseph@jnuc - zsh` title, the command
  in bold white against the lime result, and a lime block cursor blinking on a fresh prompt
  line underneath, plus a drop shadow. Applied as the net result: the window title span and
  the fresh-prompt cursor markup are now the slide's plain markup, and the CSS is one clean
  `#s14`-scoped block replacing the old unscoped `.terminal`/`.term-*` rules rather than
  stacking on them; the shared `.gates`/`.gate*` rules are untouched. `prefers-reduced-motion`
  still stops the cursor blink; every colour stays a token. Speaker notes and
  `presenter.json` needed no change - neither references the block's styling - and the check
  prints OK. Sandbox page deleted, index entry marked `.done`, `AGENTS.md`'s slide-15
  summary and the Sandbox section's "Current pages"/"Decided" lines updated. PR #39.
- **2026-08-27, slide 15 (`#s14`) terminal excerpt options offered.** Joseph said the diagram
  at the top of the slide is not obviously a terminal excerpt and asked for styling options
  that make it read as one. Nothing in the feedback was deterministic, so the deck is
  untouched this round: wording, the `terraform plan` line, the result and the four gates all
  stay, and the speaker notes and `presenter.json` need nothing (neither mentions the block's
  styling); the check prints OK. Sandbox page
  `presentations/sandbox/migrating_an_instance/s14-terminal-excerpt.html` offers A (the block
  as it stands, live now - the same navy card surface, border and radius as the four gate
  cards below it, which is the problem), B (a real window: a light grey chrome bar, red,
  amber and lime traffic lights, a `joseph@jnuc - zsh` title, the command in bold white
  against the lime result, a blinking cursor on a fresh prompt and a drop shadow, gates
  untouched), C (the opposite - no chrome at all, the block full width behind an 8px lime
  rule with square corners at 44px type, and the gate cards stripped to bare columns under
  hairline rules so the console is the only solid object on the slide) and D (a quoted
  excerpt: a lime "Terminal" tab on the corner, a gradient and scanlines on the surface, the
  command dropped to caption size and the result promoted to 44px bold behind a lime tick,
  gates kept but unfilled) - awaits a decision. All the option CSS is scoped to `#s14`
  because `.terminal`, the `.term-*` classes, `.card`, `.gate` and `.muted` are shared or
  generic. PR #38.
- **2026-08-27, slide 14 (`#s13`) option D accepted, wording made more human.** Joseph
  picked option D from the `s13-policies-only` sandbox page - the exception and its reason
  in large type, nothing else - with one change: reword it so it sounds spoken rather than
  written. Applied as the net result: the `.s13-opt-a`/`-b`/`-c`/`-d` wrappers and the hide
  rule are gone, D's four lines are the slide's plain markup, and the CSS is one clean
  `#s13` block. New wording - kicker "Just one exception"; statement "We kept policies in
  plain HCL."; reason "They're too different from each other. One `for_each` map would have
  to carry every field any policy might need, and nobody could read it."; close "Once the
  map gets harder to read than plain HCL, the pattern isn't earning its keep any more." Same
  facts throughout: policies were the one exception, too diverse for one map, so they stayed
  in plain HCL, and the pattern stops paying when the map is harder to read than the HCL.
  Speaker note eased the same way and mirrored into `presenter.json`; the check prints OK.
  Sandbox page deleted, index entry marked `.done`, `AGENTS.md`'s slide-14 summary and the
  Sandbox section's "Current pages"/"Decided" lines updated. PR #37.
- **2026-08-27, slide 6 (`#s05`) option D accepted - each path in its own panel.**
  Joseph picked option D from the `s05-fill-the-space` sandbox page: the hairlines between
  paths become full bordered panels, one per path, with the chosen path (03) edged in the
  accent colour, and each flow diagram sits centred inside its panel at 70% width rather
  than running edge to edge. Pure CSS on the existing markup - the option's rules folded
  into the S05 block as the net result, replacing the rules they override rather than
  stacking on top (the old border-bottom-only path separator and `last-child` rule are
  gone, replaced by a full border and radius on every panel). Speaker notes and
  `presenter.json` untouched - neither references the old layout - and the check prints OK.
  Sandbox page deleted, index entry marked `.done`, `AGENTS.md`'s slide-6 summary and
  Sandbox section updated. PR #36.
- **2026-08-27, slide 11 (`#s08`) migration wave workflow, option C applied.** Joseph picked
  option C from `s08-use-of-space.html`: the seven steps become full-width bands stepping
  down the slide, each one starting a notch further in than the band above it and all
  ending flush right, one step per line at slide size with the numbers in an aligned gutter
  and a coloured left edge - lime, red on step 3's freeze. Pure CSS on the existing markup,
  folded into the `#s08` block as one clean set of rules replacing the old single-row grid
  rather than layering on top. Speaker notes and `presenter.json` needed no change - neither
  pointed at the layout. Sandbox page deleted, its index entry retired to `.done`, and
  `AGENTS.md`'s slide-11 summary and the Sandbox section's "Current pages"/"Decided" lines
  updated. Presenter check prints OK. PR #35.
- **2026-08-27, slide 10 (`#s10`) option C accepted - everything bigger, diagram reflowed.**
  Joseph picked option C from the `s10-diagram-text` sandbox page: the tier labels move up
  to `--fs-body` and the right-hand examples to `--fs-code`, both a step further than the
  modest bump already shipping, and the four diagram bands grow from 140 to 156 user units
  (viewBox 1728x720 to 1728x784) so the bigger text keeps the same breathing room and stays
  clear of the timeline strip. The sandbox page did the band reflow with a DOM edit in its
  `load` handler; the deck carries it as a direct edit of the SVG's band heights, y positions
  and viewBox, so no script is needed. Speaker notes and `presenter.json` untouched - neither
  mentions the diagram's text size - and the check prints OK. Sandbox page deleted, index
  entry marked `.done`, `AGENTS.md`'s Sandbox section updated. PR #34.
- **2026-08-27, slide 6 (`#s05`) control note folded into path 03, sandbox options added.**
  Joseph asked for the annotation at the foot of the slide to go, its message to be condensed
  into option 3, and everything to expand into the space so the slide feels less busy. Applied
  deterministically: the `.card.control-note` block is out of `#s05` (the class is shared with
  `#s-singletons`, so only the slide's own two rules and its markup went; the shared rules
  stay) and path 03 carries a one-line version of it. The speaker notes already told the
  read-only-scopes story on path 03, so none pointed at the removed card and `presenter.json`
  is untouched; the check prints OK. The expansion ships as option A: each flow's viewBox
  cropped close to its drawn width so the diagrams scale up by about a quarter and fill the
  slide instead of leaving a quarter of every row empty. Sandbox page
  `s05-fill-the-space.html` offers A (that expansion, live), B (the chosen path in an accent
  panel with the two discounted paths shrunk and dimmed above it), C (the diagrams for 01 and
  02 dropped entirely, one drawing left on the slide and the control line as a closing
  statement) and D (each path as its own bordered panel with the diagram centred inside it) -
  awaits a decision. PR #33.
- **2026-08-27, slide 14 (`#s13`) cut back to policies, four options offered.** Dock items
  were never a `for_each` exception, so the dock items card, its column and the mention in
  the speaker note are gone, and the reason for the policies exception is reworded from
  payload complexity and readability to how diverse policies are - a map has to carry every
  field any policy might need. `presenter.json` mirrored, `AGENTS.md`'s slide-order entry
  and the "for_each exceptions" settled fact updated to say policies only with diversity as
  the reason. Because the slide loses half its content, four layouts ship as wrappers inside
  `#s13`: A the removal done cleanly, policies re-laid as one full-width panel (live);
  B five policy silhouettes with a sixth column showing everything one map would hold;
  C the `for_each` attempt set against the plain HCL that replaced it; D the exception and
  its reason in large type. Sandbox page
  `presentations/sandbox/migrating_an_instance/s13-policies-only.html`, awaiting a decision.
  PR #32.
- **2026-08-27, slide 11 (`#s08`) three layouts offered for the empty half of the slide.**
  Joseph's feedback was that the content of the migration wave workflow is already good and
  only the use of the space needs work. The disk screenshot confirmed it: seven narrow cards
  in one row across the top third, body text at caption size, and roughly 400px of empty
  stage below them. Layout round only, so nothing deterministic to apply and the deck itself
  is untouched - option A is the live slide. Sandbox page `s08-use-of-space.html` offers B
  (two rows, four then three, body text up to `--fs-body` and chevrons in the gaps carrying
  the direction of travel), C (seven full-width bands stepping down the slide, one step per
  line, numbers in an aligned gutter, right edges flush) and D (three columns at three
  weights - steps 1 and 2 left, the permissions revoke as a full-height centre panel with
  the lock at scale, steps 4 to 7 right). All three are CSS on the existing markup, scoped
  to `#s08`, tokens only, so no wrappers were needed in the deck. Awaits a decision. PR #31.
- **2026-08-27, slide 10 (`#s10`) diagram text bumped, sandbox options added.** Joseph's
  "text glitches until refresh" report investigated - fonts, transitions, transform/
  clip-path/filter/contain on text, and the SVG's `tspan dx` labels all checked; could not
  reproduce across `--virtual-time-budget` 500/3000 disk screenshots or real keyboard
  navigation to s10 followed by a hard refresh over HTTP, so no fix invented. The size
  request applied deterministically: `#s10 .dg-label` and `#s10 .dg-eg` both move one step
  up the `--fs-*` scale (ships now). Sandbox page `s10-diagram-text.html` offers A (that
  same modest bump, live), B (tier labels pushed further, examples left alone) and C (both
  pushed further, four bands reflowed to stay clear of the timeline strip) - awaits a
  decision. PR #29.
- **2026-08-27, feedback-workflow.md updated for the handover.** Today's learnings folded
  in: the exceptions to "no repo edits", the collaborator-PR rule, model choice, agent
  naming, the acceptance-with-a-change rule, the fetch-and-merge-first requirement for
  agents, per-file merge-conflict resolution rules, the sandbox wrapper mechanism for a new
  slide or full redesign, the per-deck sandbox path recipe, the presenter-check script
  isolation gotcha, the auto-mode `git merge` refusal, and untracked source files in the
  repo root. A new "State at handover (2026-08-27)" section added to the Log with a
  per-slide status for `migrating_an_instance` and what is pending. `AGENTS.md` checked
  against that state and needed no changes - PR #27 had already brought it current. PR #28.
- **2026-08-27, slide 4 (`#s-workspace`) decided.** The live collaborator slide (PR #21)
  kept; round-three options B to D rejected (none captured the point) and removed from the
  deck, along with their CSS rules. The sandbox page deleted, its index entry retired to a
  `.done` line. PR #27.
- **2026-08-27, slide 7 (`#s07`) runner line of sight row reworded, TODO chips cleared.**
  Migration prep's runner line of sight row reworded to Joseph's live wording; a third
  row, "Org-wide policies", added after backout plan (no chip); both remaining TODO chips
  on the slide (runner line of sight, backout plan) removed, with the AGENTS.md chip table
  and slide-order note updated to match; speaker notes and presenter.json mirrored. PR
  #25.
- **2026-08-27, slide 7 (`#s07`) option D accepted.** Sandbox option D ("two portions")
  applied to the deck's `#s07` rules after the slide's earlier rename to Prerequisites:
  instance prep and migration prep now sit side by side. The sandbox page deleted, its
  index entry retired to a `.done` line; the two TODO chips on the migration rows remain,
  pending Gordon's wording. PR #24.
- **2026-08-27, Joseph's and Gordon's photos added to both decks.** Both photos
  centre-cropped, resized and compressed in `_shared/speakers.js` to match Dafydd's
  existing 420x420 JPEG (byte size matched to his ~27KB); the amber TODO chip for the
  missing photos removed from the title slide of both decks; `AGENTS.md` updated. PR #20.
- **2026-08-27, sandbox split one per deck.** `presentations/sandbox/` restructured: a
  minimal chooser stays at the top alongside the shared `sandbox.css`, and each deck now has
  its own subdirectory (`migrating_an_instance/`, `training_a_team/`) with its own
  hand-maintained index and pages. `migrating_an_instance`'s existing index and pages moved
  in with `git mv`; `training_a_team`'s index starts empty. The landing page's single global
  Sandbox button replaced with one Sandbox button per deck card. `tools/sandbox-template.html`
  and this file's paths and URLs updated to match, `AGENTS.md`'s Sandbox section rewritten.
  At Joseph's request. PR #19.
- **2026-08-27, slide 8 (`#s-singletons`) import block filled in.** The empty
  `import {}` in the `jamfpro_client_checkin` code sample now reads `to =
  jamfpro_client_checkin.jamfpro_client_checkin` / `id =
  "jamfpro_client_checkin_singleton"`. The provider's `client_checkin.md` docs carry no
  Import section, so the id came from the provider source
  (`internal/services/client_checkin/resource_crud.go`, which fixes the resource's id to
  `jamfpro_client_checkin_singleton` on create/read/update), corroborated by the identical
  `jamfpro_activation_code_singleton` pattern on the sibling singleton resource. At
  Joseph's request, no options. PR #18.
- **2026-08-27, Sandbox button added to the landing page.** A button-style link (`.go`,
  reused from the deck cards) to `sandbox/` now sits under the deck cards on
  `presentations/index.html`, with a one-line caption. `AGENTS.md` and this file updated to
  match - both said nothing linked to the sandbox from the landing page. At Joseph's
  request. PR #16.
- **2026-08-27, slide 6 (`#s05`) option card blurb reduced.** `.option` is only used on
  this slide, but the blurb had no explicit font-size rule of its own - it inherited the
  body default. Added `#s05 .option p { font-size: var(--fs-caption); }` (down from the
  effective `--fs-body`; `--fs-body` alone made no visible difference, so the fix went
  straight to `--fs-caption`), which clears the control note from the timeline strip. At
  Joseph's request. PR #12.
- **2026-08-27, slide 5 (`#s05`) option wording amended.** The left option card now
  explains the striped approach (one resource at a time across the whole route to live,
  staging then production); the chosen card lost "But production is the configuration that
  matters." At Joseph's request, no options. PR #11.
- **2026-08-27, presenter and AGENTS.md slide titles aligned with the deck.** A
  collaborator's direct push to main (`7e1a99b`) retitled slide 4's `<h1>`/`aria-label`
  without mirroring `presenter.json`; two earlier renames (`#s-sentinel`, `#s-today`) were
  never mirrored either. `presenter.json` titles for `s04`, `s-sentinel` and `s-today` now
  match the deck; AGENTS.md's `s04` slide-order entry updated to match. The presenter sync
  check in this file now also compares titles, not just notes. PR #9.
- **2026-08-27, slide 2 (`#s01`) column titles decided.** Option C ("Bordered column
  panel") accepted and applied: `#s01 .constraints-col` is a bordered panel per column with
  a subgrid so the title row and both item rows share heights across all three panels;
  `#s01 .constraints-title` sits in accent display type; items are plain hairline-separated
  rows (the `card` class dropped from the six `<li>`s). Sandbox page deleted, index entry
  retired to a `.done` line. PR #8.
- **2026-08-27, slide 4 (`#s04`) closing line removed.** The "two more were dropped
  later, they come up where they happened" slide-note and its matching "tease the
  closing line" speaker note removed at Joseph's request; `.slide-note` CSS left in
  place (used elsewhere on the deck). `presenter.json` updated to match. PR #7.
- **2026-08-27, process changed to one PR per instruction.** Joseph: every instruction goes
  to an agent that returns one PR; the orchestrator only merges, resolves conflicts, pushes
  and reports. This file rewritten accordingly. PR #6.
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
