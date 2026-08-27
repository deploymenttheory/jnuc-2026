> **Superseded 2026-08-27.** The feedback loop now runs per `feedback-workflow.md` at the
> repo root (chat feedback, one agent per slide, PRs merged by the orchestrator). This plan
> was written for the original single-file feedback list and was executed only for slide 2
> (`s01`). It is kept for its triage table (section 1), which maps that first feedback list
> to the current deck, and for its verification snippets. Do not execute it as written.

# Clicks to Code feedback round - implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the review feedback in `feedback-clickstocode.md` to the "From Clicks to Code" deck so every open item is either fixed in the slides or explicitly parked as a decision for Joseph.

**Architecture:** The deck is one hand-built HTML file (`presentations/migrating_an_instance/index.html`) with its own tokens, CSS, inline SVG and script. Every change is a content edit to that file, mirrored into `presenter.json` (notes and order) and `AGENTS.md` (slide list, settled facts), then a `.key` rebuild. There is no build step and no test suite; verification is headless-Chrome screenshots plus grep checks.

**Tech Stack:** Static HTML/CSS/JS, headless Google Chrome for screenshots, Node + Playwright + Keynote for `npm run build:key`.

**Spec:** `feedback-clickstocode.md` (repo root, currently untracked). Its slide numbers refer to the deck order *before* Dafydd's merge (`bdf25db`), which is the order still recorded in `presenter.json`: feedback slide 16 = Growing pains, 17 = The module structure, 18 = Rebuilding staging. Section 1 below maps every feedback line to the current deck.

## Global Constraints

Copied from `AGENTS.md` house rules and Joseph's global instructions. Every task inherits these.

- Branch: `feedback/clicks-to-code`. Commit as Joseph Little only - **no `Co-Authored-By` trailer on any commit**.
- Do not open a PR, merge, or trigger GitHub Actions unless told to. Merge to `main` deploys.
- British English. No emojis. No em-dashes or en-dashes anywhere - plain hyphens only. (The existing `→` arrows in the option cards and module tree are fine.)
- Titles are plain and human. No colon-glued two-part titles, no clever fragments.
- **Never invent facts, numbers, resource names or rationale.** Anything unconfirmed gets `<span class="todo">TODO: ...</span>`. Every fact used below is either on the deck already, in the "Settled story facts" section of `AGENTS.md`, or stated in `feedback-clickstocode.md`.
- All styling derives from the `:root` token block. Never hardcode a colour/font/size in slide markup - add a token if a new value is needed.
- Every `<section>` carries `data-when`, `data-speaker` and an `<aside class="notes">` as its last element. `aria-label` must match the visible slide title.
- `presenter.json` mirrors the deck: same slide order, same ids, `notes` equal to the aside's `<p>` texts, `timerSeconds` summing to 1800.
- **`AGENTS.md` is updated in the same commit as every change** that makes any statement in it stale. If a task changes nothing that `AGENTS.md` describes, say so in the commit message.
- One HTML file, zero requests off the machine, must work opened from `file://`.
- Deck edits ship with a rebuilt `presentations/migrating_an_instance/from-clicks-to-code-jnuc2026.key` (final task).

## How to verify a slide

There are no unit tests. The check for every task is: serve the repo, screenshot the slide at 1920x1080, look at the PNG (Read tool) for overflow past the bottom of the canvas or collision with the timeline strip at the bottom, then run the text lint. Shell state does not persist between Bash calls, so each block below is self-contained.

Screenshot one slide (replace `s01`):

```sh
cd /Users/josephlittle/Github/jnuc-2026 && (lsof -i :8741 >/dev/null 2>&1 || (python3 -m http.server 8741 >/dev/null 2>&1 &)) && sleep 1 && OUT="${TMPDIR:-/tmp}/jnuc-shots" && mkdir -p "$OUT" && "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --window-size=1920,1080 --hide-scrollbars --virtual-time-budget=3000 --screenshot="$OUT/s01.png" "http://localhost:8741/presentations/migrating_an_instance/index.html#s01" 2>/dev/null && echo "$OUT/s01.png"
```

Use your session scratchpad directory for `OUT` if you have one; `${TMPDIR:-/tmp}/jnuc-shots` is the fallback.

Text lint (expect no dash hits, and the slide count shown):

```sh
cd /Users/josephlittle/Github/jnuc-2026 && grep -n -e "—" -e "–" presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json AGENTS.md; echo "dash hits above (expect none)"; grep -c '<section class="slide' presentations/migrating_an_instance/index.html
```

Presenter/deck sync check - write this to your scratchpad as `check-presenter.mjs` once (Task 17 uses it, earlier tasks may):

```js
// Checks presenter.json mirrors the deck: same slide order, same notes, timers sum to the limit.
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

Run from the repo root: `cd /Users/josephlittle/Github/jnuc-2026 && node <scratchpad>/check-presenter.mjs`. Until Task 17 it will report order mismatches (presenter.json is already stale on `main`); from Task 17 on it must print `OK`.

---

## 1. Feedback triage against the current deck

Current order, with the feedback's number for each slide in brackets:

| # | id | Speaker | Feedback item | Status |
|---|---|---|---|---|
| 1 | `s00` Title | All | intros only | nothing to do |
| 2 | `s01` Context | Dafydd | "post-migration" constraint -> during-migration removal of perms | **Task 1** |
| 3 | `s02` Who touches Jamf Pro | Dafydd | none | nothing to do |
| 4 | `s03` Objectives | Dafydd | titles? repetitive of the two slides before it? | **Task 2** (decision D2) |
| 5 | `s04` Ideas rejected | Joseph | 500 is the recommendation, 5,000 the maximum; drop the last sentence; speaker cue | **Task 3** |
| 6 | `s05` Instance order | Joseph | "Option" -> "Initial choice"; card text wrong; bottom card reads like AI and needs clarifying | **Task 4** |
| 7 | `s07` Instance prep | Gordon | change to Gordon (done in `bdf25db`); clarify the whole slide | **Task 5** |
| 8 | `s-singletons` | Gordon | a sentence reads like AI | **Task 6** |
| 9 | `s-sentinel` | Gordon | does it fit? broaden to "infra challenges" or drop | **Task 7** (decision D1) |
| 10 | `s10` Sequencing | Dafydd | "end to end in production" unclear; remove "not one instance at a time"; examples (done in `bdf25db`) | **Task 8** |
| 11 | `s08` Wave workflow | Dafydd | all good - but receives the validation gates from 15 | **Task 9** |
| 12 | `s11` Tools | Gordon | remove TODO | done in `bdf25db`, nothing to do |
| 13 | `s12` for_each | Joseph | rewrite: helper output was big JSON-like locals full of repeated defaults; no generate-config-out; zoomed-out big local vs small one | **Task 11** |
| 14 | `s13` Exceptions | Joseph | policies were the only exception (low count, huge, unique) | **Task 12** |
| 15 | `s14` Validating | Joseph | bin it, merge into 11; replace with the workspace architecture | **Task 9** + **Task 10** |
| 16 (feedback 18) | `s-staging` | Dafydd | move before the module pivot (done in `bdf25db`); "years of drift" is wrong; kept items APNS and IdP (already on gate 1) | **Task 13** |
| 17 (feedback 16) | `s-pivot` Growing pains | Joseph | bottom reads like AI | **Task 14** |
| 18 (feedback 17) | `s15b` Module structure | Dafydd | clarify once the infra slide exists | **Task 15** |
| 19 | `s-today` | Gordon | none | receives the handover close in Task 16 |
| 20 | `s16b` Numbers | Gordon | do we need it? move the numbers to Links | **Task 16** |
| 21-23 | `s17`, `s18`, `s-thanks` | Anyone | none | `s18` gains the numbers in Task 16 |

End state: **22 slides** (23 - `s14` - `s16b` + `s-workspaces`).

## 2. Decisions Joseph should confirm (defaults are baked into the tasks)

Slide numbers below are the current deck order (Section 1, first column).

- **D1 - Slide 9, `s-sentinel` (Sentinel).** Default: keep it, retitled "Infrastructure challenges" and reframed as the shared Terraform platform with Sentinel as the worked example (Task 7). The alternative is deletion: remove the `s-sentinel` section, add its two notes to slide 11 `s08`'s aside, delete row 9 from the `AGENTS.md` slide list, remove `s-sentinel` from the reader-mode list, and drop its `presenter.json` entry (put its 90 seconds on `s17`).
- **D2 - Slide 4, `s03` (Objectives), against slide 2, `s01` (Context).** Default: slide 2 keeps the constraints the bank imposed, slide 4 keeps the decisions the team made, and the two duplicates (peer review, Vault) come off slide 4. Its title becomes "What we decided up front" so slides 2-5 read Context -> What we decided -> What we rejected (Task 2).
- **D3 - New slide 15, `s-workspaces` (Workspace architecture), replacing slide 15 `s14`.** Speaker default: Joseph. After the removals the split is Dafydd 7 / Joseph 6 / Gordon 5; giving it to Gordon makes it 7 / 5 / 6. Either is a one-attribute change in Task 10.
- **D4 - Slide 20, `s16b` (By the numbers) -> slide 22, `s18` (Links).** The stats move onto Links. Slide 20's "close on the handover" note is the best line in the deck; default: it moves to slide 19 `s-today`'s notes, the last content slide (Task 16).
- **D5 - Timeline goes backwards at slides 16-18.** Slide 16 `s-staging` is `2026-04:2026-05` and slides 17-18 (`s-pivot`, `s15b`) are `2026-03`, while `AGENTS.md` says the pivot came *after* the rebuild. Only Gordon's month for the rebuild resolves this; the TODO chip on slide 16 stays and **no task changes any `data-when`**.
- **D6 - `temp.tf`** at the repo root is Dafydd's scratch for the `s12` example. Not touched by this plan; delete it separately if unwanted.
- **D7 - `feedback-clickstocode.md` and `feedback-training.md`** are untracked in a public repo. This plan references the feedback file as its spec but does not commit it. Decide whether it goes in (`docs/` would keep it off the site - the deploy syncs `presentations/` only).

## 3. File map

| File | What changes |
|---|---|
| `presentations/migrating_an_instance/index.html` | All slide edits, two new CSS blocks (`.s08-validate`, `.s-ws-*`, `.code-zoom`, `.exceptions-1`, `.stats-compact`), two new tokens, one new section `s-workspaces`, two sections removed |
| `presentations/migrating_an_instance/presenter.json` | Rebuilt to the new order with the new notes and timers |
| `AGENTS.md` | Slide list, slide count, settled facts, reader-mode list, verification hashes, layout table row for `docs/` |
| `presentations/migrating_an_instance/from-clicks-to-code-jnuc2026.key` | Rebuilt by `npm run build:key` in the final task |

---

### Task 1: s01 - permissions come off during the migration, not after

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (constraint list in `#s01`, around line 831)

- [ ] **Step 1: Replace the constraint card**

Replace:

```html
        <li class="card">Post-migration, all create/update/delete operations happen through Terraform only.</li>
```

with:

```html
        <li class="card">GUI write access is removed resource type by resource type as the migration goes, not at the end - once a type is in Terraform, every create, update and delete for it goes through Terraform.</li>
```

- [ ] **Step 2: Screenshot `s01` and check the nine cards still clear the timeline strip**

Run the screenshot block from "How to verify a slide" with `s01`. Open the PNG. The bottom `slide-note` ("Staging was supposed to mirror production...") must sit above the timeline strip.

- [ ] **Step 3: Run the text lint** (expect no dash hits, count 23)

- [ ] **Step 4: Commit**

`AGENTS.md` is unaffected (it does not quote this constraint).

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html && git commit -m "Say when GUI write access came off on the constraints slide

Feedback: the constraint read as post-migration; write permissions were
pulled per resource type during the waves. AGENTS.md unaffected."
```

---

### Task 2: s03 - decisions only, no repeats of s01 (D2)

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (`#s01` constraint list ~line 830; whole `#s03` section lines 881-907)
- Modify: `AGENTS.md` (slide list row 4)

- [ ] **Step 1: Remove the monorepo line from s01's constraints** (it is a decision, and s03 keeps it)

Delete this line from `#s01`:

```html
        <li class="card">One shared source of truth for every team - resources are not split by org structure.</li>
```

- [ ] **Step 2: Replace the s03 section body**

Replace everything from `<section class="slide" id="s03"` through its closing `</section>` with:

```html
    <section class="slide" id="s03" aria-label="What we decided up front" data-speaker="Dafydd" data-when="2025-11">
      <h1 class="slide-title">What we decided up front</h1>
      <div class="obj-groups">
        <div class="card obj-group">
          <h2 class="obj-group-title">Governance</h2>
          <ul class="obj-list">
            <li><span class="obj-num">1</span><span>One monorepo is the single source of truth for every instance and every team - resources are not split by org structure.</span></li>
            <li><span class="obj-num">2</span><span>Engineers drop to read-only in Jamf Pro as each resource type migrates; only the Terraform machine identity keeps full CRUD.</span></li>
            <li><span class="obj-num">3</span><span>A break-glass account, held in PAM (Privileged Access Management).</span></li>
          </ul>
        </div>
        <div class="card obj-group">
          <h2 class="obj-group-title">Architecture and developer experience</h2>
          <ul class="obj-list">
            <li><span class="obj-num">4</span><span>One Terraform definition drives every instance.</span></li>
            <li><span class="obj-num">5</span><span>Secrets set once by humans in Vault, read by Terraform through data sources.</span></li>
            <li><span class="obj-num">6</span><span>Branching supports three environments on VCS triggers (one instance is CLI-triggered).</span></li>
            <li><span class="obj-num">7</span><span>A BAU change is a one-line edit to a parameter map, not hand-written HCL.</span></li>
          </ul>
        </div>
      </div>
      <p class="slide-note">The bank's rules are on the previous slide. These are the calls we made inside them.</p>
      <aside class="notes">
        <p>Everything on the last slide was imposed. Everything here was chosen - and the first choice, one repo for every team, is the one that gets challenged most.</p>
        <p>Objective 7 is aimed squarely at Mac engineers new to Terraform: the contribution bar is "edit a map", not "write HCL from scratch".</p>
      </aside>
    </section>
```

- [ ] **Step 3: Mirror the notes into presenter.json**

In `presenter.json`, the `s03` entry becomes:

```json
    {
      "id": "s03",
      "title": "What we decided up front",
      "timerSeconds": 60,
      "notes": [
        "Everything on the last slide was imposed. Everything here was chosen - and the first choice, one repo for every team, is the one that gets challenged most.",
        "Objective 7 is aimed squarely at Mac engineers new to Terraform: the contribution bar is \"edit a map\", not \"write HCL from scratch\"."
      ]
    },
```

- [ ] **Step 4: Update AGENTS.md slide list row 4**

Replace:

```
4. `s03` Migration objectives and design decisions - **Dafydd**
```

with:

```
4. `s03` What we decided up front (decisions only; the bank's constraints stay on s01) - **Dafydd**
```

- [ ] **Step 5: Screenshot `s01` and `s03`**

`s01` now has eight cards in a three-column grid (last row has two) - confirm nothing looks broken. `s03` has 3 + 4 items and a slide-note; confirm the note clears the strip.

- [ ] **Step 6: Run the text lint, then commit**

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json AGENTS.md && git commit -m "Split constraints from decisions across s01 and s03

s01 keeps what the bank imposed, s03 keeps what the team chose; the peer
review and Vault duplicates come off s03. Retitled to make the trio read
context, decisions, rejections."
```

---

### Task 3: s04 - correct the workspace-size figures

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (`#s04` first `reject-why` ~line 918; notes ~936-939)
- Modify: `presentations/migrating_an_instance/presenter.json` (`s04` notes)
- Modify: `AGENTS.md` ("Rejected up front" settled fact ~line 279)

- [ ] **Step 1: Fix the rationale text**

Replace:

```html
          <p class="reject-why">Blast radius and plan execution time. Guidance suggests roughly 500 resources per workspace; the estate holds 1,500+. At ~5,000, things break down.</p>
```

with:

```html
          <p class="reject-why">Blast radius and plan time. The guidance is around 500 resources per workspace, with a maximum of 5,000 - and the estate holds 1,500+.</p>
```

- [ ] **Step 2: Add the speaker cue to the notes**

Replace the `#s04` aside with:

```html
      <aside class="notes">
        <p>A single workspace felt like the obvious starting point. Once the scale and the blast radius were clear, it stopped being attractive.</p>
        <p>Expect pushback on "not everything in Terraform" - defend it: troubleshooting must not require a pull request.</p>
        <p>Tease the closing line: two more ideas got dropped later, and they show up where they happened in the story.</p>
      </aside>
```

and set the `s04` `notes` array in `presenter.json` to the same three strings (escape the inner double quotes as `\"`).

- [ ] **Step 3: Fix the settled fact in AGENTS.md**

Replace:

```
- **Rejected up front:** single workspace (blast radius / plan time, 500-1,500-5,000
  figures); per-team modules (internal approval complexity - expansion TODO); managing
  everything (static group membership unmanaged to protect support).
```

with:

```
- **Rejected up front:** single workspace (blast radius / plan time: guidance is ~500
  resources per workspace, the maximum is 5,000, the estate holds 1,500+ - corrected Aug 2026,
  the old "at 5,000 things break down" line was wrong); per-team modules (internal approval
  complexity - expansion TODO); managing everything (static group membership unmanaged to
  protect support).
```

- [ ] **Step 4: Screenshot `s04`, run the text lint, commit**

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json AGENTS.md && git commit -m "Correct the workspace sizing figures on the rejected-ideas slide

500 is the recommendation and 5,000 the maximum; the 'things break down'
line was not right. Adds the single-workspace speaker cue."
```

---

### Task 4: s05 - initial choice, corrected option text, plainer control card

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (`#s05` lines 942-971)
- Modify: `presentations/migrating_an_instance/presenter.json` (`s05` notes)

- [ ] **Step 1: Rewrite the dimmed option card**

Replace:

```html
        <div class="card option option-dimmed">
          <span class="option-label">Option</span>
          <h2 class="option-title">Staging → Production</h2>
          <p>Two divergent sets of configuration to import - and the drifted one gets validated first.</p>
        </div>
```

with:

```html
        <div class="card option option-dimmed">
          <span class="option-label">Initial choice</span>
          <h2 class="option-title">Staging → Production</h2>
          <p>Either all of staging in one go, or each resource type across every instance at once. Both start by codifying the drifted configuration.</p>
        </div>
```

- [ ] **Step 2: Rewrite the control card**

Replace:

```html
        <p><strong>The control that made it safe:</strong> the Terraform API client held read-only scopes. Importing only reads - so state was built with no surface to change the server. Write access was widened only once imports were stable with no recurring diff. Joseph and Gordon held those keys.</p>
```

with:

```html
        <p><strong>What made it safe:</strong> the API client Terraform used only had read scopes while we imported. An import reads from Jamf Pro and writes to state, nothing else - so nothing could change the server, even by mistake. Write scopes went on once the imports were stable and plans came back with no diff. Joseph and Gordon held those credentials.</p>
```

- [ ] **Step 3: Rewrite the notes** (the instance-by-instance line moves here from `s10`)

Replace the `#s05` aside with:

```html
      <aside class="notes">
        <p>The instance-by-instance route was the first thinking: all of staging first, or one resource type across every instance. We went production first, one resource type at a time - counterintuitive on purpose.</p>
        <p>Importing is read-then-manage. With a read-only API client there is no write surface, so prod-first is safer than it sounds. Write scopes were only widened once imports were stable at zero diff.</p>
      </aside>
```

Set the `s05` `notes` in `presenter.json` to those two strings.

- [ ] **Step 4: Screenshot `s05`, run the text lint, commit**

The control card is a little longer; confirm it clears the strip. `AGENTS.md` unaffected (the prod-first fact is unchanged).

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json && git commit -m "Reword the instance-order slide

The dimmed card is now the initial choice with the two ways it could
have gone; the control card says plainly why read-only scopes made
prod-first safe. AGENTS.md unaffected."
```

---

### Task 5: s07 - clarify the prep checklist

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (`#s07` lines 973-987)
- Modify: `presentations/migrating_an_instance/presenter.json` (`s07` notes)

Facts: every item is already on the slide; "Terraform Cloud" becomes "HCP Terraform" and "the secrets manager" becomes "Vault" because that is what `s01` and `s03` call them.

- [ ] **Step 1: Replace the checklist**

Replace the `<ul class="checklist">...</ul>` in `#s07` with:

```html
      <ul class="checklist">
        <li><span class="check" aria-hidden="true"></span><span>Tidy up first. <code class="inline">PRUNE</code> exported every unused resource to JSON, then <code class="inline">jamf-resource-deleter</code> removed them - each one backed up to JSON before it went, with a restore path if it was needed back.</span></li>
        <li><span class="check" aria-hidden="true"></span><span>Check every API client: credentials valid, scopes complete.</span></li>
        <li><span class="check" aria-hidden="true"></span><span>Check the Jamf Pro version meets the provider's minimum.</span></li>
        <li><span class="check" aria-hidden="true"></span><span>Test the connection from HCP Terraform to the instance end to end, and confirm each client's credentials are read correctly.</span></li>
        <li><span class="check" aria-hidden="true"></span><span>Store every instance's API client credentials in Vault.</span></li>
        <li><span class="check" aria-hidden="true"></span><span>Split the estate into resource-type sections, so the migration can go one section at a time.</span></li>
      </ul>
```

- [ ] **Step 2: Notes**

Replace the `#s07` aside with:

```html
      <aside class="notes">
        <p>Six things, in the order they were done. The tidy-up mattered most - importing dead config would have codified years of cruft. PRUNE found the unused resources; jamf-resource-deleter removed them safely, with a JSON backup and restore path in case anything was needed back.</p>
        <p>The last item is the bridge to the sequencing slide: the sections are the resource types.</p>
      </aside>
```

Set the `s07` `notes` in `presenter.json` to those two strings.

- [ ] **Step 3: Screenshot `s07`, run the text lint, commit**

`AGENTS.md` unaffected (row 7 wording still applies).

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json && git commit -m "Clarify the instance prep checklist

Each item is now one plain action; the tooling names match the rest of
the deck (HCP Terraform, Vault). AGENTS.md unaffected."
```

---

### Task 6: s-singletons - drop the repeated "import first" sentence

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (`#s-singletons` lines 994-998)

- [ ] **Step 1: Replace the intro and control card**

Replace:

```html
          <p>Settings panes are single-instance resources - there's only ever one. Import stayed the default; apply was the fallback.</p>
          <div class="card control-note">
            <p><strong>Don't skip import if you can.</strong> Apply was only the fallback when no import statement existed.</p>
          </div>
```

with:

```html
          <p>Settings panes only ever have one instance, so they went first.</p>
          <div class="card control-note">
            <p><strong>Import where the provider supports it.</strong> Where it doesn't, write the HCL to match what the UI shows and apply it - the create is a no-op and the resource lands in state.</p>
          </div>
```

- [ ] **Step 2: Screenshot `s-singletons`, run the text lint, commit**

Notes and `AGENTS.md` are unchanged.

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html && git commit -m "Tighten the singletons slide copy

One sentence on why they went first, one on the import-or-apply rule.
AGENTS.md unaffected."
```

---

### Task 7: s-sentinel - broaden to the platform (D1)

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (`#s-sentinel` lines 1027-1055)
- Modify: `presentations/migrating_an_instance/presenter.json` (`s-sentinel` title + notes)
- Modify: `AGENTS.md` (slide list row 9)

Facts used: HCP Terraform on private runners, Sentinel on every run, no CLI outside development (all on `s01`); the import ban exists because Terraform runs the bank's public cloud (settled fact).

- [ ] **Step 1: Retitle and reframe the lead**

Replace:

```html
    <section class="slide" id="s-sentinel" aria-label="Guardrails you don't own" data-speaker="Gordon" data-when="2025-11:2026-01">
      <h1 class="slide-title">Guardrails you don't own</h1>
      <p class="lead">At LBG, every Terraform run - across the bank's entire public cloud estate - passes through Sentinel policy checks before it can apply. One of those policies bans <code class="inline">import</code> blocks outright, because importing lets a workspace adopt resources someone else already manages.</p>
```

with:

```html
    <section class="slide" id="s-sentinel" aria-label="Infrastructure challenges" data-speaker="Gordon" data-when="2025-11:2026-01">
      <h1 class="slide-title">Infrastructure challenges</h1>
      <p class="lead">At LBG, Terraform is a shared platform: HCP Terraform on private runners, Sentinel policy checks on every run, no CLI outside development. Its rules were written for the bank's public cloud, not for a Jamf Pro migration - and one of them nearly stopped it. A Sentinel policy bans <code class="inline">import</code> blocks outright, because importing lets a workspace adopt resources someone else already manages.</p>
```

The three gate cards below the lead stay exactly as they are.

- [ ] **Step 2: Notes**

Replace the `#s-sentinel` aside with:

```html
      <aside class="notes">
        <p>Frame it as the platform, not Sentinel in particular - the constraints on slide two are the same platform. Sentinel is the worked example because it is the one that nearly stopped the migration.</p>
        <p>Why the ban exists: Terraform runs the bank's whole public cloud - import blocks would let one workspace adopt someone else's resources. The policy is right; it just did not fit a sole-actor migration.</p>
        <p>Each import window needed a fresh time-bound exception until the standing exception was granted.</p>
      </aside>
```

In `presenter.json`, set the `s-sentinel` entry's `title` to `"Infrastructure challenges"` and `notes` to those three strings.

- [ ] **Step 3: AGENTS.md row 9**

Replace:

```
9. `s-sentinel` Guardrails you don't own (blocked -> per-window exceptions -> standing exception) - **Gordon**
```

with:

```
9. `s-sentinel` Infrastructure challenges (the shared Terraform platform, with the Sentinel import ban as the worked example: blocked -> per-window exceptions -> standing exception) - **Gordon**
```

- [ ] **Step 4: Screenshot `s-sentinel`** - the lead is longer; the three cards must still clear the strip. If they do not, shorten the lead by dropping the sentence "Its rules were written for the bank's public cloud, not for a Jamf Pro migration - and one of them nearly stopped it." and re-check.

- [ ] **Step 5: Run the text lint, commit**

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json AGENTS.md && git commit -m "Reframe the Sentinel slide as the shared platform

Titled Infrastructure challenges; the platform is the subject and the
import ban is the worked example, so the slide fits a journey talk."
```

---

### Task 8: s10 - say what "end to end" means

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (`#s10` intro ~line 1060; notes ~1091-1094)
- Modify: `presentations/migrating_an_instance/presenter.json` (`s10` notes)

- [ ] **Step 1: Rewrite the intro**

Replace:

```html
      <p class="s10-intro">One resource type at a time, end to end in production - not one instance at a time. The order came from the matrix: a group-built spreadsheet of every resource type and its dependencies.</p>
```

with:

```html
      <p class="s10-intro">One resource type at a time, taken all the way through in production - imported, validated, write access pulled - before the next type started. The order came from the matrix: a spreadsheet the team built of every resource type and what it depends on.</p>
```

The per-band examples on the diagram (`client check-in · inventory collection · activation code` and so on) are already present from `bdf25db`; confirm they are and leave them.

- [ ] **Step 2: Notes** - drop the instance-by-instance line (now on `s05`)

Replace the `#s10` aside with:

```html
      <aside class="notes">
        <p>All the way through means each type was imported, validated and had its UI write access pulled before the next type started - no half-managed types in flight.</p>
        <p>The matrix is a spreadsheet the team built together. Risk scales with dependency fan-in: singletons carry none, scripts and categories and departments stand alone, smart groups and advanced searches and extension attributes sit on top of those, and profiles and policies sit on top of everything - so they close the migration.</p>
      </aside>
```

Set the `s10` `notes` in `presenter.json` to those two strings.

- [ ] **Step 3: Screenshot `s10`, run the text lint, commit**

`AGENTS.md` unaffected.

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json && git commit -m "Spell out what end to end means on the sequencing slide

Drops the 'not one instance at a time' aside - that comparison now
lives on the instance-order slide. AGENTS.md unaffected."
```

---

### Task 9: Fold the validation gates into the wave workflow, delete s14

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (CSS after the S08 block ~line 625; `#s08` lines 1097-1138; delete `#s14` lines 1263-1296)
- Modify: `presentations/migrating_an_instance/presenter.json` (`s08` notes + timer; remove `s14`)
- Modify: `AGENTS.md` (slide list; folded-slides note; timeline check note)

The terminal panel and the three checks move from `s14` onto `s08` under the stepper. Gate 4 ("remove UI write permissions") is reconciled with step 3 (the freeze revokes them at wave start): after the checks pass, they stay off.

- [ ] **Step 1: Add the CSS**

After the existing block ending `.step .todo { white-space: normal; align-self: flex-start; }`, add:

```css
/* validation block under the stepper - terminal left, the three checks right */
.s08-validate {
  margin-top: var(--sp-4);
  display: grid;
  grid-template-columns: 820px 1fr;
  gap: var(--sp-4);
  align-items: start;
}
.s08-validate .terminal { margin: 0; max-width: none; }
.s08-checks { gap: var(--sp-2); font-size: var(--fs-caption); }
```

Also change the CSS section comment `/* ============================ S14 / gate cards ============================ */` to `/* ============================ gate cards + terminal (s08, s-sentinel, s-staging) ============================ */`.

- [ ] **Step 2: Rewrite step 5 and add the validation block to s08**

Replace:

```html
        <li class="card step">
          <span class="step-num">5</span>
          <p>Validate the import succeeded.</p>
        </li>
```

with:

```html
        <li class="card step">
          <span class="step-num">5</span>
          <p>Validate the import - the three checks below.</p>
        </li>
```

Then, directly after the stepper's closing `</ol>` and before `<aside class="notes">` in `#s08`, insert:

```html
      <div class="s08-validate">
        <div class="card terminal">
          <div class="term-head" aria-hidden="true">
            <span class="term-dot"></span><span class="term-dot"></span><span class="term-dot"></span>
          </div>
          <pre class="term-body"><span class="muted">$ terraform plan</span>

<span class="term-ok">No changes. Your infrastructure matches the configuration.</span></pre>
        </div>
        <ul class="dash-bullets s08-checks">
          <li><code class="inline">terraform plan</code> comes back with no changes.</li>
          <li>State lives in HCP and cannot be inspected locally, so Copilot CLI read it back to confirm every resource exists with the right dependencies.</li>
          <li>Sweep for orphans - anything on the instance that is not in the HCL.</li>
          <li>Only when all three pass do the write permissions pulled in step 3 stay off for good.</li>
        </ul>
      </div>
```

- [ ] **Step 3: s08 notes**

Replace the `#s08` aside with:

```html
      <aside class="notes">
        <p>Step 3 is the one people skip and regret - revoking write permissions makes the freeze real rather than polite.</p>
        <p>Validation is three checks: a zero-diff plan, a Copilot CLI pass over state confirming every resource and its dependencies (HCP holds the state, so nothing is locally inspectable), and a sweep for orphans outside the HCL. Only then do the permissions stay off - that is the point of no return, and the point of the whole exercise.</p>
        <p>Bulk waves ran December into January.</p>
      </aside>
```

In `presenter.json`: set `s08` `notes` to those three strings and its `timerSeconds` to `90`; delete the whole `s14` entry.

- [ ] **Step 4: Delete the s14 section**

Remove everything from `<!-- ============================ S14 - Validating a migration ============================ -->` through the `</section>` that closes `id="s14"`, including the blank line after it.

- [ ] **Step 5: AGENTS.md**

In "Current slide order": delete row `15. s14 Validating a migration - **Joseph**` (renumber below in Task 17, which rewrites the whole list). Change row 11 to:

```
11. `s08` Migration wave workflow (Dec 2025 - Jan 2026 bulk; carries the zero-diff terminal and the three validation checks folded in from the old s14) - **Dafydd**
```

Append to the "Former slides folded away" paragraph: `s14` (validation gates and terminal, into `s08` - Aug 2026 feedback).

- [ ] **Step 6: Screenshot `s08`** - the stepper cards stretch to the tallest card; the validation grid below must clear the timeline strip. If it does not, reduce `.s08-checks` to three bullets by merging bullets 3 and 4: "Sweep for orphans outside the HCL - and only when all three pass do the write permissions pulled in step 3 stay off for good."

- [ ] **Step 7: Run the text lint** (count must now be 22) and commit

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json AGENTS.md && git commit -m "Fold the validation gates into the wave workflow

The three checks and the zero-diff terminal sit under the stepper on
s08; the standalone validation slide is gone. Gate 4 is reconciled with
step 3: the permissions pulled for the freeze stay off once the checks
pass."
```

---

### Task 10: New slide - Workspace architecture (D3 for the speaker)

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (CSS after the S10 block ~line 634; new section inserted where `s14` was, between `#s13` and `#s-staging`)
- Modify: `presentations/migrating_an_instance/presenter.json` (new entry after `s13`)
- Modify: `AGENTS.md` (slide list; reader-mode list; settled facts note)

Facts used (all settled in `AGENTS.md`): one GitHub monorepo; VCS-triggered runs; HCP Terraform, remote state, private runners; Sentinel on every run; Vault via data sources; three workspaces per instance (`iam` / `profiles_policies` / `root`) for `lbgstaging` and `lbgbusiness`, and it has always been three; plans 4-6 minutes; Sandbox has no workspace; DevTest came later with one CLI workspace. `data-when` matches `s13` so the timeline renders static (the story has not moved).

- [ ] **Step 1: CSS**

After `.s10-svg .band-5 { ... }` add:

```css
/* ============================ s-workspaces ============================ */
.s-ws-intro { max-width: 1600px; margin-bottom: var(--sp-3); }
.s-ws-svg { width: 100%; height: auto; display: block; }
.s-ws-svg .inst { fill: color-mix(in srgb, var(--c-accent) 9%, var(--c-surface)); }
```

- [ ] **Step 2: Insert the section** between the `</section>` closing `#s13` and the `<!-- ============================ Rebuilding staging` comment:

```html
    <!-- ============================ Workspace architecture ============================ -->
    <section class="slide" id="s-workspaces" aria-label="Workspace architecture" data-speaker="Joseph" data-when="2026-02:2026-03">
      <h1 class="slide-title">Workspace architecture</h1>
      <p class="s-ws-intro">Three workspaces per instance, one per root, so no single run can touch the whole estate. It has been three per instance for staging and production from the start.</p>
      <svg class="s-ws-svg" viewBox="0 0 1728 620" aria-label="One GitHub monorepo triggers HCP Terraform runs; three workspaces per instance each apply to one Jamf Pro instance through private runners, with secrets from Vault and Sentinel checks on every run">
        <defs>
          <marker id="s-ws-ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0 0 L10 5 L0 10 z" fill="var(--c-line)"/>
          </marker>
        </defs>
        <rect class="dg-box" x="1" y="200" width="260" height="140" rx="12"/>
        <text class="dg-label" x="131" y="262" text-anchor="middle">GitHub</text>
        <text class="dg-eg" x="131" y="298" text-anchor="middle">one monorepo</text>
        <line class="dg-edge" x1="261" y1="270" x2="434" y2="270" marker-end="url(#s-ws-ah)"/>
        <text class="dg-eg" x="348" y="252" text-anchor="middle">VCS-triggered</text>
        <rect class="dg-box" x="1" y="420" width="260" height="140" rx="12"/>
        <text class="dg-label" x="131" y="482" text-anchor="middle">Vault</text>
        <text class="dg-eg" x="131" y="518" text-anchor="middle">secrets via data sources</text>
        <line class="dg-edge" x1="261" y1="490" x2="434" y2="490" marker-end="url(#s-ws-ah)"/>
        <rect class="dg-box" x="440" y="1" width="850" height="580" rx="12"/>
        <text class="dg-label" x="470" y="48">HCP Terraform</text>
        <text class="dg-eg" x="1260" y="48" text-anchor="end">Sentinel policy checks on every run</text>
        <rect class="dg-box inst" x="470" y="80" width="800" height="210" rx="12"/>
        <text class="dg-eg" x="490" y="116">lbgbusiness - production</text>
        <rect class="dg-box" x="490" y="140" width="240" height="120" rx="12"/>
        <text class="dg-label" x="610" y="204" text-anchor="middle">iam</text>
        <text class="dg-eg" x="610" y="240" text-anchor="middle">workspace</text>
        <rect class="dg-box" x="750" y="140" width="240" height="120" rx="12"/>
        <text class="dg-label" x="870" y="204" text-anchor="middle">profiles_policies</text>
        <text class="dg-eg" x="870" y="240" text-anchor="middle">workspace</text>
        <rect class="dg-box" x="1010" y="140" width="240" height="120" rx="12"/>
        <text class="dg-label" x="1130" y="204" text-anchor="middle">root</text>
        <text class="dg-eg" x="1130" y="240" text-anchor="middle">workspace</text>
        <rect class="dg-box inst" x="470" y="310" width="800" height="210" rx="12"/>
        <text class="dg-eg" x="490" y="346">lbgstaging - staging</text>
        <rect class="dg-box" x="490" y="370" width="240" height="120" rx="12"/>
        <text class="dg-label" x="610" y="434" text-anchor="middle">iam</text>
        <text class="dg-eg" x="610" y="470" text-anchor="middle">workspace</text>
        <rect class="dg-box" x="750" y="370" width="240" height="120" rx="12"/>
        <text class="dg-label" x="870" y="434" text-anchor="middle">profiles_policies</text>
        <text class="dg-eg" x="870" y="470" text-anchor="middle">workspace</text>
        <rect class="dg-box" x="1010" y="370" width="240" height="120" rx="12"/>
        <text class="dg-label" x="1130" y="434" text-anchor="middle">root</text>
        <text class="dg-eg" x="1130" y="470" text-anchor="middle">workspace</text>
        <text class="dg-eg" x="470" y="560">state in HCP · plans and applies on private runners inside the bank · plans in 4-6 minutes</text>
        <line class="dg-edge" x1="1270" y1="185" x2="1434" y2="185" marker-end="url(#s-ws-ah)"/>
        <rect class="dg-box" x="1440" y="125" width="287" height="120" rx="12"/>
        <text class="dg-label" x="1583" y="180" text-anchor="middle">Jamf Pro</text>
        <text class="dg-eg" x="1583" y="216" text-anchor="middle">production</text>
        <line class="dg-edge" x1="1270" y1="415" x2="1434" y2="415" marker-end="url(#s-ws-ah)"/>
        <rect class="dg-box" x="1440" y="355" width="287" height="120" rx="12"/>
        <text class="dg-label" x="1583" y="410" text-anchor="middle">Jamf Pro</text>
        <text class="dg-eg" x="1583" y="446" text-anchor="middle">staging</text>
        <text class="dg-eg" x="1" y="612">Sandbox has no workspace - local dev only, from the CLI. DevTest came later, with a single CLI-triggered workspace.</text>
      </svg>
      <details class="reader-extra">
        <summary>More detail</summary>
        <div class="detail-body">
          <p>Each root directory in the repo is wired to exactly one HCP Terraform workspace, so a change under <code class="inline">prod/lbgbusiness/iam</code> can only ever plan and apply against production's IAM resources. No CLI outside development means every staging and production run is VCS-triggered, executed on private runners inside the bank's network, and checked by Sentinel before it can apply.</p>
        </div>
      </details>
      <aside class="notes">
        <p>Three workspaces per instance is the blast radius control - guidance says around 500 resources per workspace and the estate holds 1,500+. It has been three per instance for staging and production from the start; the module pivot later changed what each root contains, not the workspaces.</p>
        <p>Every run is remote: VCS-triggered, on private runners, Sentinel-checked, secrets from Vault. No CLI outside development - which is why the import ban bit so hard.</p>
      </aside>
    </section>

```

- [ ] **Step 3: presenter.json** - insert after the `s13` entry:

```json
    {
      "id": "s-workspaces",
      "title": "Workspace architecture",
      "timerSeconds": 60,
      "notes": [
        "Three workspaces per instance is the blast radius control - guidance says around 500 resources per workspace and the estate holds 1,500+. It has been three per instance for staging and production from the start; the module pivot later changed what each root contains, not the workspaces.",
        "Every run is remote: VCS-triggered, on private runners, Sentinel-checked, secrets from Vault. No CLI outside development - which is why the import ban bit so hard."
      ]
    },
```

- [ ] **Step 4: AGENTS.md**

- Slide list: add, between the `s13` and `s-staging` rows, `15. s-workspaces Workspace architecture (GitHub -> HCP Terraform -> six workspaces -> Jamf Pro; Vault and Sentinel; same range as s13 so the timeline renders static) - **Joseph**`.
- Reader mode paragraph: add `s-workspaces` to the list `(currently s01, s05, s-singletons, s-sentinel, s12, s15b, s-staging, s-today)`.
- Settled facts, "Workspaces" bullet: append `Shown on s-workspaces; it has always been 3 per instance (SQ10), which is why the slide sits before the module pivot.`
- Verification section, timeline grey-state line: append `#s13 and #s-workspaces share a range too - s-workspaces must render grey and s-staging accent.`

- [ ] **Step 5: Screenshot `s-workspaces`, `?reader=1#s-workspaces`, and `s-staging`**

Check: no text overflows a box (the `profiles_policies` labels are the tight ones - if a label breaks out of its 240px box, widen all six boxes to 250 and shift the second and third columns by +10 and +20); the diagram clears the strip; the timeline cells render in the muted static state on `s-workspaces` and accent on `s-staging`; the "More detail" chip in reader mode sits above the strip.

- [ ] **Step 6: Run the text lint** (count 22) and commit

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json AGENTS.md && git commit -m "Add the workspace architecture slide

Replaces the validation slide's slot: one repo, HCP Terraform, three
workspaces per instance, private runners, Vault and Sentinel, drawn with
the deck's SVG primitives. Facts are the settled ones in AGENTS.md."
```

---

### Task 11: s12 - big helper output vs the compressed local

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (tokens ~line 70; CSS after `.code-narrow` ~line 280; `#s12` lines 1185-1235)
- Modify: `presentations/migrating_an_instance/presenter.json` (`s12` notes)
- Modify: `AGENTS.md` ("The loop" settled fact)

The point of the slide changes: the helpers emitted large JSON-shaped locals with every attribute spelled out, most of them defaults repeated per resource; the passes compressed the local to what varies and moved the defaults into the resource block. `generate-config-out` was never used (its rejection stays on `s11`). The example keeps Dafydd's sanitised placeholder naming ("Script 1", "Category 1").

- [ ] **Step 1: Verify the `jamfpro_script` attribute names before using them**

```sh
curl -sL "https://registry.terraform.io/v1/providers/deploymenttheory/jamfpro" >/dev/null && echo "registry reachable" ; open "https://registry.terraform.io/providers/deploymenttheory/jamfpro/latest/docs/resources/script"
```

Confirm `name`, `script_contents`, `category_id`, `info`, `notes`, `os_requirements`, `priority` and `parameter4` are attributes of `jamfpro_script`. If any is not, swap it for one that is - the example must not show an attribute the provider does not have.

- [ ] **Step 2: Tokens and CSS**

In `:root`, after `--fs-chip: 18px;` add:

```css
  --fs-code-zoom: 14px;     /* s12 "zoomed out" panel - shape over legibility, on purpose */
  --lh-code-zoom: 1.25;
```

After `.code-narrow { ... }` add:

```css
.code-zoom { font-size: var(--fs-code-zoom); line-height: var(--lh-code-zoom); }
```

- [ ] **Step 3: Replace the compare block, takeaway and note**

Replace everything from `<div class="compare">` through `<p class="slide-note">The refinement passes, repeated until zero diff ... through February and March.</p>` in `#s12` with:

```html
      <div class="compare">
        <div class="panel">
          <h2 class="panel-title">Straight out of the helper</h2>
          <pre class="code code-zoom"><span class="tk-kw">locals</span> {
  scripts = {
    <span class="tk-str">"Script 1"</span> = {
      category_id     = <span class="tk-num">9</span>
      info            = <span class="tk-str">""</span>
      notes           = <span class="tk-str">""</span>
      os_requirements = <span class="tk-str">""</span>
      priority        = <span class="tk-str">"AFTER"</span>
      parameter4      = <span class="tk-str">""</span>
      script_contents = <span class="tk-str">"#!/bin/bash ..."</span>
    }
    <span class="tk-str">"Script 2"</span> = {
      category_id     = <span class="tk-num">9</span>
      info            = <span class="tk-str">""</span>
      notes           = <span class="tk-str">""</span>
      os_requirements = <span class="tk-str">""</span>
      priority        = <span class="tk-str">"AFTER"</span>
      parameter4      = <span class="tk-str">""</span>
      script_contents = <span class="tk-str">"#!/bin/bash ..."</span>
    }
    <span class="tk-str">"Script 3"</span> = {
      category_id     = <span class="tk-num">12</span>
      info            = <span class="tk-str">""</span>
      notes           = <span class="tk-str">""</span>
      os_requirements = <span class="tk-str">""</span>
      priority        = <span class="tk-str">"AFTER"</span>
      parameter4      = <span class="tk-str">""</span>
      script_contents = <span class="tk-str">"#!/bin/bash ..."</span>
    }
    <span class="tk-cm"># ... every script, every attribute, mostly defaults</span>
  }
}</pre>
        </div>
        <div class="panel panel-ours">
          <h2 class="panel-title">After the passes</h2>
          <pre class="code"><span class="tk-kw">locals</span> {
  scripts = {
    <span class="tk-str">"Script 1"</span> = { category = <span class="tk-str">"Category 1"</span>, file = <span class="tk-str">"script_1.sh"</span> }
    <span class="tk-str">"Script 2"</span> = { category = <span class="tk-str">"Category 1"</span>, file = <span class="tk-str">"script_2.sh"</span> }
    <span class="tk-str">"Script 3"</span> = { category = <span class="tk-str">"Category 2"</span>, file = <span class="tk-str">"script_3.sh"</span> }
    <span class="tk-cm"># BAU change = one line here</span>
  }
}

<span class="tk-kw">resource</span> <span class="tk-str">"jamfpro_script"</span> <span class="tk-str">"managed"</span> {
  <span class="tk-kw">for_each</span>        = local.scripts
  name            = each.key
  category_id     = local.category_ids[each.value.category]
  script_contents = file(<span class="tk-str">"scripts/${each.value.file}"</span>)
  priority        = <span class="tk-str">"AFTER"</span>   <span class="tk-cm"># defaults set once, here</span>
}</pre>
        </div>
      </div>
      <p class="takeaway">Same resources, a fraction of the HCL. Adding script two hundred is a one-line diff, and reviews read the data, not the boilerplate.</p>
```

(The old `slide-note` about the refinement passes is deliberately gone from the slide; it lives in the notes.)

- [ ] **Step 4: Reader-extra and notes**

Replace the `#s12` reader-extra body paragraph with:

```html
          <p>The helper scripts emitted every attribute of every resource as a Terraform local - a JSON-shaped map where most values were provider defaults repeated hundreds of times. The refinement passes compressed each map down to what actually varies per resource, moved the defaults into the single resource block, stripped duplicates and replaced raw IDs with named lookups from locals built off the managed resources. One block per type means provider changes are fixed in one place and the HCL does not grow as the estate does.</p>
```

Replace the `#s12` aside with:

```html
      <aside class="notes">
        <p>The technical centrepiece. The helpers gave us huge JSON-shaped locals - every attribute for every resource, most of them defaults repeated over and over. We never used generate-config-out; we compressed the locals to what varies and put the defaults in the resource block, once.</p>
        <p>Division of labour: Gordon imported verbosely, Joseph refined in passes - dedup, name the IDs, share the locals - with a zero-diff plan after every pass, through February and March.</p>
      </aside>
```

Set the `s12` `notes` in `presenter.json` to those two strings.

- [ ] **Step 5: AGENTS.md** - in the "The loop" settled fact, after `JamfPy script emits a structured map (duplicates and all)` add `- every attribute, defaults included, so the raw locals were huge`, and after `refinement passes (dedup, raw IDs -> named locals like ..., shared locals)` add `, defaults moved into the resource block; generate-config-out was never used`.

- [ ] **Step 6: Screenshot `s12` and `?reader=1#s12`**

Both panels must end above the takeaway and the takeaway above the strip. If the zoomed panel is taller than the right panel by more than a line or two, drop the `"Script 3"` entry from it (the shape reads the same with two).

- [ ] **Step 7: Run the text lint, commit**

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json AGENTS.md && git commit -m "Show the helper output against the compressed local on s12

The comparison was never against generate-config-out. Left panel is the
raw helper local, zoomed out; right is the compact map with defaults in
the resource block."
```

---

### Task 12: s13 - policies were the only exception

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (CSS after `.exceptions { ... }` ~line 657; `#s13` lines 1237-1261)
- Modify: `presentations/migrating_an_instance/presenter.json` (`s13` title + notes)
- Modify: `AGENTS.md` (slide list row; "for_each exceptions" settled fact)

- [ ] **Step 1: CSS** - after `.exceptions { display: grid; ... }` add:

```css
.exceptions-1 { grid-template-columns: 1fr; max-width: 980px; }
```

- [ ] **Step 2: Replace the section**

Replace the whole `#s13` section with:

```html
    <section class="slide" id="s13" aria-label="The for_each exception" data-speaker="Joseph" data-when="2026-02:2026-03">
      <h1 class="slide-title">The <span class="mono">for_each</span> exception</h1>
      <p class="lead">The parameter-map pattern is a default, not dogma. One resource type got plain HCL.</p>
      <div class="exceptions exceptions-1">
        <div class="card exception">
          <h2 class="exception-title">Policies</h2>
          <ul class="exception-conditions">
            <li>Comparatively few of them</li>
            <li>Each one is huge</li>
            <li>Each one is unique</li>
          </ul>
        </div>
      </div>
      <p class="s13-close">Low count, huge payloads, nothing in common - a map of policies would be harder to read than the policies themselves.</p>
      <aside class="notes">
        <p>The honesty slide. Policies were the only exception: there are not many of them, each is enormous, and no two look alike, so a map would have been harder to read than the HCL. Everything else stayed on the pattern.</p>
      </aside>
    </section>
```

- [ ] **Step 3: presenter.json** - `s13` entry: `title` `"The for_each exception"`, `notes` the one string above.

- [ ] **Step 4: AGENTS.md**

- Slide list row: `s13 The for_each exception (policies only) - **Joseph**`.
- Settled fact: replace `- **for_each exceptions:** policies and dock items (payload complexity, readability).` with `- **for_each exception:** policies only - comparatively low count, huge, unique (Aug 2026 feedback; dock items were listed earlier in error).`

- [ ] **Step 5: Screenshot `s13`, run the text lint, commit**

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json AGENTS.md && git commit -m "Policies were the only for_each exception

Drops dock items from the slide and the settled facts; the three
reasons are low count, size and uniqueness."
```

---

### Task 13: s-staging - lose "years of drift"

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (`#s-staging` lead ~line 1301; notes ~1325-1329)
- Modify: `presentations/migrating_an_instance/presenter.json` (`s-staging` notes)

Already true on the slide and needing no change: gate 1 keeps "APNS, cloud identity provider"; the slide sits before the pivot. Confirm both, then:

- [ ] **Step 1: Lead**

Replace:

```html
      <p class="lead">Production was fully code. Staging was still years of drift - importing that drift would only have enshrined it. So it was not imported at all.</p>
```

with:

```html
      <p class="lead">Production was fully code. Staging had drifted from it, with no history to say how or why - importing it would only have made that drift permanent. So it was not imported at all.</p>
```

- [ ] **Step 2: Notes**

Replace the `#s-staging` aside with:

```html
      <aside class="notes">
        <p>The highlight - slow down here.</p>
        <p>Importing staging would have made the drift permanent. So: wipe, keeping only APNS and the cloud IdP; point production's configuration at it; iterate through the errors until clean. Parity is now inherited, not claimed.</p>
        <p>Set up the next two slides: rebuilding staging is what exposed the repo problem. A real staging environment is only useful if you can deploy to it first, and back then a change there mirrored straight to production.</p>
      </aside>
```

Set the `s-staging` `notes` in `presenter.json` to those three strings (the current entry has two and is out of date).

- [ ] **Step 3: Screenshot `s-staging`, run the text lint, commit**

`AGENTS.md` unaffected (the "Staging migration" fact does not use the phrase).

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json && git commit -m "Describe staging's drift accurately on the rebuild slide

'Years of drift' overstated it; the point is there was no history to
reconcile. AGENTS.md unaffected."
```

---

### Task 14: s-pivot - plainer closing statement

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (`#s-pivot` statement ~line 1344)

- [ ] **Step 1: Replace the statement** (keep the TODO chip - Joseph still owes the real conditional)

Replace:

```html
      <p class="statement">It got out of hand. The pivot: shared modules own the configuration; thin per-instance roots own only what genuinely differs.
        <span class="todo">TODO: real conditional example</span></p>
```

with:

```html
      <p class="statement">Before long every instance-specific decision hung off a hostname. So we split the repo: the configuration moved into shared modules, and each instance got a thin root holding only what is genuinely different about it.
        <span class="todo">TODO: real conditional example</span></p>
```

- [ ] **Step 2: Screenshot `s-pivot`** - the statement is at `--fs-h2` and now longer; it must clear the strip. If not, drop "about it".

- [ ] **Step 3: Run the text lint, commit**

Notes and `AGENTS.md` unchanged.

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html && git commit -m "Reword the growing-pains statement

Plain sentence on what the split was. AGENTS.md unaffected."
```

---

### Task 15: s15b - modules only, workspaces already covered

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (`#s15b` bullets ~1370-1377; notes ~1384-1387)
- Modify: `presentations/migrating_an_instance/presenter.json` (`s15b` notes)

- [ ] **Step 1: Replace the workspace bullet and drop the slide-note**

Replace:

```html
          <li>Every root maps one-to-one to an HCP Terraform workspace - three per instance, bounding the blast radius of any single run and holding plan times at a consistent four to six minutes.</li>
```

with:

```html
          <li>Each root is wired to one of the workspaces from earlier - the pivot changed what a root contains, not the workspaces.</li>
```

Delete:

```html
      <p class="slide-note">Sandbox has no workspace at all - it is local dev only, driven from the CLI. Plans on these workspaces run consistently in four to six minutes.</p>
```

- [ ] **Step 2: Notes**

Replace the `#s15b` aside with:

```html
      <aside class="notes">
        <p>The workspaces did not change in the pivot - it was always three per instance. What changed is what each root contains: a module call and a small file of genuine differences.</p>
        <p>Payloads live in the modules too. Staging-only profiles sit in a visible directory, so divergence is explicit.</p>
      </aside>
```

Set the `s15b` `notes` in `presenter.json` to those two strings.

- [ ] **Step 3: Screenshot `s15b` and `?reader=1#s15b`** (the reader chip now has more room without the slide-note), run the text lint, commit

`AGENTS.md`: change row 18 to `s15b The module structure (module tree -> roots; workspaces are on s-workspaces) - **Dafydd**`.

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json AGENTS.md && git commit -m "Keep the module slide to modules

Workspace count, sandbox and plan times now live on the workspace
architecture slide; s15b points back at it."
```

---

### Task 16: Move the numbers onto Links, delete s16b (D4)

**Files:**
- Modify: `presentations/migrating_an_instance/index.html` (CSS after `.stat-label` ~line 707; delete `#s16b` lines 1431-1464; `#s18` lines 1485-1496; `#s-today` notes ~1425-1428)
- Modify: `presentations/migrating_an_instance/presenter.json` (remove `s16b`; `s18` notes + timer; `s-today` title + notes)
- Modify: `AGENTS.md` (slide list; "Numbers" settled fact; folded-slides note)

- [ ] **Step 1: CSS** - after `.stat-label { ... }` add:

```css
/* compact 3x2 stats row on the links slide */
.stats-compact { width: 100%; max-width: 1400px; margin-top: var(--sp-3); }
.stats-compact .stat { padding: var(--sp-3); }
.stats-compact .stat-num { font-size: var(--fs-h1); }
.stats-compact .stat-num-sm { font-size: var(--fs-h2); }
```

- [ ] **Step 2: Delete the s16b section** - everything from `<!-- ============================ S16b - By the numbers ============================ -->` through the `</section>` closing `id="s16b"`, plus the blank line after.

- [ ] **Step 3: Rebuild s18**

Replace the whole `#s18` section with:

```html
    <!-- ============================ S18 - Links ============================ -->
    <section class="slide slide-centred" id="s18" aria-label="Links" data-speaker="Anyone" data-when="2026-07">
      <h1 class="slide-title">Links</h1>
      <div class="closing-links">
        <span>Provider: deploymenttheory/jamfpro</span>
        <span>SDK: jamfpy</span>
      </div>
      <span class="todo">TODO Q12: URLs, contact and socials</span>
      <div class="stats stats-compact">
        <div class="card stat">
          <span class="stat-num stat-num-sm">Apr 2025 →<br>May 2026</span>
          <span class="stat-label">provider development to v1.0.0 and final handover</span>
        </div>
        <div class="card stat">
          <span class="stat-num">14+</span>
          <span class="stat-label">contributors</span>
        </div>
        <div class="card stat">
          <span class="stat-num">526+</span>
          <span class="stat-label">pull requests</span>
        </div>
        <div class="card stat">
          <span class="stat-num">1,902</span>
          <span class="stat-label">commits</span>
        </div>
        <div class="card stat">
          <span class="stat-num">127</span>
          <span class="stat-label">Terraform files</span>
        </div>
        <div class="card stat">
          <span class="stat-num">19,000+</span>
          <span class="stat-label">lines of HCL</span>
        </div>
      </div>
      <aside class="notes">
        <p>Point at the provider and jamfpy repos; contact details. The numbers are here for anyone who wants them - April 2025 is the provider-development start, nothing was imported before November 2025, and May 2026 is v1.0.0 and the final handover.</p>
      </aside>
    </section>
```

- [ ] **Step 4: Move the handover close to s-today's notes**

Replace the `#s-today` aside with:

```html
      <aside class="notes">
        <p>Walk the four tiers by role, not by name. Sandbox: isolated, no restrictions, CLI and GUI both open - break it, reset, start again; onboarding and leadership demos live here. DevTest: under IdP and device compliance but not change controlled - prove a change out fast. Staging: an exact replica, to the point that a device enrolled there is indistinguishable bar the MDM certificate - and it is only true because of the rebuild three slides back. Production: minimal downtime, because everything upstream has already done the work.</p>
        <p>Then CalVer: we defaulted to SemVer like typical devs, but v1.64.3 tells you nothing about a Jamf Pro estate. A date does - roll back to the day the incidents were raised.</p>
        <p>Close on the handover: v1.0.0 and the final handover landed in May 2026, the Mac engineering team is working proficiently on its own, approaching a thousand pull requests now, and none of the three of us are on that team any more. The estate is still moving. That is the real number.</p>
      </aside>
```

- [ ] **Step 5: presenter.json**

- Delete the `s16b` entry.
- `s18`: `timerSeconds` `45`, `notes` the one string from Step 3.
- `s-today`: `title` `"The estate today"` (the file still says "Refinements along the way"), `timerSeconds` `75`, `notes` the three strings from Step 4.

- [ ] **Step 6: AGENTS.md**

- Slide list: delete the `s16b` row; change the `s18` row to `s18 Links (plus the six by-the-numbers stats, moved here from the old s16b) - **Anyone**`; change the `s-today` row to end `... Release Please -> CalVer; closes on the handover) - **Gordon**`.
- "Former slides folded away" paragraph: add `s16b` (stats onto `s18`, handover close into `s-today`'s notes - Aug 2026 feedback).
- "Numbers" settled fact: append `Shown on s18 since Aug 2026.`

- [ ] **Step 7: Screenshot `s18` and `s-today`**

`s18` is a centred slide: the six compact cards must fit between the TODO chip and the strip, and "Apr 2025 → / May 2026" must stay inside its card. If the date card overflows, change `.stats-compact .stat-num-sm` to `font-size: var(--fs-body);`.

- [ ] **Step 8: Run the text lint** (count 22) and commit

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json AGENTS.md && git commit -m "Move the numbers onto the links slide

By-the-numbers is gone as a slide; its stats sit under the links and
its handover close moves into the estate-today notes so the talk still
ends on it."
```

---

### Task 17: presenter.json - final order, titles and timers

**Files:**
- Modify: `presentations/migrating_an_instance/presenter.json` (whole file)

Earlier tasks edited notes per slide. This task fixes what they could not: the file's order still matches the pre-`bdf25db` deck (`s-pivot`, `s15b`, `s-staging`), and the timers no longer sum to 1800.

- [ ] **Step 1: Reorder the `slides` array** to exactly:

`s00, s01, s02, s03, s04, s05, s07, s-singletons, s-sentinel, s10, s08, s11, s12, s13, s-workspaces, s-staging, s-pivot, s15b, s-today, s17, s18, s-thanks`

- [ ] **Step 2: Set the timers** so they sum to 1800:

| id | timerSeconds |
|---|---|
| s00 | 90 |
| s01 | 90 |
| s02 | 45 |
| s03 | 60 |
| s04 | 75 |
| s05 | 90 |
| s07 | 30 |
| s-singletons | 75 |
| s-sentinel | 90 |
| s10 | 75 |
| s08 | 90 |
| s11 | 75 |
| s12 | 120 |
| s13 | 45 |
| s-workspaces | 60 |
| s-staging | 120 |
| s-pivot | 60 |
| s15b | 90 |
| s-today | 75 |
| s17 | 285 |
| s18 | 45 |
| s-thanks | 15 |

(90+90+45+60+75+90+30+75+90+75+90+75+120+45+60+120+60+90+75+285+45+15 = 1800.)

- [ ] **Step 3: Check every `title` matches the slide's `aria-label`** - in particular `s03` "What we decided up front", `s-sentinel` "Infrastructure challenges", `s13` "The for_each exception", `s-today` "The estate today".

- [ ] **Step 4: Run the sync check** - must print `OK`

```sh
cd /Users/josephlittle/Github/jnuc-2026 && node "${TMPDIR:-/tmp}/check-presenter.mjs"
```

(Use the scratchpad path you wrote it to.) Fix any `notes differ` line by copying the aside text from the HTML into the JSON, not the other way round - the HTML is the source of truth.

- [ ] **Step 5: Commit**

`AGENTS.md`: in the `presenter.json` row of the Files table, the sentence "Timer allocations are proposed, not rehearsed." still holds; add "Re-balanced Aug 2026 for the 22-slide order."

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add presentations/migrating_an_instance/presenter.json AGENTS.md && git commit -m "Bring presenter.json back in step with the deck

Order, titles and notes now mirror index.html; timers re-balanced to
1800 seconds for the 22-slide deck."
```

---

### Task 18: AGENTS.md sweep, full deck check, rebuild the Keynote download

**Files:**
- Modify: `AGENTS.md`
- Rebuild: `presentations/migrating_an_instance/from-clicks-to-code-jnuc2026.key`

- [ ] **Step 1: Rewrite the "Current slide order (story arc)" list in AGENTS.md** as a clean numbered list of 22 with the per-task wording applied, change "23 slides" to "22 slides", and make sure these lines elsewhere in the file are true:

- Layout table: a row `| docs/superpowers/plans/ | Implementation plans for feedback rounds. Not shipped (the deploy syncs presentations/ only). |` exists (added when this plan was written; keep it).
- "Verifying changes": the example URL ends `#s00`, not `#s00b` (that slide no longer exists).
- The `presentations/migrating_an_instance` Files table row for `index.html` still reads correctly.
- Outstanding TODO chips table is unchanged (s00 photos, s-pivot conditional, s-staging month, s18 Q12).

- [ ] **Step 2: Screenshot every slide and inspect each PNG**

```sh
cd /Users/josephlittle/Github/jnuc-2026 && (lsof -i :8741 >/dev/null 2>&1 || (python3 -m http.server 8741 >/dev/null 2>&1 &)) && sleep 1 && OUT="${TMPDIR:-/tmp}/jnuc-shots" && mkdir -p "$OUT" && for s in s00 s01 s02 s03 s04 s05 s07 s-singletons s-sentinel s10 s08 s11 s12 s13 s-workspaces s-staging s-pivot s15b s-today s17 s18 s-thanks; do "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --window-size=1920,1080 --hide-scrollbars --virtual-time-budget=3000 --screenshot="$OUT/$s.png" "http://localhost:8741/presentations/migrating_an_instance/index.html#$s" 2>/dev/null; done; ls "$OUT"
```

Open all 22 with the Read tool. Fail the task on any text clipped at the canvas edge, any content overlapping the timeline strip, or any box in the two SVG slides with text escaping it.

- [ ] **Step 3: Presenter view, reader mode, file://**

```sh
cd /Users/josephlittle/Github/jnuc-2026 && OUT="${TMPDIR:-/tmp}/jnuc-shots" && C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" && "$C" --headless --disable-gpu --window-size=1200,760 --hide-scrollbars --virtual-time-budget=3000 --screenshot="$OUT/pv-s08.png" "http://localhost:8741/presentations/migrating_an_instance/index.html?presenter=1#s08" 2>/dev/null && "$C" --headless --disable-gpu --window-size=1920,1080 --hide-scrollbars --virtual-time-budget=3000 --screenshot="$OUT/reader-ws.png" "http://localhost:8741/presentations/migrating_an_instance/index.html?reader=1#s-workspaces" 2>/dev/null && "$C" --headless --disable-gpu --window-size=1920,1080 --hide-scrollbars --virtual-time-budget=3000 --screenshot="$OUT/file-s00.png" "file:///Users/josephlittle/Github/jnuc-2026/presentations/migrating_an_instance/index.html#s00" 2>/dev/null && ls "$OUT" | grep -E 'pv|reader|file'
```

Presenter view must show the s08 notes (three paragraphs) and "Next: Tools and helpers". Reader mode must show the "More detail" chip above the strip. The `file://` title slide must show the three speaker cards.

- [ ] **Step 4: Lint, sync check, slide count**

```sh
cd /Users/josephlittle/Github/jnuc-2026 && grep -n -e "—" -e "–" presentations/migrating_an_instance/index.html presentations/migrating_an_instance/presenter.json AGENTS.md; echo "dash hits above (expect none)"; grep -c '<section class="slide' presentations/migrating_an_instance/index.html; node "${TMPDIR:-/tmp}/check-presenter.mjs"
```

Expect: no dash hits, `22`, `OK`.

- [ ] **Step 5: Rebuild the Keynote download**

Needs Keynote installed and, once, `npm ci && npx playwright install chromium`.

```sh
cd /Users/josephlittle/Github/jnuc-2026 && npm run build:key 2>&1 | tail -20 && ls -la presentations/migrating_an_instance/*.key presentations/training_a_team/*.key
```

The script fails loudly if ArrowRight ever fails to advance - that is the end-to-end navigation check. Both `.key` files are rewritten; only commit the one for this deck unless the training deck's bytes changed for a reason you understand (`git status` will show it - if it changed and you did not touch that deck, `git checkout -- presentations/training_a_team/ClickOps_to_GitOps.key`).

- [ ] **Step 6: Commit**

```sh
cd /Users/josephlittle/Github/jnuc-2026 && git add AGENTS.md presentations/migrating_an_instance/from-clicks-to-code-jnuc2026.key && git commit -m "Rebuild the clicks-to-code Keynote download and settle AGENTS.md

22-slide order recorded; verification hash fixed; .key rebuilt from the
edited deck."
```

- [ ] **Step 7: Report** - `git log --oneline main..HEAD` and the list of decisions D1-D7 with what was assumed, so Joseph can flip any of them.

---

## Self-review

- **Spec coverage:** every line in `feedback-clickstocode.md` maps to a task or a "done in bdf25db / nothing to do" row in Section 1. The two questions the feedback leaves open (Sentinel keep-or-cut, replace validation with workspace architecture) are D1 and Task 10 with defaults stated.
- **Placeholders:** the only open values are the three pre-existing TODO chips (photos, real conditional, staging month) and the Q12 links chip; none were introduced by this plan. `${TMPDIR:-/tmp}` is a real fallback, not a placeholder.
- **Consistency:** ids used across tasks - `s-workspaces` (Tasks 10, 15, 17, 18), `.s08-validate`/`.s08-checks` (Task 9 only), `.code-zoom` + `--fs-code-zoom`/`--lh-code-zoom` (Task 11 only), `.exceptions-1` (Task 12 only), `.stats-compact` (Task 16 only), `.s-ws-intro`/`.s-ws-svg`/`.inst` (Task 10 only). Timer table in Task 17 matches the per-task timer edits (s08 90, s-workspaces 60, s18 45, s-today 75) and takes the remaining 15 seconds off questions (s17 285).
