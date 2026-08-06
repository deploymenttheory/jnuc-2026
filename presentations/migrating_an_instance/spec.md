# Deck spec and change history

The archive behind `index.html`. AGENTS.md is the live reference for what the deck is and how
to work on it; this file is where all of that came from - the original build runbook, Joseph's
source narrative, and three rounds of questions answered inline.

Nothing here overrides AGENTS.md. Where a section has been overtaken by a later decision it is
marked SUPERSEDED with a pointer to what replaced it. Everything is kept anyway: the reasoning
behind a discarded option is often the thing you need six months later.

Consolidated on 30 Jul 2026 from `fable-spec.md`, `story.md`, `amendments.md`,
`amendments-2.md` and `story-questions.md`, which this file replaces in full.

## Contents

1. How the deck got here
2. The original build runbook (29 Jul 2026)
3. The source narrative (30 Jul 2026)
4. Round 1 - open questions
5. Round 2 - slide-by-slide corrections
6. Round 3 - story questions
7. Decision index

---

## 1. How the deck got here

**Pass one, 29 Jul 2026.** A background document was turned into the runbook in section 2:
17 slides, each specified down to layout, on-slide copy and speaker notes, with 17 unresolved
points flagged as `[OPEN Qn]` and rendered in the deck as amber TODO chips rather than guessed
at. The first `index.html` was built from that runbook.

**Pass two, 29 Jul 2026.** Two feedback rounds in quick succession. Round 1 (section 4) answered
the open questions: light theme instead of dark, GT Ultra, no live demo, real HCL over
representative examples, a 30-minute slot for three speakers. Round 2 (section 5) was a
slide-by-slide read-through with corrections - wrong team names, wrong objective ordering, a
factually wrong claim that every instance was VCS-triggered.

**Pass three, 30 Jul 2026.** Joseph supplied the narrative in section 3: why production was
migrated first, the Sentinel wall, the loop that did the actual work, and the March module pivot.
This changed the deck from a description of an architecture into a story with a spine. Round 3
(section 6) pinned down the facts behind it - the read-only API client, the singleton trick, the
staging rebuild, the timeline anchors.

**Pass four, 30 Jul 2026.** The restructure: 27 slides reordered into context -> decisions ->
first wins -> the wall -> the loop -> growing pains -> payoff, then trimmed to 23 to fit the slot.
Dates moved off the slides onto a persistent timeline strip. Seven new story slides were added
(`s00b`, `s-singletons`, `s-sentinel`, `s-pivot`, `s15b`, `s-staging`, `s-today`) and four old
ones folded away. Legacy section ids were kept stable through the reorder, which is why `s10` no
longer sits at position 10.

The current slide order, the settled facts and the outstanding TODO chips live in AGENTS.md, not
here.

---

## 2. The original build runbook

> Status: historical. Sections 2.0 to 2.2 still describe how the deck is authored, and AGENTS.md
> restates them. Section 2.3 (deck order) and section 2.5 (open questions) are SUPERSEDED. The
> slide specifications in 2.4 are the source of every fact on the slides that descended from them;
> each carries a note on where it ended up.

Working title: **From Clicks to Code - Migrating Jamf Pro to Terraform at Lloyds Banking Group**
[OPEN Q12]
Speaker: Joseph Little. Co-builder and co-owner of the `deploymenttheory/jamfpro` Terraform
provider. [OPEN Q12 for exact credit line]

### 2.0 Instructions to the build agent

You are building a conference presentation as an HTML deck from this spec. Follow it exactly.

- Do not invent facts, numbers, resource names, or rationale. Anywhere this document says
  `[OPEN Qn]`, the content is unresolved. Render unresolved content as a visible amber
  placeholder chip (`TODO Qn: <short description>`) on the slide so nothing ships silently wrong.
- All styling derives from the token block in section 2.2. Never hardcode a colour, font, or size
  in slide markup. If you need a new value, add a token.
- No emojis anywhere in the deck.
- British English throughout (organisation, optimisation, enrolment).
- On-slide text is what appears on screen. Speaker notes are for the presenter only (delivery per
  [OPEN Q14]).

### 2.1 Delivery constraints

- One single self-contained `.html` file. Zero external requests at runtime: no CDNs, no webfont
  fetches, no external JS. Assume no network (conference wi-fi, locked-down corporate laptop).
  Fonts must be system-stack or embedded. [OPEN Q3 - confirm vs a framework like reveal.js]
- 16:9. Design at a 1920x1080 canvas, scaled to viewport via CSS transform or vw units.
- Navigation: arrow keys and space advance; left arrow back; `Home`/`End` jump; URL hash per slide
  (`#s04`) so any slide is directly linkable; small unobtrusive slide counter bottom-right.
- Code blocks: monospace, syntax-highlighted. Because no external libs, either pre-tokenise the
  HCL into spans by hand or embed a tiny highlighter inline.
- Respect `prefers-reduced-motion`. Keep transitions to a single restrained slide-change animation
  (`--transition-slide`), no scattered effects.
- Visible keyboard focus states on any interactive element.

### 2.2 Styling constants

Define once in `:root`. Palette and type below are PENDING placeholders until Q1/Q2 are answered -
structure is final, values are not.

> SUPERSEDED, values only. The palette below was a dark placeholder pending Q1/Q2; Round 1 flipped
> the deck to a light LBG-green theme with GT Ultra. The live token block in `index.html` is the
> source of truth. The structure - tokens for canvas, palette, type, spacing, shape and motion,
> nothing hardcoded in slide markup - is unchanged and still binding.

```css
:root {
  /* Canvas */
  --slide-w: 1920px;
  --slide-h: 1080px;
  --slide-pad: 96px;

  /* Palette - PENDING Q1 (brand direction undecided) */
  --c-bg: #101418;          /* base background */
  --c-surface: #1A2026;     /* cards, code blocks */
  --c-border: #2C343C;
  --c-text: #EDF1F4;
  --c-text-muted: #93A0AB;
  --c-accent: #7DE24B;      /* primary accent: chosen paths, highlights */
  --c-accent-2: #5CA8FF;    /* secondary accent: links, diagram edges */
  --c-danger: #F0554D;      /* rejected ideas, revoked permissions */
  --c-success: #4CC38A;     /* validated / managed states */
  --c-warn: #E3A008;        /* TODO placeholder chips, freeze notices */

  /* Typography - PENDING Q2 */
  --f-display: Georgia, "Times New Roman", serif;        /* placeholder - slide titles */
  --f-body: -apple-system, "Segoe UI", Roboto, sans-serif;
  --f-mono: "SF Mono", "Cascadia Code", Consolas, monospace;
  --fs-hero: 88px;
  --fs-h1: 64px;
  --fs-h2: 44px;
  --fs-body: 30px;
  --fs-code: 26px;
  --fs-caption: 22px;
  --lh-tight: 1.1;
  --lh-body: 1.45;

  /* Spacing scale */
  --sp-1: 8px;  --sp-2: 16px; --sp-3: 24px;
  --sp-4: 40px; --sp-5: 64px; --sp-6: 96px;

  /* Shape and motion */
  --radius: 12px;
  --transition-slide: 240ms ease;
}
```

Signature visual device (use consistently, sparingly): the deck's recurring motif is
**clicks vs code** - UI-chrome fragments (buttons, checkboxes, cursor) rendered in
`--c-text-muted` being replaced by monospace HCL in `--c-accent`. Use it on the title slide and
once at the close; do not repeat it on every slide. As built, this exists as the title wording
rather than as a drawn device.

### 2.3 Deck order

> SUPERSEDED by the story restructure. AGENTS.md holds the current 23-slide order. Kept here
> because the ID column explains why today's ids do not match today's positions.

| ID  | Slide | Source | Where it is now |
|-----|-------|--------|-----------------|
| S00 | Title | ADDED - [OPEN Q12] | `s00` |
| S01 | Context, requirements, constraints | Slide 1 | `s01` |
| S02 | Who touches Jamf Pro | Slide 2 | `s02` |
| S03 | Migration objectives and design decisions | Slide 3 | `s03` |
| S04 | Ideas rejected, and why | Slide 4 | `s04`, trimmed to 3 rejects |
| S05 | Instance migration order | Slide 5 | `s05` |
| S06 | Resource migration path | Slide 6 - INCOMPLETE [OPEN Q6] | folded into `s10`'s intro |
| S07 | Instance prep | Slide 7 | `s07` |
| S08 | Migration wave workflow | Slide 8 | `s08` |
| S09 | Resource sequencing | Slide 9 | folded into `s10` |
| S10 | The sequence, visualised | Slide 10 | `s10` |
| S11 | Tools and helpers | unnumbered "migration tools and helpers" slide | `s11` |
| S12 | Dynamic creation with for_each | Slide 11 | `s12` |
| S13 | for_each exceptions | Slide 12 | `s13` |
| S14 | Validating a migration | Slide 13 | `s14` |
| S15 | Workspace optimisation | Slide 14 - thin [OPEN Q13] | dropped; became `s15b` |
| S16 | Live demo - import sequence | "Live Demo example of import sequence (Joe)" | removed, Q17 |
| S17 | Closing / Q&A / links | ADDED - [OPEN Q12] | split into `s17` and `s18` |

Optional S16b "By the numbers" pending [OPEN Q10]. Approved, now `s16b`.

### 2.4 Slide specifications

#### S00 - Title [ADDED, confirm Q12]

- Layout: full-bleed. Title in `--f-display` at `--fs-hero`, subtitle beneath, speaker credit
  bottom-left, JNUC 2026 mark bottom-right [OPEN Q1 - logo assets].
- On-slide: title [OPEN Q12], subtitle "Migrating Jamf Pro management from click-ops to
  infrastructure as code", "Joseph Little - Lloyds Banking Group", provider credit line
  [OPEN Q12].
- Visual: the clicks-vs-code signature motif.

Now `s00`. Round 1 removed the JNUC 2026 mark for a placeholder-logo chip and removed the provider
credit line; Round 2 removed the second subtitle line. The credit moved to the new `s00b`
"Who we are".

#### S01 - Context, requirements, constraints

- Purpose: establish the estate and the non-negotiables before any design talk. Everything later
  traces back to a constraint here.
- Layout: top band shows the route to live as a three-node pipeline; below, constraints as a
  two-column checklist of cards.
- On-slide, pipeline: `Dev/Test -> Staging -> Production` labelled "Route to live - three Jamf Pro
  instances".
- On-slide, constraints:
  - No hardcoded secrets, anywhere.
  - Every production change gated by peer review.
  - Align with the bank's strategic tooling: GitHub, VCS-triggered Terraform runs, HashiCorp
    Vault, HCP Terraform for remote state and run execution on HCP private runners.
    [OPEN Q5 - Vault vs HCP-native secrets end-state]
  - Terraform CLI available only in development environments.
  - One shared source of truth for every team - resources are not split by org structure.
  - Post-migration, all create/update/delete operations happen through Terraform only.
  - All HCL must satisfy org linters.
  - Release Please for versioning and release tagging. [OPEN Q4 - see semver/CalVer contradiction]
- Speaker notes: this is a bank; the constraints are the interesting part. The TF CLI restriction
  in particular shapes the whole workflow (no local applies, no local state access - pays off on
  S14).

Now `s01`. The Release Please constraint was generalised to "versioned releases, with change
history findable when it is needed" once Q4 established that Release Please was later dropped for
CalVer; that switch is now its own beat on `s-today`. The pipeline gained the parity notes from
the source narrative, which set up both the prod-first decision and the staging rebuild.

#### S02 - Who touches Jamf Pro

- Purpose: five teams, one config surface. Motivates the single-source-of-truth decision.
- Layout: five cards in a row (or 2+3 grid), each with team name and access model. Colour-code:
  "actions only" in `--c-text-muted`, "resource management" in `--c-accent`.
- On-slide:
  - 1st / 2nd line support - actions only
  - 3rd line support - resource management
  - Mac Platform team - resource management
  - Device Security Engineering - resource management
  - App Packaging - resource management
- Speaker notes: four of five teams write config. Splitting the repo by team would have fragmented
  ownership of shared dependencies.

Now `s02`, corrected by Round 2 to four teams with the real names: Support, Mac@LBG, Security,
App Packaging & Deployment. The Support card carries an open TODO for its access model. The
five-team split above is the only record of the original reading - 1st/2nd line as actions only,
3rd line as resource management - and may be the answer to that TODO, but it has not been
confirmed, so it is not on the slide.

#### S03 - Migration objectives and design decisions

- Purpose: the eight decisions that define the target state.
- Layout: numbered list is legitimate here (it is a genuine enumeration), split into two visual
  groups: "Governance" (items 2, 5, 6, 7) and "Architecture and DX" (items 1, 3, 4, 8). Keep
  numbering continuous.
- On-slide:
  1. One Terraform definition drives all instances.
  2. A monorepo is the single source of truth for every instance.
  3. Secrets centralised in HashiCorp Vault. [OPEN Q5]
  4. Branching strategy supports three environments with VCS-based triggers.
  5. Every merge to main requires at least one peer review from another engineer.
  6. Post-migration, all engineers drop to read-only in Jamf Pro; only the Terraform machine
     identity holds full CRUD.
  7. Break-glass account available, held in PAM.
  8. Developer experience: one resource block per type, fed by a parameter map - BAU change means
     appending an entry to the params list, not writing HCL from scratch.
- Speaker notes: item 8 was aimed squarely at Mac engineers new to Terraform; it lowers the
  contribution bar to "edit a map".

Now `s03`. Round 2 renumbered the list so the visible order matches the groups (Governance 1-4:
monorepo, peer review, read-only, break-glass; Architecture and DX 5-8: one definition, Vault,
branching, DX), expanded PAM to Privileged Access Management, noted that one instance is
CLI-triggered rather than VCS, and simplified item 8 to "BAU change is a one-line edit to a
parameter map, not hand-written HCL". Q5 added the Vault detail: internally hosted, set once by
humans, read by Terraform via data sources.

#### S04 - Ideas rejected, and why

- Purpose: credibility through discarded options.
- Layout: table or stacked cards, idea on the left struck through or tagged in `--c-danger`,
  rationale on the right.
- On-slide:
  - **A single workspace for all resources** - blast radius and plan execution time. Guidance
    suggests roughly 500 resources per workspace; the estate holds 1,500+. At ~5,000, things break
    down. [Tone of "boom boom" - OPEN Q11]
  - **Semantic versioning for releases** - version numbers carried no meaning against Jamf Pro's
    history. Chose calendar versioning instead: when a flood of tickets lands on 1 December, the
    matching release and its change history are findable by date. [OPEN Q4]
  - **Per-team Terraform modules scoped to each team's resources** - [rationale not stated in
    source; presumed conflict with the single-source-of-truth constraint - OPEN Q16]
  - **Managing everything with Terraform** - deliberately excluded pre-existing global settings
    such as cloud identity provider integrations: live-config breakage risk, and they are
    singletons.
  - **Sandbox inside the route to live** - trialled, then removed and kept separate. [rationale not
    stated - OPEN Q16]
- Speaker notes: the "everything in Terraform" rejection is the one audiences push back on; be
  ready to defend leaving singleton service integrations alone.

Now `s04`, holding the three architectural rejections. Per SQ9 the other two moved to where they
happened in the story: CalVer and sandbox-out-of-the-route-to-live are both on `s-today`. Q16 gave
per-team modules its real reason (internal approval complexity, with a TODO to expand). Round 2
rewrote the manage-everything rejection to the sharper version: static group membership stays
unmanaged to protect the support experience, because troubleshooting should not require a pull
request.

#### S05 - Instance migration order

- Purpose: one decision, clearly argued.
- Layout: two large option cards side by side. `Staging -> Production` dimmed; `Production first`
  highlighted in `--c-accent` with a "chosen" tag.
- On-slide: "We migrated production first. Staging had drifted so far from production that
  importing it first would have validated the wrong thing."
- Speaker notes: counterintuitive on purpose - importing is read-then-manage, so starting with
  prod is lower-risk than it sounds, and it means the config you codify is the config that
  matters.

Now `s05`. Round 2 asked for a TODO here so Joseph could explain why; SQ3 answered it, and the
slide now carries the control that made prod-first safe as its own card - the Terraform API client
held read-only scopes during import, widened only once imports were stable with no recurring diff,
with Joseph and Gordon holding those keys.

#### S06 - Resource migration path [OPEN Q6 - source is truncated]

- Purpose: second axis of ordering - per resource type vs per instance.
- Layout: mirror S05's two-option card layout for visual consistency.
- On-slide, as far as the source states:
  - Option A: take one resource type end-to-end across all instances, then move to the next.
  - Option B: "Migrate one" - sentence cut off in source. Presumed: migrate one instance
    completely, then the next. [OPEN Q6]
  - Chosen option and rationale: not stated. [OPEN Q6]
- Render both options plus an amber placeholder chip for the decision until Q6 is answered.

Folded into `s10`'s intro during the trim. Q6 settled it: everything was migrated in place in
production first, one resource type at a time, imported very verbosely and then moved into more
efficient `for_each` blocks. That sentence now opens `s10`, so the slide-sized version of the
question was no longer worth its 30 seconds.

#### S07 - Instance prep

- Purpose: the unglamorous pre-flight work.
- Layout: pre-flight checklist styling - checkbox glyphs in `--c-success`.
- On-slide:
  - Big tidy-up: removed all non-active resources from the tenant.
  - Verified API credentials per client were valid and complete.
  - Confirmed the Jamf Pro instance version met provider requirements.
  - Stored credentials for every instance's API clients in the secrets manager.
- Speaker notes: the tidy-up mattered - importing dead config would have codified years of cruft.

Now `s07`, with an open TODO for more prep points (Round 2).

#### S08 - Migration wave workflow

- Purpose: the repeatable per-wave runbook. This is the operational heart of the talk.
- Layout: horizontal stepper, seven steps, numbered (genuine sequence). Step 3 gets a `--c-danger`
  lock glyph.
- On-slide:
  1. Tell the Mac team which resources are in this wave.
  2. Communicate a change freeze for those resource types to affected teams.
  3. Start the wave: revoke GUI write permissions for in-scope resources - no side-door edits
     mid-import. [Original phrasing "so that people are not cheeky buggars" - keep or formalise,
     OPEN Q11]
  4. Run the import.
  5. Validate the import succeeded.
  6. Publish example documentation showing how to manage the resource via Terraform in BAU.
  7. Announce to all teams: the resource is now Terraform-managed.
- Speaker notes: step 3 is the one people skip and regret. Permissions revocation makes the freeze
  real rather than polite.

Now `s08`, unchanged in content. Q11 kept the formalised wording for step 3.

#### S09 - Resource sequencing

- Purpose: which resources go first and why.
- Layout: five ordered tiers, top to bottom, width or colour intensity increasing with risk. Pairs
  with S10 - keep this slide text-only.
- On-slide:
  1. Singletons and resources that rarely change.
  2. Dependency targets - resources other resources depend on.
  3. Resources with one or two dependencies.
  4. Resources with more than two dependencies.
  5. Policies last.
- Speaker notes: risk scales with dependency fan-in; policies sit on top of everything, so they
  close the migration.

Folded into `s10`. The text tiers and the diagram said the same thing twice; the diagram carries
the labels now.

#### S10 - The sequence, visualised

- Purpose: the S09 tiers as one diagram. Source says only "Diagram."
- Layout: full-slide inline SVG. Five horizontal bands matching the S09 tiers, dependency arrows
  flowing downward into the policies band. Band labels in `--f-mono` caption size; arrows in
  `--c-accent-2`.
- Content: generic band labels by default. Real resource-type names per band (e.g. which resources
  were the singletons, which were the shared dependencies) pending [OPEN Q7].
- Build as SVG in the file, not a raster image, so it inherits tokens.

Now `s10`, absorbing S06's decision and S09's tiers. SQ6 added where the order came from: a
spreadsheet of every resource type and its dependencies, built by the group. Q7's real
resource-type names remain an open TODO for Gordon Deacon.

#### S11 - Tools and helpers

- Purpose: how imports were actually mechanised.
- Layout: left, a vertical pipeline diagram: `jamfpro Python SDK -> per-resource script ->
  structured map -> Terraform local -> for_each resource block -> import`. Right, supporting
  bullets.
- On-slide:
  - Extraction driven by the jamfpro Python SDK.
  - Each migration candidate got a script that pulled live config and emitted a structured map,
    shaped for a Terraform `local`.
  - Map pasted into a `local`; a single resource block with `for_each` loops over it to
    create/import every instance of that type.
  - Regex mop-up pass to tidy the generated output.
  - Rejected `terraform plan -generate-config-out`: it emits one HCL block per resource; we wanted
    one block per resource type driven by data. [Source sentence truncates at "Instead wanted" -
    confirm this completion, OPEN Q9]
  - AI-assisted where it helped. [Too vague to render - what specifically, and what can be said
    publicly? OPEN Q8]
- Speaker notes: the SDK is Joseph's own open-source project (jamfpy) - decide whether to say so
  here or on S17. [OPEN Q12]

Now `s11`. Q8 replaced the vague AI line with the specific one: AI-assisted validation of
configuration and dependency links, mostly Copilot CLI. The generate-config-out completion is
still marked TODO Q9 for confirmation.

#### S12 - Dynamic creation with for_each

- Purpose: the deck's technical centrepiece. Left/right code comparison.
- Layout: two code panels side by side. Left titled "generate-config-out style", right titled
  "Ours", right panel bordered in `--c-accent`. Beneath, one line of takeaway text.
- Code: representative example below; replace with sanitised real HCL if supplied [OPEN Q9].

Left panel:

```hcl
resource "jamfpro_category" "engineering" {
  name     = "Engineering"
  priority = 9
}

resource "jamfpro_category" "security" {
  name     = "Security"
  priority = 9
}

# ... one block per category, repeated ~120 times
```

Right panel:

```hcl
locals {
  categories = {
    "Engineering" = { priority = 9 }
    "Security"    = { priority = 9 }
    # BAU change = append one line here
  }
}

resource "jamfpro_category" "managed" {
  for_each = local.categories
  name     = each.key
  priority = each.value.priority
}
```

- On-slide takeaway: "Adding resource number two hundred is a one-line diff. Reviews read the
  data, not the boilerplate."
- Speaker notes: maintainability (single block to fix when the provider changes), review
  ergonomics (diffs are data), scaling (map grows, HCL does not).

Now `s12`, which also absorbed the refinement passes from the source narrative and the
Gordon/Joseph split of the work. Q9 asked for real HCL: the representative example above is still
in place behind a TODO chip until sanitised real HCL arrives.

#### S13 - for_each exceptions

- Purpose: honesty about where the pattern broke.
- Layout: simple. Two exception cards: Policies, Dock Items. Beneath each, the conditions that
  triggered the exception.
- On-slide:
  - The parameter-map pattern is a default, not dogma.
  - Exceptions: policies and dock items.
  - Trigger conditions: payload complexity and readability - when the map becomes harder to read
    than plain HCL, the pattern has stopped paying for itself.
- Speaker notes: expand on what specifically made policies unmappable (nested payload structure,
  scope blocks). [Any extra detail welcome - OPEN Q9]

Now `s13`, unchanged.

#### S14 - Validating a migration

- Purpose: how "done" was proven before permissions were pulled.
- Layout: four sequential gates. Centrepiece: a mock terminal panel in `--c-surface` rendering
  `No changes. Your infrastructure matches the configuration.` in `--f-mono`.
- On-slide:
  1. `terraform plan` returns zero diff.
  2. State is centralised in HCP and not locally inspectable - used AI-assisted checks to confirm
     each resource exists with the correct dependencies assigned. [OPEN Q8 - specifics]
  3. Sweep for orphaned resources living outside the HCL config.
  4. Only after all checks pass: remove UI write permissions for that resource type.
- Speaker notes: gate 4 is the point of no return and the point of the whole exercise.

Now `s14`, with gate 2 naming Copilot CLI per Q8.

#### S15 - Workspace optimisation [OPEN Q13 - source is two bullet fragments]

- Purpose: how the estate was split into workspaces, and the numbers behind it.
- Layout: intended as a chart slide - resources-per-workspace bar chart or a workspace table - but
  the chosen topology, workspace count, and plan-time figures are not in the source.
- On-slide, currently supportable: "Blast radius vs plan execution time" and the 500/1,500+/5,000
  figures from S04.
- Everything else renders as amber placeholder chips until Q13 is answered. Do not fabricate a
  topology.

Dropped. Q13 asked for a proper topology slide instead, and the module pivot in the source
narrative supplied it: `s15b` "The module structure" is that slide. The 500/1,500/5,000 figures
stayed on `s04`, and the plan-time figures are still an open TODO on `s15b`.

#### S16 - Live demo: import sequence

- Purpose: holding slide while Joseph demos.
- Layout: near-empty. Title "Live demo - importing a resource", one caption line listing what the
  audience is about to see [OPEN Q17 - demo scope], `--c-text-muted`.
- Include a fallback consideration: pre-rendered screenshots or a recording if the demo
  environment dies. [OPEN Q17]

Removed. Q17: there is no demo.

#### S17 - Closing / Q&A [ADDED, confirm Q12]

- Layout: mirror of S00. Signature motif resolves fully into code.
- On-slide: talk title, speaker name, links (provider repo, jamfpy, contact/socials) [OPEN Q12],
  "Questions".

Split into `s17` Questions and `s18` Links. Q12 left the URLs, contact and socials as a TODO.

#### S16b (optional) - By the numbers [OPEN Q10]

Only build if approved. Source background doc offers: Apr 2025 solo start to May 2026 v1.0.0;
14+ contributors; 526+ PRs; 1,902 commits; 127 Terraform files; 19,000+ lines of HCL. Layout:
large stat grid, `--f-display` numerals, `--fs-caption` labels.

Approved (Q10) and built as `s16b`. SQ8 clarified what the Apr 2025 start was: provider
development, not migration - nothing was imported before November 2025. A TODO covers whether to
show the pre-November timeline.

### 2.5 Open questions index

> SUPERSEDED. All 17 were answered in Round 1 or settled without an answer; what remains open is
> tracked as TODO chips in the deck and tabulated in AGENTS.md. Kept because three chips in
> `index.html` still cite their question numbers (`TODO Q1`, `TODO Q9`, `TODO Q12`).

Q1 palette/branding and logo assets. Q2 fonts. Q3 build target confirmation. Q4 Release Please vs
CalVer contradiction. Q5 Vault vs HCP-native secrets. Q6 S06 truncated options and decision.
Q7 real resource names for the S10 diagram. Q8 what "leveraged AI" means publicly. Q9 real vs
representative HCL, plus truncated sentences on S11/S13. Q10 include by-the-numbers slide.
Q11 tone and humour. Q12 added slides, title, credit lines, links. Q13 workspace topology and
figures. Q14 speaker notes rendering. Q15 slide budget / session length. Q16 missing rejection
rationales (per-team modules, sandbox). Q17 demo scope and fallback.

---

## 3. The source narrative

> Joseph's account, supplied 30 Jul 2026. This is the raw input that turned the deck into a story.
> Reproduced as written apart from punctuation. The facts here are settled and restated in
> AGENTS.md; the phrasing is kept because it is the record of how it actually went.

### 3.1 The account

We needed to migrate 3 instances, and a long discussion was held around how to do that. At the
time we had sandbox, staging and prod. Sandbox has no parity, staging was supposed to have parity
and prod was prod but with no history/way to make it in line with staging. We thought about doing
staging first, then prod, but that would mean importing two sets of configuration with diff
because of the lack of parity. Despite the risk, we elected to migrate prod first, because with
the right controls (no edit access on the API integration/key) we could import resources to state
without having a risk surface to change anything, so that's what we did.

We started with resources which were considered "singletons" - these are the resources there is
only ever one instance of, basically various settings panes. These don't even need "importing" as
you can just set up a resource with matching params to what the UI shows and apply it - it'll
attempt to change it but nothing will actually happen because of the single instance. We did this
for all the settings resources pretty quickly - basically in a day. One blocker we did have
however is that Lloyds banking group impose sentinel policies for Terraform which mean you cannot
actually use an "import" block - and we have no CLI access for PRD workspaces. Therefore we had to
spend some time, and pull some strings to get the policy excepted. Why is blocked might you ask?
Well, terraform is used for many many things at LBG - primarily all of our public cloud (Azure,
GCP) resources, and it would mean one person can import and manipulate other people's
configuration. So we had to submit an exception (time bound, for the window) every time we wanted
to do some runs. Later down the line we explained to the sentinel team that we didn't need this
because we were the sole actors and they put in a lifetime exception.

The flow from this point on was effectively:

- identify the next resource to migrate from the matrix we'd made
- Write a small python script leveraging JamfPy to generate a local map with all the attributes -
  even if there were duplicates
- Pipe that into a for_each with conditionals and dynamic blocks
- Apply it with no changes (so now we controlled the config)
- Up to this point, all the work was Gordon
- then I, Joseph, would comb over multiple passes reducing the duplicates, mapping ids (so
  category_id = integer for a script would become
  category_id = local.category_ids["category_name"]) - we'd make locals for easier access from the
  categories resource and so on
- Keep this repetitive refinement going until It was as efficient as it could be, ensuring no diff
  each time.
- Repeat

At this point we just had one directory called terraform/jamfpro. This was becoming a bit of a
burden due to all of the instance specific conditionals. We had stupid conditionals reading the
FQDN and then assuming things for each deployment. It got a bit out of hand, so toward the latter
stages (we're into march now) we pivoted to a module-model in which the instance specific stuff
had it's own folder.

### 3.2 The repository tree

Remembering per 1 instance of Jamf Pro, there are three Terraform cloud workspaces to cover it
because of the resource split and blast radius.

The deck's `s15b` shows a trimmed version of this - modules and roots only, with the payload
directories described in prose. This is the full shape:

```
terraform/
|-- modules/
|   |-- iam_main/
|   |   |-- privilege_sets/
|   |   |   |-- account_groups/
|   |   |   |   |-- priv_set_x.json
|   |   |   |   `-- ...
|   |   |   |-- accounts/
|   |   |   |   |-- priv_set_x.json
|   |   |   |   `-- ...
|   |   |   `-- template.json
|   |   |-- main.tf
|   |   `-- ...
|   |-- profiles_policies_main/
|   |   |-- policy_descriptions/
|   |   |   |-- desc_x.txt
|   |   |   `-- ...
|   |   |-- profiles/
|   |   |   |-- x.mobileconfig
|   |   |   `-- ...
|   |   |-- profile_staging_only/
|   |   |   |-- x.mobileconfig
|   |   |   `-- ...
|   |   |-- self_service_icons/
|   |   |   `-- .png
|   |   |-- main.tf
|   |   |-- policy1.tf
|   |   `-- ...
|   `-- root_main/
|       |-- app_installer_descriptions/
|       |   |-- x.txt
|       |   `-- ...
|       |-- mac_app_descriptions/
|       |   |-- x.txt
|       |   `-- ...
|       `-- script/
|           |-- thing.sh
|           `-- ...
`-- prod/
    |-- lbgstaging/
    |   |-- iam/
    |   |   `-- main.tf/
    |   |       |-- -> calls module above
    |   |       |-- specific_to_here.tf
    |   |       `-- ...
    |   |-- profiles_policies/
    |   |   |-- -> calls module above
    |   |   |-- ...
    |   |   |-- specific_to_here.tf
    |   |   `-- ...
    |   `-- root/
    |       |-- -> calls module above
    |       |-- ...
    |       |-- specific_to_here.tf
    |       `-- ...
    `-- lbgbusiness/
        |-- iam/
        |   |-- -> calls module above
        |   |-- ...
        |   |-- specific_to_here.tf
        |   `-- ...
        |-- profiles_policies/
        |   |-- -> calls module above
        |   |-- ...
        |   |-- specific_to_here.tf
        |   `-- ...
        `-- root/
            |-- -> calls module above
            |-- ...
            |-- specific_to_here.tf
            `-- ...
```

---

## 4. Round 1 - open questions

> Asked against the first build, 29 Jul 2026. Questions as put, answers as given.

### Q1 - Palette, branding, logo assets

The colour palette in the deck is a placeholder (dark grey/green/blue). Also, S00 shows a
plain-text "JNUC 2026" mark bottom-right - no logo asset supplied.

- Do you have a brand direction / colour preferences (LBG colours? JNUC branding? keep the current
  dark theme)?
- Any logo files to embed (JNUC mark, LBG, provider logo)? They'd need to be embeddable (SVG/PNG
  to inline as data URI).

**Answer:** Remove JNUC 2026 for now, and add "placeholder-logo". Let's flip the colour scheme to
be a light background, but similar style. Use the Lloyds banking group font if you can.

### Q2 - Fonts

Slide titles currently use a placeholder serif (Georgia); body is the system sans stack; code is
system mono. Everything must be system-stack or embedded (no webfont fetches).

- Preferred typefaces, or happy with the placeholders? As in Q1, try to use the LBG one, GT-ULTRA

**Answer:** (answered inside the question - GT Ultra, with system fallbacks, still a placeholder
until brand assets arrive.)

### Q4 - Release Please vs CalVer contradiction

S01 lists "Release Please for versioning and release tagging" as a constraint, but S04 says
semantic versioning was rejected in favour of calendar versioning. Release Please is semver-native,
so the two statements conflict as written.

- How do these fit together (e.g. Release Please configured differently, CalVer via another
  mechanism, or one statement wrong)?

**Answer:** We started as release-please but realised the candence was too hard to keep up with,
and the numbers/release times needed more tracking. So now we use calendar versioning instead to
keep things more visible nad consistent.

### Q5 - Vault vs HCP-native secrets end-state

S01 and S03 both name HashiCorp Vault, but the end-state is unclear: self-hosted Vault, HCP Vault,
or HCP Terraform's native variable sets/secrets?

- What is (or will be) the actual secrets end-state?

**Answer:** It's an internally hosted vault, accessed via human access to initially set things and
then the terraform code accesses via datasources.

### Q6 - Resource migration path (S06)

The source cut off mid-sentence. Option A: one resource type end-to-end across all instances, then
the next. Option B was truncated at "Migrate one" - the deck currently presumes "migrate one
instance completely, then the next".

- Is the presumed Option B wording right?
- Which option did you choose, and why?

**Answer:** Everything was migrated in-place in the production instance first, one resource at a
time. They were all imported very verbosely then moved {} into more efficient for_each blocks.

### Q7 - Real resource names for the S10 diagram

The five-tier sequence diagram currently has generic band labels (singletons, dependency targets,
1-2 deps, 2+ deps, policies).

- Which actual resource types sat in each band? (e.g. which were the singletons, which were the
  shared dependency targets like categories/scripts/groups, etc.)

**Answer:** Add a ToDo for Gordon Deacon for this

### Q8 - What "AI-assisted" means publicly

S11 says "AI-assisted where it helped" and S14 gate 2 says AI-assisted checks confirmed each
resource exists with correct dependencies (since HCP state isn't locally inspectable).

- What specifically was AI used for, and what are you comfortable saying publicly at a conference?

**Answer:** AI was used to validate configuration and depenency links, mostly just copilot cli.

### Q9 - Real HCL, and two truncated sentences

- S12's code comparison uses a representative `jamfpro_category` example. Do you want to supply
  sanitised real HCL instead, or keep the representative example?
- S11: the rejection of `terraform plan -generate-config-out` - source truncated at "Instead
  wanted". The deck presumes: "we wanted one block per resource type driven by data". Correct?
- S13: anything more specific on why policies/dock items broke the map pattern (nested payloads,
  scope blocks)?

**Answer:** Let's use real stuff.

### Q11 - Tone and humour

Two lines were formalised from the source; say if you want the originals back (or something in
between):

- S04 workspace rejection: source had "boom boom" energy around the 500/1,500/5,000 figures -
  currently rendered straight.
- S08 step 3: source said revoke permissions "so that people are not cheeky buggars" - currently
  "no side-door edits mid-import".

**Answer:** Let's be more professional but not boring

### Q12 - Title, credit line, links

- Confirm the talk title: "From Clicks to Code - Migrating Jamf Pro to Terraform at Lloyds Banking
  Group"?
- Exact credit line on S00 (currently: "Co-builder and co-owner of the deploymenttheory/jamfpro
  Terraform provider")?
- S17 links: provider repo URL, jamfpy URL, contact/socials to show?
- Where to mention jamfpy is yours - S11 (tools) or S17 (closing)?

**Answer:** Talk title good. Remove the credit line and add a placeholder "who we are" page. Then
add a placeholder "links" page at the end.

### Q13 - Workspace topology and figures (S15)

S15 currently shows only the 500 / 1,500+ / ~5,000 figures. The intended chart needs:

- How the estate was split into workspaces (topology - by what dimension?)
- Workspace count
- Resources per workspace (for the chart)
- Plan execution times before/after, if you have them

**Answer:** add a ToDo for the topology of repo dirs -> workspaces and make a whole slide for it.

### Q15 - Slide budget / session length

How long is the session slot? 19 slides currently (18 + optional stats slide). Anything to cut or
expand?

**Answer:** This talk is 30 minutes and 3 people will be speakin.

### Q16 - Missing rejection rationales (S04)

Two rejected ideas have no stated rationale in the source:

- **Per-team Terraform modules** - deck currently presumes conflict with single-source-of-truth.
  Actual reason?
- **Sandbox inside the route to live** - trialled then removed. Why?

**Answer:** Too much approval complexity internal, sandbox is only a CLI instance now. Add a ToDo
for mentioning a dev-test instance

### Q17 - Demo scope and fallback (S16)

- What will the live demo actually show (so the holding-slide caption can list it)?
- Fallback preference if the demo environment dies: screenshots, recording, or skip?

**Answer:** There is no demo, remove it for now.

### Settled without an answer

**Q3** single self-contained HTML file, no framework. **Q10** "By the numbers" slide included.
**Q14** speaker notes omitted from the file. Q14 was later reversed: notes now ship in a hidden
`<aside class="notes">` on every slide and drive the presenter view.

---

## 5. Round 2 - slide-by-slide corrections

> A read-through of the rebuilt deck, 29 Jul 2026. Slide numbers are positions in the then-current
> deck (1 title, 2 who we are, 3 = S01, 4 = S02, 5 = S03, 6 = S04, 7 = S05, 8 = S06, 9 = S07,
> 10 = S08). Verbatim below; AGENTS.md's TODO table reads slides 7 and 9 as S07 and S09, and the
> chips that exist today are on `s07` (more prep points) and `s10` (resource-type names).

**Slide 1**

Second subtitle line is not needed.

**Slide 3**

the RTL is devtest -> Staging -> prod

**Slide 4**

It's Support, Mac@LBG, Security, App Packaging & Deployment

**Slide 5**

All the numbers on this page are wrong. It goes 2-1-5-3...

Add an abbreviation for PA

One of the instances is CLI triggered not VCS, but close enough

Simplify point 8, it's confusing

**Slide 6**

Add a ToDo to expand on the internal approval complexity

Managing everything with Terraform can be changed to "static group membership unmanaged to improve
support experience (no PR for troubleshooting)", but update thr wording

**Slide 7**

Add a ToDO on this whole slide so I can explain why

**Slide 9**

ToDo to add more points

**Slide 10**

(no comment given)

---

## 6. Round 3 - story questions

> Asked against the source narrative in section 3, 30 Jul 2026. These are the answers that
> produced the settled-facts list in AGENTS.md.

### Proposed running order

Context -> decisions -> first wins -> the wall -> the loop -> growing pains -> payoff:

1. Title
2. Who we are
3. Context, requirements, constraints (adds: the parity reality - sandbox no parity, staging
   supposed to have parity but didn't, prod with no history)
4. Who touches Jamf Pro
5. Objectives and design decisions
6. Ideas rejected up front (single workspace, per-team modules, manage-everything - see SQ9 re the
   other two)
7. Instance order: the staging-first vs prod-first debate, and the controls that made prod-first
   safe
8. Instance prep
9. NEW - First wins: singletons in a day (the no-import-needed trick)
10. NEW - The wall: Sentinel blocks import blocks; per-window exceptions; eventual lifetime
    exception
11. Resource migration path (per resource type, in place, in prod)
12. Resource sequencing (the matrix / 5 tiers) + visualised
13. Migration wave workflow (freeze, revoke, import, validate, document, announce)
14. Tools and helpers (JamfPy script -> map -> for_each) + the Gordon/Joseph split
15. for_each comparison (verbose import -> refined)
16. NEW or folded into 15: the refinement passes (dedup, id -> local name mapping, zero-diff gate,
    repeat)
17. for_each exceptions
18. Validating a migration
19. NEW - Growing pains: one terraform/jamfpro dir, FQDN conditionals out of hand -> March module
    pivot
20. NEW/reworked - The topology: modules + per-instance dirs, three workspaces per instance
    (replaces the placeholder repo->workspace slide)
21. Workspace optimisation figures
22. By the numbers
23. Questions
24. Links

**Answer:** (no veto given - adopted, then trimmed from 27 slides to 23 to fit the 30-minute slot.
Items 11 and 12 merged into `s10`, item 16 folded into `s12`, item 21 merged into `s15b`.)

### SQ1 - Instance inventory

story.md says "we had sandbox, staging and prod" and "we needed to migrate 3 instances". The deck
(per your earlier amendment) says the route to live is DevTest -> Staging -> Production, with
sandbox now a CLI-only instance outside the RTL. The module tree shows only `prod/lbgstaging` and
`prod/lbgbusiness`.

- What are the three migrated instances, by name?
- Is today's DevTest the old sandbox renamed/repurposed, or a separate fourth instance?
- `lbgstaging` sits under a top-level `prod/` folder - what does `prod/` mean there (TFC project?
  environment tier?), and where does the third instance's config live? Is the third the
  CLI-triggered one, hence no VCS directories for it?

**Answer:** Devtest was actually brought in very recently, and there is little ambiguity on what's
used for what. Assume sandbox at first and add devtest later down the line with a TODO for a mac
engineer to clarify.

### SQ2 - After prod

story.md covers the prod import end-to-end but stops before the other instances. How did staging
and the third instance come under management afterwards - the same import flow repeated per
instance, or the modules applied fresh with drift reconciled by hand?

**Answer:** We effectively just nuked staging bar some important items (APNS, cloud IDP) and then
pointed the config for Prod at it. there were many errors and it took a lot of refinement, but it
worked eventually and achieved relatively "easy" parity. Make this a highlight of the story. Add a
ToDo for a mac-engineer to clarify.

### SQ3 - The controls that made prod-first safe

"with the right controls (no edit access on the API integration/key) we could import resources to
state without having a risk surface to change anything."

- Does this mean the Terraform API client was scoped read-only during the import phase (state
  could be populated, nothing could be written), then widened once a resource type was fully
  managed?
- Or that humans were locked out of editing the API integration/key itself?
- Who held the ability to change those scopes?

**Answer:** Yes, it could not change things in the server. It would not know that as for import it
only reads. It was widened once we knew the import was stable and there was no re-occuring diff.
Myself and Gordon held those keys.

### SQ4 - Sentinel, publicly

Confirming the mechanics and what you're happy saying on stage:

- No CLI access for PRD workspaces, so imports ran as VCS-triggered runs using `import` blocks -
  which LBG's Sentinel policies block org-wide, because Terraform covers all public cloud (Azure,
  GCP) and import would let one person pull other people's resources into their own state.
- You filed a time-bound exception every time you wanted a run window, and had to pull strings to
  get it.
- Later you explained you were the sole actors on these workspaces and the Sentinel team granted a
  lifetime exception.

Anything wrong or missing? Comfortable naming Sentinel and the exception process at a conference?

**Answer:** Correct. Correct, and correct.

### SQ5 - The singleton trick

My reading: settings-style resources are single-instance, so you don't import at all - you write a
resource with params matching the UI and apply; Terraform "creates" it but the write is
effectively a no-op because the values are identical, and now it's in state. Correct enough to
state on a slide? And keep the "all settings resources in about a day" claim?

**Answer:** Correct.

### SQ6 - The matrix

"identify the next resource to migrate from the matrix we'd made" - what was the matrix (a
spreadsheet of resource types vs dependencies/owners/counts?), and is it the thing that produced
the 5-tier sequencing already on the deck? Worth showing a sanitised version, or keep the tiers as
the visual?

**Answer:** It was a spreadsheet which we made as a group. Just refine what's there, I like it, and
keep the Todo for gordon to refine the actual items.

### SQ7 - People and the split

"Up to this point, all the work was Gordon" - Gordon Deacon, I assume. OK to name the division of
labour on-slide (Gordon: per-resource scripts and verbose import; Joseph: refinement passes -
dedup, `category_id = 5` -> `local.category_ids["Name"]`, locals for cross-resource access, zero
diff after every pass)? And is Gordon one of the three speakers - and who is the third?

**Answer:** Yes, yes, yes. Dafydd Watkins is the third.

### SQ8 - Timeline anchors

"we're into march now" - March 2026? Rough dates wanted so the story has a spine: prod import
start, singletons day, per-window exceptions period, lifetime exception, module pivot, all
instances done. And how does "Apr 2025 -> May 2026, solo start to v1.0.0" (By the numbers slide)
fit around this - what was the Apr 2025 solo start, groundwork before the prod import began?

**Answer:** Yes. Singletons were November, bulk in December/Jan, refinement through feb and march.
Nothing was imported before November. Before that it was all provider development. Add a possible
to do for timeline prior to nov 25.

### SQ9 - Rejected-ideas placement

For story flow I'd keep the up-front rejected card for the architectural calls (single workspace,
per-team modules, managing everything), and move the other two to where they happened in the
journey: CalVer (started Release Please, cadence unsustainable) and sandbox-out-of-the-RTL as later
refinements near the module pivot. OK, or keep all five together up front?

**Answer:** Perfect, the calver was much later around the time of dev-test.

### SQ10 - Workspace numbers

With the module model: three workspaces per instance (iam / profiles_policies / root). What's the
total workspace count for the optimisation slide, and do you have plan-time figures (before/after
the split), or shall I keep those as TODO chips?

**Answer:** We've always had 3 per instance for staging/prod. Devtest (recent addition is only 1
CLI workspace). Sandbox add a todo to clarify.

---

## 7. Decision index

Every question, its outcome, and where it landed. Round 1 questions are Qn, Round 3 are SQn.

| Ref | Decision | Landed |
|---|---|---|
| Q1 | Light theme, LBG green, placeholder-logo chip instead of a JNUC mark | Token block, `s00` |
| Q2 | GT Ultra with system fallbacks, still placeholder until brand assets | Token block |
| Q3 | Single self-contained HTML file, no framework | Whole build |
| Q4 | Release Please first, cadence unsustainable, switched to CalVer | `s01` constraint reworded, `s-today` |
| Q5 | Internally hosted Vault, set by humans, read via data sources | `s01`, `s03` |
| Q6 | In place in production, one resource type at a time, verbose then `for_each` | `s10` intro |
| Q7 | Real resource-type names per band | Open TODO, Gordon Deacon, `s10` |
| Q8 | AI-assisted validation of config and dependency links, mostly Copilot CLI | `s11`, `s14` gate 2 |
| Q9 | Use real sanitised HCL | Open TODO, `s12`; wording chip on `s11` |
| Q10 | Include the by-the-numbers slide | `s16b` |
| Q11 | Professional but not boring | Whole deck |
| Q12 | Title confirmed; credit line out; "who we are" and "links" pages added | `s00`, `s00b`, `s18` |
| Q13 | Build a real topology slide, repo dirs to workspaces | `s15b` |
| Q14 | Reversed: notes ship hidden in the HTML and drive presenter view | Every slide |
| Q15 | 30 minutes, three speakers | Trim to 23 slides |
| Q16 | Per-team modules rejected on internal approval complexity; sandbox is CLI-only | `s04`, `s-today` |
| Q17 | No live demo | S16 removed |
| SQ1 | Sandbox first, DevTest added recently | `s01`, `s-today`, TODO for a Mac engineer |
| SQ2 | Staging was nuked bar APNS and cloud IdP, then prod's config pointed at it | `s-staging`, the highlight |
| SQ3 | Read-only API client during import, widened once stable; Joseph and Gordon held the keys | `s05` |
| SQ4 | Sentinel can be named publicly, mechanics confirmed | `s-sentinel` |
| SQ5 | Singleton no-import trick confirmed, one day for all settings resources | `s-singletons` |
| SQ6 | The matrix was a group-built spreadsheet | `s10` intro |
| SQ7 | Gordon scripts and verbose imports, Joseph refinement passes; Dafydd Watkins is the third speaker | `s00b`, `s12` |
| SQ8 | Singletons Nov 2025, bulk Dec-Jan, refinement Feb-Mar; nothing imported before Nov 2025 | Timeline strip, `s16b` TODO |
| SQ9 | CalVer and sandbox-out-of-RTL move to where they happened | `s04` trimmed, `s-today` |
| SQ10 | Three workspaces per instance for staging and prod, one CLI workspace for DevTest | `s15b`, sandbox TODO |
