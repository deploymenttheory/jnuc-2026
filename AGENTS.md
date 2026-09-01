# AGENTS.md

Reference for anyone (human or agent) working on this repo. Keep this file current: update it
in the same change whenever anything here becomes inaccurate or stale.

## What this repo is

Home for all public JNUC 2026 materials. It holds more than one conference talk. Each talk is
a self-contained folder under `presentations/`.

| Deck | Status |
|---|---|
| `presentations/migrating_an_instance` | Ported in and being worked on. Full detail below. |
| `presentations/training_a_team` | Content work ongoing, slide by slide. Full detail below. |

`presentations/index.html` is the landing page rather than a deck. It serves the site root and
links to each deck by hand, so a new deck needs a card adding to it. Each card carries two
links: "Open deck" and a Keynote download. The HTML deck is the source of truth - the `.key`
is built from it on a Mac and committed. See Building the downloads.

**Both decks follow the Jamf-supplied JNUC 2026 Keynote template** (`template.key` at the repo
root, committed as the canonical style reference). The template's mandatory slides appear
directly in each deck - a session-title slide carrying the speakers, a "Questions? Your turn!"
slide and a Thank You close - and every other slide keeps its own content but adopts the
template's formatting. The template look: royal blue `#273FAB` canvas, dark navy `#152143`
panels/alternate ground, lime `#D1F682` as the single accent, off-white `#F4F4F4` text,
cornflower `#5E79D7` for secondary data series, HelveticaNeue (stack:
`"Helvetica Neue", Helvetica, Arial, sans-serif` - no webfonts), cube-wireframe background
pattern, jamf + JNUC 2026 logos (embedded as data URIs, extracted from the template). The
landing page keeps its own near-black look - it is not a deck.

## Layout

| Path | Role |
|---|---|
| `presentations/<slug>/` | One talk. Snake-case slug. Each deck owns its own HTML, tokens and script; decks do not import from each other beyond `_shared/`. |
| `presentations/_shared/` | Data used by more than one deck: `speakers.js` and `qr-code.png` (the training deck's take-it-with-you code). Content, not styling - see below. |
| `presentations/<slug>/art/` | Source art for anything a deck embeds as a data URI: one Markdown Pixelforge spec plus the PNGs exported from it. Deploy excludes `*.md`, so the spec is kept for regeneration only; the PNGs ride along but nothing links to them, because the deck carries its own base64 copy. Currently only `migrating_an_instance/art/`. |
| `presentations/sandbox/` | Feedback review pages, one sandbox per deck: a shared `sandbox.css`, a minimal chooser `index.html`, and one subdirectory per deck (`migrating_an_instance/`, `training_a_team/`) each with its own hand-maintained `index.html` listing that deck's pages, one page per change showing three implementation options as live renders of the real slide. Deploys with the site at `/sandbox/`, linked from a Sandbox button on each deck card on the landing page (added 2026-08-27 at Joseph's request; split into one sandbox per deck the same day). See Sandbox. |
| `template.key` | The Jamf-supplied JNUC 2026 Keynote template. Canonical reference for palette, typography and mandatory slides. |
| `.github/workflows/` | `deploy.yml` only - the S3 sync and CloudFront invalidation. See Deployment. |
| `tools/` | `build-key.mjs`, which builds the Keynote downloads from the decks on a Mac (the only thing `package.json` exists for), and `sandbox-template.html`, the starting point for every sandbox review page. |
| `feedback-workflow.md` | The deck feedback loop: standing rules, orchestrator and slide-agent roles, brief templates, commands, recovery steps and a log. Read it before touching a deck in response to feedback. Not shipped (`*.md` is excluded from the deploy). |
| `docs/superpowers/plans/` | The first-round implementation plan, superseded by `feedback-workflow.md` and kept for its triage table. Not shipped. |
| `docs/timeline-notes.md` | Authoritative for slide order, speaker and timeline correspondence in both decks: one four-column table per deck (slide number, title, speaker, time notes), the notes column left for Joseph to say whether and where a slide should highlight the timeline strip. Where this file's slide-order or speaker lists disagree with it, this doc wins and those lists get corrected to match. Not shipped. |
| `README.md`, `LICENSE` | Repo boilerplate. |

The decks have no build step. Node is in this repo purely for `tools/build-key.mjs`, which is
run by hand on a Mac; nothing about editing a deck requires `npm install`.

## Shared speaker data

`presentations/_shared/speakers.js` is the single source of truth for who is speaking. It
sets `window.JNUC_SPEAKERS`, keyed by `dafydd` / `joseph` / `gordon`, each with `name`,
`initials`, `org`, `role`, `bio` and `photo` (a self-contained data URI, or `null`).

- It is loaded with a plain `<script src="../_shared/speakers.js">`, not `fetch`. `fetch` on
  a `file://` page is blocked by CORS; a classic script tag is not, so the decks still work
  opened straight off disk. Verified in headless Chrome over both `file://` and `http://`.
- The fields are a **superset**. Each deck renders only what its own layout uses, in its own
  order, with its own classes, from a small render block just before its main script.
- Strings are plain text, injected with `textContent`, so write `&` not `&amp;`.
- **Both decks now render the template's three-speaker title-slide cards** from this file:
  photo square (or an initials placeholder while a photo is missing), NAME AND SURNAME in
  caps, the role + org line in lime, and the bio. Speaker order on both title slides:
  Joseph, Gordon, Dafydd. All three speakers have photos (Joseph and Gordon added
  2026-08-27).
- `migrating_an_instance` keeps hardcoded names in the title cards as a fallback so the
  opening slide is never blank if `_shared/` goes missing; the shared file overwrites them on
  load and always wins.

`_shared/` must ship anywhere a deck ships. A deck copied out on its own loses its speakers.

## House rules for every deck

These apply to any deck in this repo, current or future.

- **Adhere to the JNUC 2026 template** (`template.key`). Mandatory slides transfer directly
  (title with speakers, Questions, Thank You); everything else adopts the template's
  formatting - palette, HelveticaNeue stack, title/kicker treatment, footer chrome.
- One HTML file per deck, holding its own CSS, JS and images. Zero requests off the machine:
  no CDNs, webfonts, remote JS or remote images. The only local files a deck may reference
  are in `../_shared/` (`speakers.js`, and `qr-code.png` where used). A deck must work opened
  straight off disk.
- All styling derives from the token block in that deck's `:root`. Never hardcode a
  colour/font/size in slide markup - add a token if a new value is needed.
- **Never invent facts, numbers, resource names, or rationale.** Anything unconfirmed gets an
  amber TODO chip: `<span class="todo">TODO: ...</span>`.
- **Titles are plain and human.** No colon-glued two-part titles ("The Wall: How We Hit It")
  and no clever fragment titles ("The shape that stuck"). Write titles the way a person
  would: "Getting past Sentinel", "The module structure", "Rebuilding staging".
- Visible keyboard focus states on anything interactive.
- British English. No emojis. No em-dashes - plain hyphens only (user preference, applies to
  every deliverable in this repo).
- Tone: professional but not boring.
- 1920x1080 canvas scaled to viewport; arrow/space/Home/End navigation, plus single-finger
  horizontal swipe on touch devices (60px threshold, pinches and vertical drags ignored);
  URL hash per slide; respect `prefers-reduced-motion`.
- Every slide carries speaker notes (in `migrating_an_instance` a hidden
  `<aside class="notes">` as the section's last element; in `training_a_team` a `data-notes`
  attribute). Notes are delivery cues in full sentences; they ship inside the HTML, so keep
  them safe for public reading or strip them from any copy that gets distributed.
- Nothing in a deck may depend on where it is served from. The presenter window opens off
  `location.pathname`, which is why the move into `presentations/` needed no code change -
  keep it that way.
- **The build interface is load-bearing**: `section.slide` elements, an `.active` class on
  the current slide, and ArrowRight advancing exactly one slide with no intra-slide
  fragments. `tools/build-key.mjs` depends on all three and fails loudly if a deck stops
  advancing.

The presenter view and reader mode below are implemented inside `migrating_an_instance`'s
`index.html`, not in shared code. A second deck wanting them has to copy the pattern across.
If that happens, that is the first real candidate for `_shared/`. The speaker overlay is
already in that position: both decks have one, each with its own markup, styling and key
handler, sharing only the `data-speaker` / `data-speaker-note` attribute contract. Change
one and the other does not follow.

## Deck: presentations/migrating_an_instance

**"From Clicks to Code - Migrating Jamf Pro to Terraform at Lloyds Banking Group"**.
30-minute slot, three speakers: Joseph Little, Gordon Deacon, Dafydd Watkins (all LBG).

### Files

| File | Role |
|---|---|
| `index.html` | The deck. Needs `../_shared/speakers.js` alongside it for the title-slide speaker cards. |
| `from-clicks-to-code-jnuc2026.pptx` | Gone. The download is now the committed `.key` below. |
| `from-clicks-to-code-jnuc2026.key` | The committed Keynote download, written by `tools/build-key.mjs`. The landing page links to this exact filename, so it is set in the script, not chosen freely. Rebuild and commit it with any deck edit. |
| `presenter.json` | Per-slide speaker notes and timer lengths plus the 30-minute talk limit. Notes are a copy of the deck's `<aside class="notes">` text and the slide order mirrors the deck - the deck wins when they differ, and `feedback-workflow.md` carries a check that must print `OK` before every push. Regenerated from the deck on 2026-08-27 (timers kept). Timer allocations are proposed, not rehearsed. Nothing reads this file yet. |
| `art/` | Source art for the pixel-art icons that used to sit on slide 16: `s-staging-steps.md` (the Pixelforge spec - palette, rules and prose for all three) and `s-staging-wipe.png` / `s-staging-apply.png` / `s-staging-iterate.png`, 1024px square (Pixelforge's ceiling; redrawn at that size 2026-08-28, up from 384px), exported at scale 1. The icons came off the slide 2026-09-01 ("for now"); these files are unused but kept so the art can come back. See Embedded artwork below. |
| `spec.md` | Spec and change history: the original build runbook, Joseph's source narrative and full repo tree, all three Q&A rounds answered inline, and a decision index. **Historical** - sections marked SUPERSEDED (deck order, palette values, open-questions index) predate the story restructure, and everything it says about the light LBG-green palette predates the JNUC template adoption. |

`spec.md` is provenance for every fact in the deck. Do not delete it; do not treat its
superseded sections as current. This file wins wherever the two disagree on story facts.
Note that `spec.md` predates the move into `presentations/`, so any repo tree or path it
quotes is stale.

### Deck-specific authoring rules

- **Palette and type are the JNUC template's**, wired through the deck's token block: royal
  blue stage, navy panels and code blocks, lime accent, off-white text, cornflower reserved
  for navy surfaces, HelveticaNeue stack. Code blocks map hand-tokenised HCL to lime
  keywords, light-cornflower strings and amber numbers; TODO chips are solid amber with navy
  ink. Logos (jamf white, JNUC 2026) live in tokens as data URIs.
- **Embedded artwork.** Everything the deck draws with an image is a data URI in the HTML,
  because the deck has to work opened straight off disk. Currently that is only the logos -
  white-on-transparent SVGs living in tokens. Slide 16 used to carry three multicolour
  pixel-art step icons inline as `<img class="s-staging-art">`; they came off the slide
  2026-09-01 ("for now") and the deck currently embeds no raster art. If they (or any other
  pixel art) return: this deck has **no theme system** - no `[data-theme]` blocks, no
  `--art-mono-filter` or `--art-plate` knobs (those belong to `training_a_team`) - so
  embedded art gets no per-theme filter or backing plate here; the stage is always royal
  blue and the cards always navy, so new pixel art should carry a dark outline (the removed
  icons used `#0A1030`) that reads on both. New art must be sized in tokens. Pixel art
  carries `image-rendering: pixelated` only when the source is at or near its display size;
  the removed icons were 1024px shown at 168px, and at that ratio nearest-neighbour throws
  away five source pixels in six and shreds the outlines, so they used `image-rendering:
  auto` and let the browser downscale smoothly (Chrome treats `crisp-edges` as nearest, so
  it is not a third option). Source files and the Pixelforge spec go in the deck's `art/`
  directory, never linked.
- **Dates live on the persistent timeline, not in slide content.** A `<section>` carries
  `data-when="YYYY-MM"` or `data-when="YYYY-MM:YYYY-MM"` (a month range), `data-when="now"`
  (see below), or carries no `data-when` at all. A fixed strip at the bottom of the stage
  runs Nov 2025 -> Mar 2026 -> Now (six stops: Nov 25, Dec, Jan 26, Feb, Mar, Now); the
  active slide's range is highlighted, earlier months tinted. The title slide and the three
  pre-migration context slides (landscape, who touches Jamf Pro, what a workspace is) carry
  no `data-when`, so the strip stays blank through them - there is nothing to highlight
  until the story reaches its first dated slide. From there, keep positions monotonically
  non-decreasing through the deck. Don't add per-slide date chips. Elements that sit near a
  slide's bottom-left must clear the strip - use the `--tl-clear` token for their bottom
  offset. The template's brand footer (jamf + JNUC logos) appears on the title, Questions
  and Thank You slides only, sitting above the strip; content slides keep the timeline strip
  and counter as their bottom chrome - the two would collide otherwise, and the strip is
  deck content. `now` is a sentinel, not a real month: the script's `MONTHS` array carries
  it as its last entry, so the existing `indexOf` lookup matches it exactly like any
  `YYYY-MM` value with no other parsing change. It is only ever used bare (`data-when="now"`),
  never in a range. Currently `#s16b` (By the numbers) is the only slide that advances to
  it (bright accent, since the story moves from March to now); `#s17`, `#s18` and
  `#s-thanks` repeat `data-when="now"` and render muted, carrying that state to the end of
  the deck. `#s15b` (Getting as close to DRY as we can) is the last slide before that,
  advancing to `2026-03` (bright).
- **The highlight only goes accent when the story moves.** A slide whose `data-when` range
  repeats the previous slide's renders those cells in the muted static state (via
  `#timeline.tl-static`); the month label stays accent either way. This is also how a slide
  that should not move the story forward carries the previous slide's state: it repeats that
  slide's exact `data-when` value. Omitting `data-when` does not do this - the script
  computes each slide's highlight solely from its own attribute, so an omitted attribute
  blanks the whole strip rather than carrying anything forward; omission is reserved for the
  pre-timeline slides above. Comparison is deck order, so a slide's state is fixed regardless
  of how you navigated to it, and the first slide always counts as advancing (moot when it
  has no `data-when` to render). Reordering slides or editing a `data-when` therefore changes
  which slides grey out - check the neighbours either side.
- Code blocks are hand-tokenised HCL (`tk-kw`, `tk-str`, `tk-num`, `tk-cm` spans). Diagrams
  are inline SVG using the `dg-*` primitives so they inherit tokens.
- The recurring motif is clicks vs code: UI-chrome fragments in muted text giving way to
  monospace HCL in the accent colour. Carried by the title wording rather than a drawn
  device.

### Presenter view and reader mode

- **Presenter view**: pressing `p` in the deck opens a second window
  (`?presenter=1`) showing current slide (from the section's `aria-label`), notes, next
  slide, slide count, and a click-to-reset elapsed timer. Windows sync via BroadcastChannel
  with a localStorage fallback - **sync requires serving over HTTP** (file:// windows get
  opaque origins). On stage: extended displays, audience window on the projector, presenter
  window on the laptop. `aria-label` doubles as the presenter-view title, so keep it matching
  the visible slide title.
- `presenter.json` mirrors the notes with per-slide `timerSeconds` (summing to the
  1800-second `timeLimitSeconds`). It is not wired into the presenter view; the deploy sync
  ships it to S3 (only `*.md` and `.DS_Store` are excluded), which is fine while it only
  duplicates the already-public notes.
- **Speaker overlay**: press `s`. A pill in the stage's top-right gutter showing who has
  the room on this slide, read off each section's `data-speaker` / `data-speaker-note`
  attributes. Off by default - it is a rehearsal aid, not deck content, so it never lands in
  the Keynote capture - and unassigned slides say "No speaker assigned" rather than
  inheriting the previous name. Person colours: Dafydd `--c-accent`, Joseph `--c-code-str`,
  Gordon `--c-warn`, All/Anyone `--c-text`. Top-right rather than the training deck's
  top-left because the template's corner arrow owns the top-left of the title and close
  slides. Note `data-speaker` does double duty in this deck: on a `<section>` it is the
  presenter's display name, on a `.tspeaker` card it is the `speakers.js` key.

- **Reader mode**: press `d` or open with `?reader=1`. Reveals "More detail"
  `<details class="reader-extra">` popovers on selected slides (currently s01, s05,
  s-singletons, s-sentinel, s12, s15b, s-staging) for post-presentation viewers.
  The counter shows a "reader" tag while active. Popover content follows the same
  no-invented-facts rule.

### Current slide order (story arc)

`docs/timeline-notes.md` is authoritative for slide order, speaker and timeline
correspondence. The list below is a description of the current state, kept in step by hand -
where it disagrees with the doc, this list is corrected to match the doc, not the other way
round.

Context -> decisions -> first wins -> the wall -> the loop -> growing pains -> payoff.
22 slides. Legacy section ids kept stable across reorders (so `s10` no longer sits at
position 10); new story slides use semantic ids. The bold name on each line is who
presents it, held in the slide's `data-speaker` attribute and surfaced by the speaker
overlay - keep the two in step when slides move.

1. `s00` Title (template session-title layout with the three speaker cards) - **All (intros)**
2. `s01` Landscape prior to the migration (our environment before the migration: Sandbox / Staging / Production as one three-segment chevron arrow, `clip-path` rules scoped to `#s01`, no annotations, under a "Context" heading inside the pipeline-band card; six constraints as plain rows in two bordered column panels, Requirements / Constraints, with a subgrid keeping each panel's title and row heights aligned, via `.constraints-col` and `.constraints-title` scoped to `#s01`) - **Dafydd**
3. `s02` Who uses Jamf Pro in our Org ? (five team cards, each reading team name, a one-line
   description of what that team does, then a "Performs:" label above the existing access tag,
   via `.team-head`, `.team-role`, `.team-performs` and `.team-performs-label`; the closing note
   makes the depth-and-breadth point rather than recounting the cards) - **Dafydd**
4. `s-workspace` What a Terraform workspace is (definition, HashiCorp workspace-anatomy
   diagram, four lenses that decide how an instance gets carved up) - **Dafydd (TBC)**
5. `s04` Migration outcomes we considered and rejected (3 architectural rejects; the other 2 moved into the story) - **Joseph**
6. `s05` Migration path options (three paths, each its own bordered panel with the flow diagram centred inside, chosen path's panel edged in the accent colour, prod-first chosen; the read-only API client control reads as a line inside path 03 rather than a card at the foot of the slide) - **Joseph**
7. `s07` Prerequisites (a `.slide-sub` line framing the split; two portions, instance prep
   and migration prep, each a tidied checklist, sharing a row subgrid - same technique as
   `#s01`'s constraints panels - so the heading and each checklist row line up across both
   columns) - **Gordon**
8. `s10` Resource sequencing (per-resource-type choice + matrix intro + 5-tier diagram) - **Dafydd**
9. `s-singletons` Singletons first (Nov 2025, no-import trick) - **Gordon**
10. `s-sentinel` Guardrails you don't own (blocked -> per-window exceptions -> standing exception; a `.slide-sub` line plus three `.gates-3` cards, and nothing else in the section. Moved off the shared `.lead` onto `.slide-sub` 2026-09-01 - it was the only oversized subtitle in the deck and nothing else on the slide needed `.lead`'s size. The round-one alternative wrappers came back out on 2026-08-28 when Joseph rejected them; the open sandbox page `s-sentinel-round2` is pure CSS on this markup, so the section has no slide-specific rules of its own) - **Gordon**
11. `s08` Migration wave workflow (Dec 2025 - Jan 2026 bulk; seven steps as full-width
    bands stepping down the slide, numbers in an aligned gutter, step 3's freeze marked
    with a red left edge) - **Dafydd**
12. `s11` Tools and helpers (the pipeline diagram unchanged on the left - jamfpy -> script
    -> map -> for_each -> import; on the right the same four points as a numbered list, 1
    to 4 in mono in an accent gutter, each name in the display face, bold: PRUNE and
    jamf-resource-deleter, jamfpy, the regex mop-up pass, and `--generate-config-out`
    rejected, its number and name both in the danger colour. Option D, accepted
    2026-08-28. Cut back from seven bullets 2026-08-28; the three that went are told by
    the diagram or by `s12`, and the "mostly Copilot CLI" mention left the slide with
    them) - **Gordon**
13. `s12` Dynamic creation with for_each (comparison + the refinement passes, Gordon/Joseph split) - **Joseph**
14. `s13` for_each exceptions (single statement - policies stayed in plain HCL because
    they are too diverse for one map) - **Joseph**
15. `s14` Validating a migration (the `terraform plan` block reads as a real terminal
    window - light chrome bar, red/amber/lime traffic-light dots, a centred
    `joseph@jnuc - zsh` title, and a blinking cursor on a fresh prompt line below the
    result; four gate cards unchanged) - **Joseph**
16. `s-staging` Rebuilding staging (the highlight; sits before the module pivot it caused;
    a numbered run of the three steps down the left on a rail, verb and sentence on one
    line each, with the lead and the takeaway as a quiet right-hand column. The pixel-art
    icons that used to ride beside each ring came off 2026-09-01 at Joseph's request ("for
    now"); the rings and rail carry the sequence on their own. Sources stay in `art/`,
    unused for now) - **Dafydd**
17. `s-pivot` One codebase for every instance (rewritten 2026-08-28 with `s15b` as one arc:
    context, problem, techniques. The DRY objective in an accent band, then a real
    `jamfpro_static_computer_group` block whose `assigned_computer_ids` are the only amber
    thing on the slide, against a shared / unique-to-one-instance breakdown. Closes on "The
    resource is shared. Part of its configuration cannot be." Rules are `#s-pivot .dry-*`)
    - **Joseph**
18. `s15b` Getting as close to DRY as we can (the second half of that arc: six techniques in
    a three by two grid, each carrying the syntax you actually write - input variables, local
    values, data sources, child modules (marked as what the estate runs), configuration as
    data, Terragrunt - over a caution that CLI workspaces share a backend. Terraform Stacks
    was on this slide and came off 2026-08-28: it is GA but needs HCP Terraform or Terraform
    Enterprise 2.0 on a resource-under-management plan, so it is unavailable to anyone
    running Terraform CLI and does not belong in a list of techniques the audience can use. The module tree moved
    into the reader-mode popover. Rules are `#s15b .tech-*`) - **Dafydd**
19. `s16b` By the numbers (one hero number, 900 PRs merged, with the supporting figures -
    35-40 contributors, 1,902 commits, 134 HCL files, 19,000+ lines of code - in a quiet
    row below; date range Jan to Sept 2026; option C, accepted 2026-08-28) - **Gordon**
20. `s17` Questions (template "Questions? Your turn!", navy) - **Anyone**
21. `s18` Links - **Anyone**
22. `s-thanks` Thank You (template close, royal blue) - **nobody assigned**

The old `s00b` "Who we are" slide was folded into the title slide when the template's
three-speaker title layout arrived. Former slides folded away in the earlier trim: `s06`
(into s10's intro), `s09` (into s10), `s-refine` (into s12), `s15` (chips moved to s15b; its
500/1,500/5,000 figures remain on s04), `s-today` (removed 2026-08-27 at Joseph's request).

### Settled story facts (do not re-ask, do not contradict)

- **Estate at the start:** Sandbox (no parity), Staging (parity on paper, drifted, no history
  to reconcile), Production. DevTest was added recently (2026) as the first stop on the route
  to live - a single CLI-triggered workspace. Sandbox is now CLI-only, outside the RTL.
  Today's RTL: DevTest -> Staging -> Production.
- **Prod first** because staging's drift meant importing it first would validate the wrong
  thing. The control: the Terraform API client held read-only scopes during import (import
  only reads); write access widened only once imports were stable with no recurring diff.
  Joseph and Gordon held those keys.
- **Singletons (Nov 2025):** settings panes are single-instance - write HCL matching the UI,
  apply, the "create" is a no-op, resource lands in state. All settings resources in ~a day.
  Nothing was imported before November 2025; before that it was all provider development.
- **Sentinel:** LBG Sentinel policy bans `import` blocks org-wide (Terraform runs the bank's
  Azure/GCP; import would let one workspace adopt others' resources). No CLI access to PRD
  workspaces. Fix: time-bound exception per import window, later a standing exception once
  the team showed they were sole actors. Fine to name Sentinel publicly.
- **The loop:** matrix (group-built spreadsheet of resource types and dependencies) picks the
  next resource -> jamfpy script emits a structured map (duplicates and all) -> `for_each`
  with conditionals/dynamic blocks -> apply with zero changes -> refinement passes (dedup,
  raw IDs -> named locals like `local.category_ids["Name"]`, shared locals), zero-diff plan
  gating every pass. Gordon: scripts + verbose imports. Joseph: refinement passes.
- **Write-permission removal goes FIRST, not last.** GUI/UI write access for the in-scope
  resource types is revoked at the *start* of a wave (step 3 of the wave workflow), before the
  import - so nobody can make a change you do not know about, which would surface as a diff you
  then have to chase. The validation slide used to present it as the final gate; that was the
  order things happened to run in on some waves, but it is not the advice, and it contradicted
  the wave-workflow slide. Corrected by Gordon Deacon, Aug 2026. A zero diff is only meaningful
  because write access went first - say that, rather than treating the removal as a finish line.
- **The SDK is written `jamfpy`, lower case**, everywhere it is named: `s11`, its speaker
  notes, `presenter.json` and the `s18` links chip all use it, and Joseph writes it that way
  too. This file's two `JamfPy` spellings were normalised to match on 2026-08-28. The `s11`
  pipeline diagram's top box says "jamfpro Python SDK" (the thing it talks to), which is a
  separate label and was left alone.
- **Bulk imports** Dec 2025 - Jan 2026; refinement through Feb - Mar 2026.
- **Sequencing bands:** 1 singletons (client check-in, inventory collection, activation code);
  2 no dependencies (scripts, categories, departments); 3 dependent (smart groups, advanced
  searches, extension attributes); 4 configuration profiles and policies. Confirmed by Gordon
  Deacon, Aug 2026.
- **Module pivot:** happened *after* the staging rebuild, and was caused by it - the team wanted
  to deploy to staging first without the change mirroring straight to production, and the only
  lever the repo had was an FQDN conditional. One `terraform/jamfpro` dir with FQDN-keyed
  conditionals got out of hand -> shared modules (`iam_main`, `profiles_policies_main`, `root_main`) + thin
  per-instance roots (`prod/lbgstaging`, `prod/lbgbusiness`, each with `iam` /
  `profiles_policies` / `root`). Modules carry payloads (privilege-set JSON, .mobileconfig,
  scripts, icons, descriptions; `profile_staging_only/` for staging-only profiles).
- **Workspaces:** 3 per instance (iam / profiles_policies / root) for staging and prod, for
  blast radius. DevTest: 1 CLI workspace. Sandbox: no workspace at all - local dev only, driven
  from the CLI. Plans run consistently in 4-6 minutes. Confirmed by Gordon Deacon, Aug 2026.
- **Staging migration:** not imported - nuked bar essentials (APNS, cloud IdP), then prod's
  configuration pointed at it and iterated through errors to a clean run. Presented as a
  highlight of the talk. Sequenced *before* the module pivot, which it caused. Kept-items
  confirmed by Gordon Deacon, Aug 2026; the month is still open and drives the timeline bar.
- **Route to live (today):** Sandbox (isolated, CLI and GUI, no restrictions - onboarding and
  leadership hands-on; sits outside the route) -> DevTest (under IdP and device compliance, not
  change controlled) -> Staging (exact replica of prod: IdP, device compliance, directory access
  all mirror; a device enrolled there is indistinguishable bar the MDM certificate) ->
  Production. Confirmed by Gordon Deacon, Aug 2026.
- **CalVer:** started on Release Please; cadence unsustainable, tracking unclear; switched to
  calendar versioning much later, around the time DevTest arrived.
- **Numbers:** Apr 2025 (provider development start) -> May 2026 (v1.0.0 and final handover); 35-40
  contributors; 900 PRs merged; 1,902 commits; 134 HCL files; 19,000+ lines of code. Refreshed by
  Joseph, 2026-08-27 (was 14+ contributors, 526+ PRs, 127 Terraform files); he gave "lines of code"
  rather than "lines of HCL" and that wording is now what `s16b` shows. The commit count is the one
  figure he did not restate, so 1,902 is carried over from the first build and is probably stale -
  worth confirming before the talk. The date-range figure on the slide itself was then changed to
  "Jan 2026 -> Sept 2026" on 2026-08-28 at Joseph's request; this story fact and the speaker notes
  still build to Apr 2025 -> May 2026, so the slide now disagrees with both - flagged for Joseph to
  reconcile, not resolved here.
- **for_each exceptions:** policies only. Dock items were never an exception (corrected by
  Joseph, 2026-08-27). The reason is how diverse policies are: they vary so widely from one
  to the next that a `for_each` map has to carry every field any policy might need, which
  makes it harder to read than plain HCL. Which policy fields vary is not recorded - do not
  invent examples.
- **DRY across instances (slides 17 and 18, confirmed by Dafydd, Aug 2026):** the objective
  was one Terraform codebase applied to every Jamf Pro instance. Jamf Pro does not allow it,
  because the same resource type carries configuration unique to the instance it is deployed
  in - a static computer group holds computer IDs, and the push certificate and Volume
  Purchasing content tokens are issued to one instance. Static groups were the exception the
  team expected and planned for; the point of the pair is that more kept appearing during
  implementation, so techniques were needed to get as close to DRY as the product allows.
  The techniques are a menu with no right answer and the estate uses more than one of them.
  Use vendor names throughout: Jamf's for Jamf objects (Volume Purchasing content token, not
  VPP token; push certificate for the Apple push artefact), HashiCorp's for Terraform (root
  module, child module, input variables, local values, meta-arguments, data sources).
  "Thin root" is not a Terraform term and is not used. Before putting a product on this
  slide, check it is reachable by someone running Terraform CLI: Terraform Stacks was cut
  for failing that test.
- **Rejected up front:** single workspace (blast radius / plan time, 500-1,500-5,000
  figures); per-team modules (internal approval complexity - expansion TODO); managing
  everything (static group membership unmanaged to protect support).

### Outstanding TODO chips in the deck

| Slide | TODO | Owner |
|---|---|---|
| `s-pivot` | The rest of the instance-unique list, beyond static computer group members, the push certificate and Volume Purchasing content tokens | Dafydd |
| `s-staging` | Confirm the month - drives the timeline bar | Gordon Deacon |
| `s18` | URLs, contact, socials (Q12) | Joseph |

One chip still carries a question number from the first build (`TODO Q12`). It resolves in
`spec.md` §4. The old logo/brand-assets chip died when the template
arrived. Three earlier table rows (s02 support-team access model, s04 per-team-modules
approval complexity, s07 more prep points) remain outstanding as content work but carry no
chip in the deck; their context is in `spec.md` and the git history of this file.

## Deck: presentations/training_a_team

**"ClickOps to GitOps - Learning Journey"**, in `index.html`. Renamed from
`clickops-to-gitops.html` when the site moved to path-per-deck: the CloudFront Function
resolves `/training_a_team/` to `index.html`, so any other filename is only reachable by its
full path. **21 slides.** `ClickOps_to_GitOps.key` alongside it is the committed Keynote
download from `tools/build-key.mjs`. No spec, notes file or slot length has been recorded
here yet. Content work is ongoing, slide by slide (Aug 2026).

`docs/timeline-notes.md` is authoritative for slide order, speaker and timeline
correspondence. The slide map and speaker list below are descriptions of the current state -
where either disagrees with the doc, it is corrected to match the doc, not the other way
round.

Slide map (after the template adoption and the merge with Dafydd's Aug 2026 edits): `#1`
title (template three-speaker layout, LBG logo in the template's customer-logo slot, stats
row kept), `#2` "Where we are today" (the old half-speakers slide kept its real content -
the estate statecards, centred and enlarged - when the speakers moved to `#1`), `#3` goals,
`#4` execution, `#5` what didn't work, `#6` what worked, `#7` conditions, `#8` learning
priorities by role, `#9` the learning pathway (four phases - **merges the old `#9` matrix and
`#10` timeline**, Aug 2026: both said the same thing twice and neither described what the team
actually did). Titled "the pathway we **followed**", not "that worked": phase 1 front-loaded
all the theory and the team only found out afterwards that it did not land, so that card
carries a "we'd change this" flag and agrees with `#5` rather than contradicting it. Phase 3
teaches Git *after* two phases of Terraform, deliberately - nobody had anything to put in Git
yet; the thing that needs versioning has to exist before you can version it. Both confirmed by
Gordon Deacon, Aug 2026. The four phases are his: 1 front-load the theory (flagged), 2 ground
the concepts, 3 Git/GitHub/GitOps, 4 advanced - aimed at the seniors who would own the repo
after handover, and closing on PR review, which is condition 07 from `#7` arriving again.

`#9` deliberately does **not** use the bordered-card grid the rest of the deck runs on (`#7`,
`#8`, `#11`, `#14` all do). It is drawn as a **route**: one rising SVG track with four stop
dots, and the text for each phase hanging beneath its own stop. **The track and the dots share
one coordinate space** - an earlier attempt put the line in an SVG and the dots in CSS and they
never met. The viewBox is `0 0 1676 376`, where **1676 is the real content box**: the deck is
1920x1080 and `.slide` padding is `88px 122px 72px`, so 1920 - 2x122 = 1676. Get that number
wrong and `preserveAspectRatio="none"` stretches the whole SVG - the track overshoots the last
stop and the dots render as ovals. Columns are (1676 - 3x40 gap) / 4 = 389 wide, left edges at
0/429/858/1287, each dot one radius (9px) in: cx 9/438/867/1296, cy 83/62/41/20. The track runs
`M9 83 L1296 20` - it starts on stop 1 and ends on stop 4. The `.route-stops` grid is stepped
by the same 21px the dots rise (`margin-top` 83/62/41/20), so moving a dot means moving its
text block by the same amount. Phase 1's dot is a hollow `--warn` ring and its
number and warning line are `--warn`; the rest are `--accent`. Keep the Jamf palette tokens -
the difference from the other slides is layout only.

A dashed `--alt-light` **gate** sits in the column gap after stop 3 (75.7%): an engineer was
competent to change a live production instance from the end of phase 3, once Git and the GitOps
flow were in. Everything left of the gate is the whole team; phase 4 is the maintainers only.
Confirmed by Gordon Deacon, Aug 2026. Move the gate and you must move the `.gate-label` width
with it - the label is right-aligned inside a box the same width as the gate offset. Then `#10` delivery, `#11` content types, `#12` case study, `#13` scope, `#14`
onboarding, `#15` hiring, `#16` resources (with the QR rail - see below), `#17` Questions
("Questions? Your turn!", navy), `#18` Thank You, `#19` the skills map (moved to post-matter by
Dafydd, kept there), `#20` and `#21` the two slides the merge replaced - the old pathway matrix
and the old week-by-week timeline, kept as appendix reference at Gordon's request (Aug 2026),
with `data-speaker` stripped so they stay out of the speaking rotation - and `#22` the colour
appendix. The deck is **22 slides**; eyebrow numbers and section banners were renumbered to
match. `#17`-`#22` are post-matter: Thank You closes the talk.
Thank You closes the talk; `#20`-`#21` are reference material for readers. Eyebrow numbers
match slide numbers (Dafydd's convention) - renumber them when slides move.

Merged in from Dafydd's edits, on top of the restyle:

- **QR rail on `#17`**: a third grid column (`.res3`, `.qr-rail`, `.qr-tile`) holding
  `../_shared/qr-code.png` with a "take it with you" caption; the delivery note says to
  leave it up while taking questions. The tile's white background is a deliberate literal -
  a QR code stays black-on-white under every theme - with a `var(--border)` hairline so it
  doesn't dissolve on the light themes.
- **Speaker overlay (press `S`)**: a fixed top-left pill showing who has the room, read off
  each section's `data-speaker` / `data-speaker-note` attributes (16 slides carry them;
  unassigned slides say "No speaker assigned" rather than inheriting). It is a rehearsal
  aid, off by default so it never lands in the Keynote capture, and hidden in print. Person
  colours: Dafydd `--green-bright`, Joseph `--blue-light`, Gordon `--amber`.

Notable content slides:

- **Goals** (`#3`): learning-outcome cards, a "what success looked like" behaviours block,
  a non-goals strip and a trained-bar definition.
- **Execution** (`#4`): a fan-out - a hub panel (one engineer seconded into the DevOps CoE,
  3 months, train-the-trainer) bracketed by an SVG to five outcome cards (materials, session
  design, hackathons and homework, migration waves, handover), with two full-width arrows
  underneath showing the two-way trade: domain context in, GitOps practice back. Classes
  `.fanout`, `.hub`, `.brace`, `.spokes`/`.spoke`, `.flow`/`.flowrow`.
- **What didn't work** (`#5`): a hero SVG chart across the top - bands mark teaching
  sessions, a gradient line rises through each then decays through the gap that follows,
  trending down over six months. **That curve is illustrative, not measured**, and the slide
  says so in a `SHAPE IS ILLUSTRATIVE` label - keep that label if the chart is edited. Below
  it, eight chips: seven failures plus one accent chip for what replaced the programme, then
  a quote strip. Classes `.chartwrap`/`.chd`, `.fchips`/`.fchip` (`.won` for the accent one)
  and `.qstrip`.
- **Conditions** (`#7`): a hero layout - a large left panel gives psychological safety the
  weight the copy claims for it ("the most evidenced condition of all") with three practical
  points under it; the other six conditions, including "Expect the dip", sit right as
  compact numbered cards. Classes `.herowrap`, `.heropanel`, `.supp`/`.suppcard` (`.dip`).
- **Learning priorities by role** (`#8`): three role cards across the top; below them two
  radar webs (grid rings plus spokes, thin outlines, translucent fills), each carrying all
  three roles. Left is a small org with no DevOps function, where every shape is broad;
  right is a large org like LBG, where the shapes narrow but spike on Jamf APIs and
  Mentoring while Environment and GitOps pull back to the platform team. Classes `.roles3`,
  `.scen2`. The colour chip in each role-card header is the chart key, so **chip and polygon
  colours must stay in step**: junior `--accent` (lime), engineer `--alt-light`
  (cornflower), senior `--text-2` (off-white). The mapping is documented in the `.roles3`
  CSS comment.

Unconfirmed facts carry amber TODO chips - the deck has a `.todo` chip class and an amber
token for exactly that. Current chips (3): photos for Joseph and Gordon (`#1`); how long the
dip lasts (`#7`); the 3-4 minute interview with Louise. The `#5` engineer quote was confirmed
by Gordon Deacon, Aug 2026, and its chip is gone. The `#3` "what success looked like" behaviours
(the team became self-sufficient committing and reviewing PRs without assistance, was making
architectural decisions and was managing resources in code exclusively), the trained bar and the
non-goals were confirmed by the user, Aug 2026, and all three `#3` chips are gone.

Speakers (`data-speaker`), after the `#9`/`#10` merge - `docs/timeline-notes.md` is
authoritative here too; this list is corrected to match it when they disagree: `#5`, `#7`,
`#9` and `#14` are Gordon; `#4`, `#6`, `#10`, `#11` and `#13` are Joseph; `#3`, `#8`, `#12`,
`#15` and `#16` are Dafydd. Scope moved from Dafydd to Joseph and onboarding from Dafydd to
Gordon, Aug 2026. `#2` is still marked **All** but Gordon's notes assign it to Dafydd -
unresolved.

`#7` carries a seventh condition, "Decide who approves the pull requests" (`.suppcard.wide`,
full-width across the 2-column grid), and its hero panel is now **Two kinds of safety** -
operational (leadership) and psychological (engineers) - rather than psychological alone.
Both from Gordon, Aug 2026. The dip lasted 2-3 months.

**The four disciplines are a shared vocabulary.** `#19` (skills map) is built on
**Environment, Git, Terraform, GitOps**. The merged `#9` deliberately drops the discipline
tagging to stay readable from the back of the room; `#19` still calls
them "the four core disciplines" in its subtitle. `#8`'s radar uses those same four plus
Jamf APIs and Mentoring, the two that only start to matter as people move up. If you rename
or re-cut a discipline on any of those four slides, change all four.

Two deliberate decisions on `#8` worth not undoing:

- **Provider architecture and SDK design were removed.** Building the Terraform provider is a
  different job from using it, and no Mac team needs a Go developer to adopt this. It was
  replaced with Jamf Pro API knowledge. The senior row owns the "resource isn't supported
  yet" triage: does the API support it, is it a provider gap, is it worth raising.
- **The senior label is "The escalation point", not "End-to-end mastery"**, because seniors
  are defined here by responsibility rather than by a completed body of knowledge.

Known tension, left as-is on purpose: `#8` organises the curriculum by job grade, while `#9`
organises it by stage of learning (Oriented, Safe Contributor, and so on) and `#5` reports
that prior coding experience predicted success rather than seniority. The speaker owns that
framing and chose to keep grades, since that is how the audience's own org charts read.

**How `#8`'s two charts are scored** - this came from the speaker directly, so do not
"correct" it back:

- **Jamf APIs score identically in both charts.** No external team is ever going to know your
  own service's APIs better than the team that owns the service, so org size makes no
  difference to it. If you find yourself lowering one of them, you have misunderstood.
- **Environment is the real differentiator.** Small org: you design it, build it and maintain
  it, because nobody provisions a repo for you. Large org: repos and toolchain arrive from
  the internal developer platform as templates, so the burden genuinely lifts.
- **Git and GitOps barely move between the two, and must not be scored sharply lower in the
  large org.** In a large org the Mac team still owns its branching strategy, still wires the
  Git event triggers into its own environments, and still handles merges to main and
  releases. What it loses is authority, not knowledge: every PR needs a second approver,
  GitHub access stops at the edges of what the team owns, and it cannot disable Checkov or
  the linters. An earlier draft scored these down to 0.60 and that was wrong.
- **The governing principle**, and the speaker's own wording, which the panel straplines now
  carry verbatim: small org is "Design, build and maintain the platform and manage the Jamf
  Terraform workflows"; large org is "Consume the platform, inside its guardrails and manage
  the Jamf Terraform workflows". The closing line is "You still need to know how the platform
  is designed. But your workflow will have to conform with wider company standards." Note
  that managing the Jamf Terraform workflows is constant across both; only the platform
  underneath changes hands.
- **Say "the platform", not "it".** An earlier draft leaned on an unanchored pronoun whose
  referent drifted between the tooling, the delivery machinery and the whole body of
  knowledge, within a single panel. On a slide read at distance there is no time to resolve
  an antecedent, so name the thing.
- Mentoring is low in the small org (fewer people, one person often spans all three roles)
  and high in the large one (bigger team, plus the packaging and endpoint security teams).

The figures on `#5` are measured, not estimated. They come from
`github.com/deploymenttheory/terraform-training-jamfpro` at the time of writing: 214,645
words across 51 markdown files in `training_materials/` (of which 20 Terraform modules sit in
a `WIP/` folder) against 3,778 words across 6 files in `training_essentials/`, a ratio of
roughly 57 to 1. The 144 prescribed hours are the TOTAL row of the module table in
`training_materials/0.0.0_module_overview.md` (85.5 instructor-led plus 58.5 student-led).
Re-measure with `wc -w` before quoting them again, since the repo is still being worked on.

The reading of those 144 hours matters and is the speaker's, not a derived one: it is about
four weeks of learning, which is roughly right for the number of topics. The failure was the
calendar, not the volume - four weeks of content delivered across six months, with interest
wandering off in the gaps. Don't recast it as "too much content".

Everything about it is its own: its own token names, its own slide machinery. Nothing is
borrowed from the other deck and nothing should be.

### Colour knobs and themes

Every colour in this deck resolves to a semantic token in `:root`. **Never hardcode a hex in
slide CSS or markup** - reuse a knob or add one, or the themes will not reach it. The old
colour-named tokens (`--green`, `--blue-light`, `--red`) survive as aliases of the semantic
ones, so existing rules keep working, but new work should use `--accent`, `--alt`, `--warn`,
`--surface`, `--text-dim` and friends.

- **The unthemed default is the JNUC 2026 template look** (royal blue canvas, navy surfaces,
  lime accent, off-white text, cornflower secondary) - the bare `:root`, no `[data-theme]`
  block. **Seven presets** in `THEMES`: `default`, `midnight` (the deck's original near-black
  look, preserved verbatim when the JNUC default landed), `light-paper`, `light-slate`,
  `jamf` (modelled on the Jamf Pro admin console), `deep-green`, `contrast`. Add a preset by
  copying a block and adding its name to `THEMES` in the theme script.
- **Controls**: `T` cycles, `Shift+T` cycles back, `K` opens the knobs panel. `?theme=<name>`
  wins on load; `?knobs=1` opens the panel. The choice persists in `localStorage`, wrapped in
  try/catch because `file://` can have an opaque origin - losing persistence is fine, throwing
  is not.
- **The knobs panel** lists the primary knobs, hides the fine tints behind a toggle, and
  "Copy CSS" emits a paste-ready `[data-theme="my-theme"]{…}` block.
- **Values marked DERIVED** in the token block are not from the brand colour system; they
  are tints worked out from a documented colour (template or brand), and each says which.
  Brand colours (Mountain Meadow, Tropical Rain Forest, Jamf Blue, Alert Red) and the
  template palette values are always used exactly.
- **The colour appendix (`#21`) stays canonical.** Its chips keep literal hexes under every
  theme, because it documents the brand palette rather than the active UI. Do not tokenise
  them.
- **Embedded artwork**: several logos are white-on-transparent PNGs/SVGs drawn for a dark
  stage (Octocat, cursor, the white jamf and JNUC logos). `--art-mono-filter` inverts the
  monochrome marks and `--art-plate` sits the white/multicolour ones on a plate where a
  light theme needs it. These rules are scoped per-theme; the royal-blue default carries the
  white artwork unfiltered.
- **Slide copy must stay theme-neutral.** Do not write "the green bands" or "the lime chip"
  when a theme can turn them another colour.

When changing anything colour-related, screenshot all 21 slides on `default` before and after
and `cmp` them. A pure tokenising change must not alter the rendering of any theme you did
not intend to change; that check is what catches a wrong substitution.

- Slides are `<section class="slide">` with no ids except `#s1`. Navigation is by index -
  the URL hash is `#1`..`#21`, not a slide name. Removing or adding a slide renumbers
  everything after it - update this file's slide references when that happens.
- Notes live in a `data-notes` attribute on each section, shown in an overlay toggled with
  `n`. There is no second-window presenter view and no `presenter.json`.
- Keys: arrows / PageUp / PageDown / space / Home / End to move, `n` notes, `s` speaker
  overlay, `f` fullscreen, `T`/`Shift+T` themes, `K` knobs. Click-to-advance lives in an
  inch-wide gutter down each screen edge.
- The footer hairline and JNUC logo sit slightly lower than the template's geometry so dense
  slides can never collide with them; the slide counter sits bottom-left above the help
  strip.

Known gaps, none of them addressed:

- No spec or provenance file, so the facts on its slides have no recorded source.
- Slot length and which of the three speakers present it are unrecorded.

(The deck's em-dashes were all removed when the template restyle touched every slide, so
that former gap is closed.)

## Building the downloads

Each deck's `.key` is generated from the deck's own HTML by `tools/build-key.mjs`. GitHub's
runners do not ship Keynote, so **the build runs on a Mac by hand and the `.key` files are
committed** - the deploy only syncs them. Run `npm run build:key` (needs `npm ci` and
`npx playwright install chromium` once, plus Keynote installed). **Rebuild and commit the
`.key` files in the same change as any deck edit**, or the download on the landing page goes
stale - nothing in CI checks this.

Playwright opens each deck over `file://`, presses ArrowRight through it and screenshots the
viewport at 1920x1080; AppleScript then drives Keynote to assemble the PNGs into a
1920x1080 deck and save it. Both decks share the interface the script relies on -
`section.slide` elements, an `.active` class on the current one, and ArrowRight advancing
exactly one slide with no intra-slide fragments. A deck that breaks any of those needs the
script updating, and the script fails loudly rather than silently emitting duplicate slides:
after each keypress it asserts the deck actually moved.

- **Every slide is a full-bleed image.** These decks are hand-built HTML with SVG, gradients
  and absolute positioning; none of that survives translation into Keynote shapes. The
  download is for handing out, not for editing.
- **Speaker notes are real text**, read from `<aside class="notes">` (`migrating_an_instance`)
  or `data-notes` (`training_a_team`) and written into the presenter notes. That one
  expression covers both decks, so neither needs per-deck config.
- **`#help` is hidden during capture** - a keyboard hint means nothing in a downloaded file.
  The slide counters and the timeline strip are deliberately kept: the counter is useful on
  paper and the timeline is deck content.
- **Keynote quirks the script already handles**: Keynote must be started via
  `open -ga Keynote` and polled until scriptable (an AppleScript `launch` inside the tell
  block errors with -600 when it is not already running); the whole build runs inside
  `with timeout of 900 seconds` because saving a 20-odd-slide document outlasts the default
  AppleEvent reply timeout; and a failed osascript gets one clean Keynote relaunch and retry
  (the connection can drop with -609 under a long scripted build).
- **Output filenames are fixed in the script** because `presentations/index.html` hardcodes
  them. Changing one means changing both.
- The `.key` files ARE committed (unlike the old CI-built `.pptx` downloads, which were
  gitignored). Fonts and rendering therefore match the Mac that ran the build.

## Sandbox (feedback review pages)

Feedback on a deck arrives in chat. The loop that turns it into deployed changes - an
orchestrator session dispatching one Sonnet agent per slide, each delivering a single PR
that carries the slide edit, the sandbox page, the index entry below and any `AGENTS.md`
updates the change needs, with the orchestrator only merging and deploying - is written
down in `feedback-workflow.md` at the repo root (committed; read it first).

`presentations/sandbox/` holds one sandbox per deck. `sandbox.css` (landing-page look, not
the JNUC template - this is tooling, not a deck) is shared by all of them.
`presentations/sandbox/index.html` is a minimal chooser: a two-item list linking to each
deck's own sandbox, `presentations/sandbox/migrating_an_instance/` and
`presentations/sandbox/training_a_team/`. Each of those subdirectories has its own
hand-maintained `index.html` listing that deck's pages by hand, and holds that deck's
review pages alongside it. Each change gets a review page under
`presentations/sandbox/<deck>/`, created from `tools/sandbox-template.html`, showing three
implementation options; Joseph picks one in chat or asks for another set, and the winner
goes into the deck. Every page carries `<meta name="robots" content="noindex">`. The
landing page carries a "Sandbox" button on each deck card, linking to that deck's sandbox
(added 2026-08-27 at Joseph's request; moved from one global button to one per deck card
the same day, when the sandbox itself split one-per-deck).

How a review page works: it embeds the real slide three times in iframes
(`../../<deck>/index.html#<slide-id>` - two levels up from `presentations/sandbox/<deck>/`
to `presentations/`, then into the deck) and, on each iframe's `load`, appends a `<style>`
with that option's CSS to the iframe document. The options are therefore always the
deployed deck plus a few rules, never a copy of the deck, and they track deck edits
automatically.

- Option A is by convention whatever the deck currently ships and injects nothing.
- Variant CSS only touches the slide's `#id` and only uses the deck's own tokens, so an
  accepted option pastes into the deck unchanged.
- Injection needs same-origin access, so it only works over HTTP. Opened from `file://` the
  iframes load but every option renders as the plain deck. Verify with a local server (see
  Verifying) and a tall headless window, e.g. `--window-size=1400,3000`.
- Check each option for overflow into the timeline strip, and for rules leaking onto other
  elements that share a class - on `s01` the top caption shares `.pipeline-label` with the
  band label, so band rules must be scoped to `#s01 .pipeline-band .pipeline-label`.
- Page names: `presentations/sandbox/<deck>/<slide-id>-<what>.html`. The deck's own index
  entry records date, deck, slide, speaker and decision state. Once an option is accepted,
  apply it to the deck and mark the entry decided (or delete the page and its entry).

Current pages (all under `presentations/sandbox/migrating_an_instance/`):
`s-sentinel-round2` (2026-08-28, slide 9 - three fresh treatments after round one was
rejected, all leaning simpler and all pure CSS on the existing `.lead` / `ol.gates` /
`li.card.gate` markup scoped to `#s-sentinel`, so nothing new ships in the deck: A the live
slide, B the cards as three tall columns ruled top and bottom with the number large in mono
and the only colour on the slide, C the three states as one run of plain blocks joined by
two arrows in the diagram line colour, D a two-column split with the lead holding the left
half and the gates stacked down the right as a numbered list with hairlines between).
Decided (all under `presentations/sandbox/migrating_an_instance/`):
`s11-bullets-round2` (2026-08-28, slide 12 - four plain treatments of the right-hand
points, wording unchanged, all four pure CSS on the same list: A the dashed list the deck
now ships, B the points separated by a hairline rule at full column width, C each point on
the navy card surface with the name in a fixed-width left column so the four lines align,
D the points numbered 1 to 4 in mono in a gutter with the name in the display face. The
rejected flag keeps the danger colour on its name in all four, never a strike-through, and
the left-hand pipeline SVG is untouched. Decided 2026-08-28: option D, applied to the
deck's `#s11` rules; the page is deleted, the index keeps the record as a non-linked
`.done` entry);
`s11-right-hand-points` (2026-08-28, slide 12 - four visual treatments of the right-hand
column, which that PR cut from seven bullets to four points, shipped as the markup wrappers
`.s11-opt-a` to `.s11-opt-d` inside `#s11`. Superseded 2026-08-28 with no option chosen:
Joseph rejected all four and asked for plain, easily separated bullet points, so the
wrappers, their markup including the inline-SVG glyphs, and their CSS came out of the deck
and `s11-bullets-round2` above replaced the page. The page is deleted, the index keeps the
record as a non-linked `.done` entry);
`s-sentinel-visual` (2026-08-28, slide 9 - four visual treatments, no wording or fact
changes anywhere: A the live lead-plus-gate-cards slide, B a hatched Sentinel wall crossed
three times, C a staircase of three panels growing taller left to right, D the three states
on a Nov 2025 to Jan 2026 axis with the exception windows as a repeating tick band; B, C
and D shipped as hidden wrappers in `#s-sentinel`. Superseded 2026-08-28: all three
rejected, no option chosen, the wrappers and the whole S-SENTINEL CSS block removed from
the deck and the round two page opened in its place. Page deleted, the index keeps the
record as a non-linked `.done` entry);
`s-staging-steps-first` (2026-08-27, slide 16 - four ways to put the three rebuild steps
first, all four pure CSS on the same markup: A three full-height panels, B a numbered run
down the left with a quiet right-hand column, C one flow strip in the deck's diagram style,
D the wipe as a hero panel; the rewritten wording ships in all four. Amended 2026-08-28 when
the three pixel-art step icons landed: the icons are in all four renders and each option's
CSS now sizes and places `.s-staging-art` for its own layout - 192px in the card middle in
A, 96px beside the ring in B, 144px above each node in C, and 120px in D's hero panel only,
because D's half-height cards have no room for one. Decided 2026-08-28: option B, applied
to the deck's `#s-staging` rules; the icons were grown from B's 96px to 168px, the largest
width a rail row allows before the third row's icon meets the timeline strip. Page retired);
`s16b-numbers` (2026-08-27, slide 19 - the refreshed figures shipped in all four
renders; A the six stat tiles the deck already had, B five gauge bars each measured against
its own next round number with the ranges drawn as open ends, C one hero number - 900 PRs
merged - with the other four as a quiet supporting row, D unit grids of one mark per
contributor and one mark per HCL file with the three uncountable totals stated below.
Decided 2026-08-28: option C, applied to the deck's `#s16b` rules as its plain markup; the
slide's date-range figure also changed to Jan 2026 - Sept 2026 at Joseph's request, now at
odds with the speaker notes and the settled Numbers fact above - flagged, not reconciled.
Page retired);
`s14-terminal-excerpt` (2026-08-27, option B - the `terraform plan` block as a real window:
a light chrome bar, red/amber/lime traffic-light dots, a centred `joseph@jnuc - zsh` title,
white bold command text against the lime result, and a blinking cursor on a fresh prompt
line below it - applied to the deck's `#s14` rules; the page is deleted, the index keeps
the record as a non-linked `.done` entry); `s13-policies-only` (2026-08-27, option D - the
exception and its reason in large type,
nothing else, wording made more human - applied to the deck's `#s13` rules; the page is
deleted, the index keeps the record as a non-linked `.done` entry);
`s01-environment-band` (2026-08-27, option B - the Sandbox / Staging / Production row as
one three-segment chevron arrow - applied to the deck's `#s01` rules; the page is deleted,
the index keeps the record as a non-linked `.done` entry); `s01-column-titles`
(2026-08-27, option C - bordered column panels with aligned dividers - applied to the
deck's `#s01` rules; the page is deleted, the index keeps the record as a non-linked
`.done` entry); `s07-checklist` (2026-08-27, option D - two portions - applied to the
deck's `#s07` rules; the page is deleted, the index keeps the record as a non-linked
`.done` entry); `s08-use-of-space` (2026-08-27, option C - seven full-width bands
stepping down the slide, each starting a notch further in than the one above - applied to
the deck's `#s08` rules; the page is deleted, the index keeps the record as a non-linked
`.done` entry); `s05-fill-the-space` (2026-08-27, option D - each path as its own bordered
panel with the diagram centred inside - applied to the deck's `#s05` rules; the page is
deleted, the index keeps the record as a non-linked `.done` entry); `s-workspace-round3`
(2026-08-27, live slide kept, B to D rejected - none
of the three redesigned alternatives captured the point; the page is deleted, the index
keeps the record as a non-linked `.done` entry); `s10-diagram-text` (2026-08-27, option C -
tier labels and examples pushed further up the font scale and the four bands grown to
match - applied to the deck's `#s10` rules and SVG; the page is deleted, the index keeps
the record as a non-linked `.done` entry); `s-pivot-display` (2026-08-27, closed without a
decision - live slide (option A) kept, B to D not chosen; the page is deleted, the index
keeps the record as a non-linked `.done` entry). `presentations/sandbox/training_a_team/`
has no pages yet.

## Deployment

`.github/workflows/deploy.yml` deploys this repo on merge to `main` (only when
`presentations/**` or the workflow itself changes) and on manual dispatch. It syncs
`presentations/` to S3 with `--delete` (the committed `.key` downloads ride along like any
other file), then creates a CloudFront invalidation and waits for it. A sync alone is not
enough, because the distribution uses CachingOptimized and holds objects at the edge for a
day. Last, it rewrites the CloudFront link in `README.md` to whatever the distribution
actually reports and pushes that back to `main`. There is no build step in CI any more -
`tools/**` and `package*.json` changes do not trigger a deploy.

The bucket mirrors `presentations/` exactly, so the URL layout is the repo layout:

| Path | Serves |
| --- | --- |
| `/` | `presentations/index.html` (the landing page) |
| `/migrating_an_instance/` | `presentations/migrating_an_instance/index.html` |
| `/training_a_team/` | `presentations/training_a_team/index.html` |
| `/_shared/speakers.js` | `presentations/_shared/speakers.js` |
| `/sandbox/` | `presentations/sandbox/index.html`, a chooser linking to `/sandbox/migrating_an_instance/` and `/sandbox/training_a_team/` (feedback review pages, one sandbox per deck, linked from each deck card's Sandbox button) |

Live at https://d3ga0oyittaf77.cloudfront.net - CloudFront in front of a private S3 bucket
(`jl-html-presentation-2026`, OAC access). Infra is `~/Github/terraform/presentation.tf`, an
S3-backend workspace driven from the local CLI. That repo owns the bucket, the distribution
and the `jnuc-2026-deploy` IAM user; the bucket name and distribution ID are duplicated in
this workflow's `env:` block, so a change on either side needs the other updated.

The domain is not duplicated anywhere. The workflow reads it from
`cloudfront get-distribution` at deploy time and uses it for both the run summary and the
README rewrite, so replacing the distribution only means updating `DISTRIBUTION_ID`. That
needs `cloudfront:GetDistribution` on the deploy user (granted in the same `InvalidateDistribution`
statement as the invalidation permissions) and `contents: write` on the workflow, which is
what lets it push the README commit as `github-actions[bot]`. The URL above is the one place
still maintained by hand - the rewrite only touches `README.md`.

Things that will bite you:

- **Every deck directory needs an `index.html`.** A CloudFront Function resolves `/<deck>/`
  to `/<deck>/index.html` and 301s a bare `/<deck>` to `/<deck>/`. Any other filename is
  only reachable by its full path.
- **Keep shared assets relative and one level up.** Both decks load
  `../_shared/speakers.js` (and the training deck `../_shared/qr-code.png`), which resolve
  under `/_shared/` only because every deck sits one level down in a single bucket. A deck
  nested deeper, or moved to its own bucket, loses its speakers.
- **Adding a deck is two edits plus a build.** The directory gives you the URL, but it will
  not be reachable from anywhere until you add a card to `presentations/index.html`. That
  list is hand-maintained on purpose: generating it would mean client-side JS or a build
  step, and this site has neither. A deck wanting a Keynote download needs the card, an
  entry in `DECKS` in `tools/build-key.mjs`, and a local `npm run build:key` with the
  result committed.
- **The download can go stale.** CI no longer rebuilds it, so a deck edit shipped without a
  rebuilt `.key` deploys an out-of-date download. The rule is above: rebuild and commit in
  the same change.
- **The README's link is generated.** Any `*.cloudfront.net` URL in `README.md` gets
  overwritten on the next deploy, so edit the distribution, not the file. The rewrite is a
  regex over the whole file - a different CloudFront URL added there would be clobbered too.
- **A miss still returns 403, not 404.** The distribution has no `custom_error_response`, and
  a private S3 origin answers a missing key with 403. Only `/` and the deck paths are
  guaranteed to resolve.
- The `*.md` exclude keeps this file and each deck's `spec.md` off the site, but the decks
  ship with their presenter notes embedded, so keep them public-safe.

The workflow authenticates with an IAM user access key, held as the `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY` repo secrets. The user is scoped to this one bucket and this one
distribution and can do nothing else in the account.

Deck rendering itself survived the move: the stage scales to `visualViewport` (fallback
`innerWidth/innerHeight`) so browsers with dynamic chrome (mobile toolbars) don't hide the
bottom of the deck - the timeline strip sits there. Headless-Chrome caveat when verifying:
old headless enforces a minimum window width of ~500px, so phone-sized `--window-size`
screenshots clip on the right; that is the test tool, not the deck.

## Verifying changes

No build step. Serve from the repo root and address decks by their path. To check slides
render without overflow, screenshot with headless Chrome:

```sh
python3 -m http.server 8741 &   # from the repo root
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DECK="http://localhost:8741/presentations/migrating_an_instance/index.html"
"$CHROME" --headless --disable-gpu --window-size=1920,1080 --hide-scrollbars \
  --virtual-time-budget=3000 --screenshot=/tmp/slide.png "$DECK#s00b"
```

For `training_a_team`, swap in `training_a_team/index.html` and use a numeric hash (`#2`),
not a slide id.

When a change is meant to leave the rendering alone - anything sourced from `_shared/`, for
instance - prove it rather than eyeballing it. Screenshot before, screenshot after, and
`cmp` the PNGs; they should be byte-identical. `git show HEAD:<path> > _orig.html` inside the
deck directory gives a baseline to serve alongside the working copy (delete it afterwards).

Anything touching `_shared/` also needs a `file://` check, since that is where a relative
script src would break - both decks render their title-slide speaker cards from it:

```sh
"$CHROME" --headless --disable-gpu --window-size=1920,1080 --hide-scrollbars \
  --virtual-time-budget=3000 --screenshot=/tmp/file.png \
  "file:///Users/josephlittle/Github/jnuc-2026/presentations/migrating_an_instance/index.html#s00"
```

Also check after any structural change:

- Presenter view: same command with `?presenter=1#<slide-id>` at ~1200x760.
- Reader mode: `?reader=1#<slide-id>` - confirms the "More detail" chip placement.
- Timeline: any slide with low-sitting content - the month labels must not clip at the
  canvas edge and content must not collide with the strip.
- Timeline grey state: `#s08` and `#s11` share a range, so shoot both - `s08` highlights in
  accent, `s11` in the muted static state, with the "Dec 25" label accent in both. `#s00`
  accent, `#s01` grey covers the first-slide case. `#s10` moved to sit directly after `#s07`
  (see Current slide order): it no longer precedes `#s08` so their old accent/grey pairing is
  gone, and `#s10`, `#s-singletons` and `#s-sentinel` each now render accent, since none
  repeats the `data-when` of the slide immediately before it in the new order.
- Both decks: ArrowRight must advance exactly one slide per press end to end (the `.key`
  build depends on it), and a deck edit means `npm run build:key` + committing the fresh
  `.key`.

(Serving over HTTP avoids file:// restrictions and is required for presenter sync; any port
works. The timeline and reader-mode checks are `migrating_an_instance` specifics -
`training_a_team` has neither.)
