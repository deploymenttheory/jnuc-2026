# AGENTS.md

Reference for anyone (human or agent) working on this repo. Keep this file current: update it
in the same change whenever anything here becomes inaccurate or stale.

## What this repo is

Home for all public JNUC 2026 materials. It holds more than one conference talk. Each talk is
a self-contained folder under `presentations/`. One deck is ported in so far; a second is
expected.

| Deck | Status |
|---|---|
| `presentations/migrating_an_instance` | Ported in and being worked on. Full detail below. |
| `presentations/training_a_team` | Deck dropped in, not yet worked on here. Full detail below. |

`presentations/index.html` is the landing page rather than a deck. It serves the site root and
links to each deck by hand, so a new deck needs a card adding to it.

The two decks look nothing like each other - one is a light LBG-green theme, the other is
near-black. That is deliberate. Do not harmonise their styling. The landing page sits apart
from both: near-black, anchored on `#006A4D`, the one green they have in common.

## Layout

| Path | Role |
|---|---|
| `presentations/<slug>/` | One talk. Snake-case slug. Each deck owns its own HTML, tokens and script; decks do not import from each other beyond `_shared/`. |
| `presentations/_shared/` | Data used by more than one deck. Currently `speakers.js` only. Content, not styling - see below. |
| `.github/workflows/` | Empty. There is no CI. |
| `README.md`, `LICENSE` | Repo boilerplate. |

`.github/workflows/` is empty, so git does not track it - it exists on Joseph's machine only
until something is committed inside it.

## Shared speaker data

`presentations/_shared/speakers.js` is the single source of truth for who is speaking. It
sets `window.JNUC_SPEAKERS`, keyed by `dafydd` / `joseph` / `gordon`, each with `name`,
`initials`, `org`, `role`, `bio` and `photo` (a self-contained data URI, or `null`).

- It is loaded with a plain `<script src="../_shared/speakers.js">`, not `fetch`. `fetch` on
  a `file://` page is blocked by CORS; a classic script tag is not, so the decks still work
  opened straight off disk. Verified in headless Chrome over both `file://` and `http://`.
- The fields are a **superset**. Each deck renders only what its own layout uses, in its own
  order, with its own classes, from a small render block just before its main script. Adding
  a field here changes nothing until a deck asks for it.
- Strings are plain text, injected with `textContent`, so write `&` not `&amp;`.
- `migrating_an_instance` uses `name` and `org` only. It deliberately ignores `role` and
  `photo` - that deck still carries a "roles + photos" TODO and its own photo treatment is
  unsettled. The data is there whenever that TODO is picked up.
- `training_a_team` uses `initials`, `name`, `role`, `bio` and `photo`. Only Dafydd has a
  photo; the render skips the `<img>` for anyone whose `photo` is `null`.
- The title-slide credit line in `migrating_an_instance` keeps its hardcoded names as a
  fallback so the opening slide is never blank if `_shared/` goes missing. The shared file
  overwrites it on load and always wins. The speaker cards have no such fallback - three
  duplicated cards were not worth the drift risk.

`_shared/` must ship anywhere a deck ships. A deck copied out on its own loses its speakers.

## House rules for every deck

These apply to any deck in this repo, current or future.

- One HTML file per deck, holding its own CSS, JS and images. Zero requests off the machine:
  no CDNs, webfonts, remote JS or remote images. The only local file a deck may reference is
  `../_shared/speakers.js`. A deck must work opened straight off disk.
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
- Every slide carries speaker notes in a hidden `<aside class="notes">` (last element of the
  section). Notes are delivery cues in full sentences; they ship inside the HTML, so keep
  them safe for public reading or strip them from any copy that gets distributed.
- Nothing in a deck may depend on where it is served from. The presenter window opens off
  `location.pathname`, which is why the move into `presentations/` needed no code change -
  keep it that way.

The presenter view and reader mode below are implemented inside `migrating_an_instance`'s
`index.html`, not in shared code. A second deck wanting them has to copy the pattern across.
If that happens, that is the first real candidate for `_shared/`.

## Deck: presentations/migrating_an_instance

**"From Clicks to Code - Migrating Jamf Pro to Terraform at Lloyds Banking Group"**.
30-minute slot, three speakers: Joseph Little, Gordon Deacon, Dafydd Watkins (all LBG).

### Files

| File | Role |
|---|---|
| `index.html` | The deck. Needs `../_shared/speakers.js` alongside it for the title credit and the S00b cards. |
| `presenter.json` | Per-slide speaker notes and timer lengths plus the 30-minute talk limit. Notes are a copy of the deck's `<aside class="notes">` text - keep both in sync when notes change. Timer allocations are proposed, not rehearsed. Nothing reads this file yet. |
| `spec.md` | Spec and change history: the original build runbook, Joseph's source narrative and full repo tree, all three Q&A rounds answered inline, and a decision index. **Historical** - sections marked SUPERSEDED (deck order, palette values, open-questions index) predate the story restructure. |

`spec.md` is provenance for every fact in the deck. Do not delete it; do not treat its
superseded sections as current. This file wins wherever the two disagree. Note that `spec.md`
predates the move into `presentations/`, so any repo tree or path it quotes is stale.

### Deck-specific authoring rules

- **Dates live on the persistent timeline, not in slide content.** Every `<section>` carries
  `data-when="YYYY-MM"` or `data-when="YYYY-MM:YYYY-MM"` (a month range). A fixed strip at
  the bottom of the stage runs Nov 2025 -> Jul 2026 (present day); the active slide's range
  is highlighted, earlier months tinted. Pre-migration scene-setting slides sit at Nov 2025;
  keep positions monotonically non-decreasing through the deck. Don't add per-slide date
  chips. Elements that sit near a slide's bottom-left must clear the strip - use the
  `--tl-clear` token for their bottom offset.
- **The highlight only goes accent when the story moves.** A slide whose `data-when` range
  repeats the previous slide's renders those cells grey (`--c-tl-static`, applied via
  `#timeline.tl-static`); the month label stays accent either way. Comparison is deck order,
  so a slide's state is fixed regardless of how you navigated to it, and the first slide
  always counts as advancing. Reordering slides or editing a `data-when` therefore changes
  which slides grey out - check the neighbours either side.
- Code blocks are hand-tokenised HCL (`tk-kw`, `tk-str`, `tk-num`, `tk-cm` spans). Diagrams
  are inline SVG using the `dg-*` primitives so they inherit tokens.
- The recurring motif is clicks vs code: UI-chrome fragments in muted text giving way to
  monospace HCL in the accent colour. Title slide and close only - never on every slide.
  Currently carried by the title wording rather than a drawn device.
- Palette is a light LBG-green theme; fonts prefer GT Ultra with system fallbacks. Both are
  placeholders until logo/brand assets arrive (Q1).

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
- **Reader mode**: press `d` or open with `?reader=1`. Reveals "More detail"
  `<details class="reader-extra">` popovers on selected slides (currently s01, s05,
  s-singletons, s-sentinel, s12, s15b, s-staging, s-today) for post-presentation viewers.
  The counter shows a "reader" tag while active. Popover content follows the same
  no-invented-facts rule.

### Current slide order (story arc)

Context -> decisions -> first wins -> the wall -> the loop -> growing pains -> payoff.
23 slides, trimmed from 27 to fit the 30-minute slot. Legacy section ids kept stable across
reorders (so `s10` no longer sits at position 10); new story slides use semantic ids.

1. `s00` Title
2. `s00b` Who we are
3. `s01` Context, requirements, constraints (estate at the start: Sandbox / Staging / Production, parity notes)
4. `s02` Who touches Jamf Pro
5. `s03` Migration objectives and design decisions
6. `s04` Ideas rejected, and why (3 architectural rejects; the other 2 moved into the story)
7. `s05` Instance migration order (prod first + read-only API client control)
8. `s07` Instance prep
9. `s-singletons` Singletons first (Nov 2025, no-import trick)
10. `s-sentinel` Getting past Sentinel (blocked -> per-window exceptions -> standing exception)
11. `s10` Resource sequencing (per-resource-type choice + matrix intro + 5-tier diagram)
12. `s08` Migration wave workflow (Dec 2025 - Jan 2026 bulk)
13. `s11` Tools and helpers (JamfPy -> script -> map -> for_each)
14. `s12` Dynamic creation with for_each (comparison + the refinement passes, Gordon/Joseph split)
15. `s13` for_each exceptions (policies, dock items)
16. `s14` Validating a migration
17. `s-pivot` Growing pains (FQDN conditionals -> Mar 2026 module pivot)
18. `s15b` The module structure (module tree -> workspaces + workspace TODO chips)
19. `s-staging` Rebuilding staging (the highlight)
20. `s-today` Refinements along the way (DevTest in, Sandbox out, Release Please -> CalVer)
21. `s16b` By the numbers
22. `s17` Questions
23. `s18` Links

Former slides folded away in the trim: `s06` (into s10's intro), `s09` (into s10),
`s-refine` (into s12), `s15` (chips moved to s15b; its 500/1,500/5,000 figures remain on s04).

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
  next resource -> JamfPy script emits a structured map (duplicates and all) -> `for_each`
  with conditionals/dynamic blocks -> apply with zero changes -> refinement passes (dedup,
  raw IDs -> named locals like `local.category_ids["Name"]`, shared locals), zero-diff plan
  gating every pass. Gordon: scripts + verbose imports. Joseph: refinement passes.
- **Bulk imports** Dec 2025 - Jan 2026; refinement through Feb - Mar 2026.
- **Module pivot (Mar 2026):** one `terraform/jamfpro` dir with FQDN-keyed conditionals got
  out of hand -> shared modules (`iam_main`, `profiles_policies_main`, `root_main`) + thin
  per-instance roots (`prod/lbgstaging`, `prod/lbgbusiness`, each with `iam` /
  `profiles_policies` / `root`). Modules carry payloads (privilege-set JSON, .mobileconfig,
  scripts, icons, descriptions; `profile_staging_only/` for staging-only profiles).
- **Workspaces:** 3 per instance (iam / profiles_policies / root) for staging and prod, for
  blast radius. DevTest: 1 CLI workspace. Sandbox layout: TODO.
- **Staging migration:** not imported - nuked bar essentials (APNS, cloud IdP), then prod's
  configuration pointed at it and iterated through errors to a clean run. Presented as a
  highlight of the talk.
- **CalVer:** started on Release Please; cadence unsustainable, tracking unclear; switched to
  calendar versioning much later, around the time DevTest arrived.
- **Numbers:** Apr 2025 (provider development start) -> May 2026 (v1.0.0); 14+ contributors;
  526+ PRs; 1,902 commits; 127 Terraform files; 19,000+ lines of HCL.
- **for_each exceptions:** policies and dock items (payload complexity, readability).
- **Rejected up front:** single workspace (blast radius / plan time, 500-1,500-5,000
  figures); per-team modules (internal approval complexity - expansion TODO); managing
  everything (static group membership unmanaged to protect support).

### Outstanding TODO chips in the deck

| Slide | TODO | Owner |
|---|---|---|
| `s00` | Logo/brand assets (Q1) | Joseph |
| `s00b` | Speaker roles + photos. Real roles and Dafydd's photo now exist in `_shared/speakers.js`; this deck ignores them on purpose until the treatment is decided | Joseph |
| `s02` | Support team access model (unconfirmed prior reading in `spec.md` §2.4 S02: 1st/2nd line actions only, 3rd line resource management) | Joseph |
| `s04` | Expand per-team-modules approval complexity | Joseph |
| `s07` | More prep points (Joseph wants to explain why) | Joseph |
| `s-singletons` | Real singleton HCL example (placeholder: `jamfpro_client_checkin`) | Joseph/Gordon |
| `s10` | Real resource-type names per band | Gordon Deacon |
| `s11` | Confirm generate-config-out rationale wording (old Q9) | Joseph |
| `s12` | Sanitised real HCL | Joseph/Gordon |
| `s-pivot` | Real FQDN-conditional example | Joseph/Gordon |
| `s15b` | Sandbox workspace layout; plan-time figures | Joseph |
| `s-staging` | Confirm kept-items and timing | Mac engineer |
| `s-today` | Clarify instance roles (DevTest vs Sandbox) | Mac engineer |
| `s16b` | Pre-Nov 2025 provider-development timeline (optional slide) | Joseph |
| `s18` | URLs, contact, socials (Q12) | Joseph |

Three chips still carry question numbers from the first build (`TODO Q1`, `TODO Q9`,
`TODO Q12`). Those resolve in `spec.md` §2.5 and §4.

## Deck: presentations/training_a_team

**"ClickOps to GitOps - Learning Journey"**, in `index.html`. Renamed from
`clickops-to-gitops.html` when the site moved to path-per-deck: the CloudFront Function
resolves `/training_a_team/` to `index.html`, so any other filename is only reachable by its
full path. 20 slides. Dropped in as a finished-looking deck; no spec, notes file or slot
length has been recorded here yet. Content work has now begun, slide by slide (Aug 2026):

- **Goals** (`#3`): new learning-outcome cards, a "what success looked like" behaviours block,
  a non-goals strip and a trained-bar definition.
- **Execution** (`#4`): rebuilt from scratch. The old six-box left-to-right pathway is gone,
  replaced by a fan-out - a hub panel (one engineer seconded into the DevOps CoE, 3 months,
  train-the-trainer) bracketed by an SVG to five outcome cards (materials, session design,
  hackathons and homework, migration waves, handover), with two full-width arrows underneath
  showing the two-way trade: domain context in, GitOps practice back. Classes `.fanout`,
  `.hub`, `.brace`, `.spokes`/`.spoke`, `.flow`/`.flowrow`; the old `.pathway`, `.stepcard`,
  `.chev` and `.insight` rules were deleted with it.
- **What didn't work** (`#6`): rebuilt, replacing two cards and an `xxx` placeholder. A hero
  SVG chart runs across the top: green bands mark teaching sessions, and a gradient line
  rises through each one then decays through the gap that follows, trending down over six
  months. **That curve is illustrative, not measured**, and the slide says so in a
  `SHAPE IS ILLUSTRATIVE` label - keep that label if the chart is edited. Below it sit eight
  chips: seven failures plus one green chip for what replaced the programme, then a quote
  strip. Classes `.chartwrap`/`.chd`, `.fchips`/`.fchip` (`.won` for the green one) and
  `.qstrip`, plus a `--red-light` token. The earlier `.failcard`, `.quotecard`, `.swapcard`
  and `dense6` rules were deleted with the layout they served.
- **Conditions** (`#7`): rebuilt from seven equal `numcard` boxes into a hero layout. A large
  left panel gives psychological safety the weight the copy always claimed for it ("the most
  evidenced condition of all") with three practical points under it; the other six conditions,
  including the added "Expect the dip", sit right as compact numbered cards. Classes
  `.herowrap`, `.heropanel`, `.supp`/`.suppcard` (`.dip` for the blue one); `.numcard` was
  deleted with the layout it served.
- **Learning priorities by role** (`#8`): realigned with the three curriculum slides that
  follow it, and rebuilt around **two org scenarios**. The three role cards run across the
  top; below them sit two radar webs (grid rings plus spokes, thin outlines, translucent
  fills), each carrying all three roles. Left is a small org with no DevOps function, where
  every shape is broad because if the Mac team does not own the pipeline, the state backend
  and the guardrails then nobody does. Right is a large org like LBG, where the shapes narrow
  but spike on Jamf APIs and Mentoring while Environment and GitOps pull back to the platform
  team. Classes `.roles3`, `.scen2`. The colour chip in each role-card header is the chart
  key, so **chip and polygon colours must stay in step**: junior `--accent-strong`, engineer
  `--accent`, senior `--alt`.

Unconfirmed facts carry amber TODO chips - the deck has a `.todo` chip class and an `--amber`
token for exactly that. Earlier work wired its speakers to `_shared/`.

**The four disciplines are a shared vocabulary.** `#9` (pathway matrix), `#10` (timeline) and
`#12` (skills map) are all built on **Environment, Git, Terraform, GitOps**, and `#12` calls
them "the four core disciplines" in its subtitle. `#8`'s radar now uses those same four plus
Jamf APIs and Mentoring, the two that only start to matter as people move up. If you rename
or re-cut a discipline on any of those four slides, change all four.

Two deliberate decisions on `#8` worth not undoing:

- **Provider architecture and SDK design were removed.** Building the Terraform provider is a
  different job from using it, and no Mac team needs a Go developer to adopt this. It was
  replaced with Jamf Pro API knowledge, which the deck previously never taught at all -
  before this change the only mention of an API anywhere in the deck was one bullet on the
  hiring slide. The senior row now owns the "resource isn't supported yet" triage: does the
  API support it, is it a provider gap, is it worth raising.
- **The senior label is "The escalation point", not "End-to-end mastery"**, because seniors
  are defined here by responsibility rather than by a completed body of knowledge.

Known tension, left as-is on purpose: `#8` organises the curriculum by job grade, while `#9`
organises it by stage of learning (Oriented, Safe Contributor, and so on) and `#6` reports
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

The figures on `#6` are measured, not estimated. They come from
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

- **Six presets**, three dark and three light. Dark: `default` (the original near-black, and
  the only one with no `[data-theme]` block), `deep-green`, `contrast`. Light: `light-paper`,
  `light-slate`, and `jamf` - which is modelled directly on the Jamf Pro admin console
  (white cards on a faint grey canvas, hairline borders, near-black type, Jamf Blue as the
  only strong colour, console icon-tile pastels as the washes). Add a preset by copying a
  block and adding its name to `THEMES` in the theme script.
- **Controls**: `T` cycles, `Shift+T` cycles back, `K` opens the knobs panel. `?theme=<name>`
  wins on load; `?knobs=1` opens the panel. The choice persists in `localStorage`, wrapped in
  try/catch because `file://` can have an opaque origin - losing persistence is fine, throwing
  is not.
- **The knobs panel** lists the primary knobs, hides the fine tints behind a toggle, and
  "Copy CSS" emits a paste-ready `[data-theme="my-theme"]{…}` block.
- **Values marked DERIVED** in the token block are not from the slide 20 colour system; they
  are tints worked out from a documented brand colour, and each says which. Brand colours
  (Mountain Meadow, Tropical Rain Forest, Jamf Blue, Alert Red) are always used exactly.
- **Slide 20 stays canonical.** Its chips keep literal hexes under every theme, because it
  documents the brand palette rather than the active UI. Do not tokenise them.
- **Embedded artwork**: several logos are white-on-transparent PNGs drawn for a dark stage.
  `--art-mono-filter` inverts the monochrome marks (Octocat, cursor) and `--art-plate` sits
  the multicolour ones (Jamf) on a dark plate. These rules are scoped to `html[data-theme]`
  on purpose: applying `filter` at all promotes a compositing layer and shifts antialiasing,
  so the unthemed default must not carry them.
- **Slide copy must stay theme-neutral.** Do not write "the green bands" or "the green chip"
  when a theme can turn them blue.

When changing anything colour-related, screenshot all 20 slides on `default` before and after
and `cmp` them. Tokenising must never alter the default rendering; that check is what catches
a wrong substitution.

- Slides are `<section class="slide">` with no ids except `#s1`. Navigation is by index -
  the URL hash is `#1`..`#20`, not a slide name.
- Notes live in a `data-notes` attribute on each section, shown in an overlay toggled with
  `n`. There is no second-window presenter view and no `presenter.json`.
- Keys: arrows / PageUp / PageDown / space / Home / End to move, `n` notes, `f` fullscreen.
  Clicking the left 28% of the screen goes back, anywhere else forward.
- Speakers are on slide 2 (`#2`), rendered from `_shared/speakers.js`.

Known gaps, none of them addressed:

- The deck uses em-dashes throughout (9 literal, 34 `&mdash;`), against the repo-wide
  no-em-dash rule. Pre-existing; the working rule is that any slide touched by content work
  is brought fully to house style (the Goals and Conditions slides already have been), the
  rest are left alone until touched.
- No spec or provenance file, so the facts on its slides have no recorded source.
- Slot length and which of the three speakers present it are unrecorded.

## Deployment

`.github/workflows/deploy.yml` deploys this repo on merge to `main` (only when
`presentations/**` or the workflow itself changes) and on manual dispatch. It syncs
`presentations/` to S3 with `--delete`, then creates a CloudFront invalidation and waits for
it. A sync alone is not enough, because the distribution uses CachingOptimized and holds
objects at the edge for a day. Last, it rewrites the CloudFront link in `README.md` to
whatever the distribution actually reports and pushes that back to `main`.

The bucket mirrors `presentations/` exactly, so the URL layout is the repo layout:

| Path | Serves |
| --- | --- |
| `/` | `presentations/index.html` (the landing page) |
| `/migrating_an_instance/` | `presentations/migrating_an_instance/index.html` |
| `/training_a_team/` | `presentations/training_a_team/index.html` |
| `/_shared/speakers.js` | `presentations/_shared/speakers.js` |

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
  `../_shared/speakers.js`, which resolves to `/_shared/speakers.js` only because every deck
  sits one level down in a single bucket. A deck nested deeper, or moved to its own bucket,
  loses its speakers.
- **Adding a deck is two edits, not one.** The directory gives you the URL, but it will not
  be reachable from anywhere until you add a card to `presentations/index.html`. That list is
  hand-maintained on purpose: generating it would mean client-side JS or a build step, and
  this site has neither.
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
script src would break:

```sh
"$CHROME" --headless --disable-gpu --window-size=1920,1080 --hide-scrollbars \
  --virtual-time-budget=3000 --screenshot=/tmp/file.png \
  "file:///Users/josephlittle/Github/jnuc-2026/presentations/migrating_an_instance/index.html#s00b"
```

Also check after any structural change:

- Presenter view: same command with `?presenter=1#<slide-id>` at ~1200x760.
- Reader mode: `?reader=1#<slide-id>` - confirms the "More detail" chip placement.
- Timeline: any slide with low-sitting content - the month labels must not clip at the
  canvas edge and content must not collide with the strip.
- Timeline grey state: `#s10` and `#s08` share a range, so shoot both - `s10` highlights in
  accent, `s08` in grey, with the "Dec 25" label accent in both. `#s00` accent, `#s00b` grey
  covers the first-slide case.

(Serving over HTTP avoids file:// restrictions and is required for presenter sync; any port
works. The timeline and reader-mode checks are `migrating_an_instance` specifics -
`training_a_team` has neither.)
