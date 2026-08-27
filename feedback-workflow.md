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

### State at handover (2026-08-27)

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
