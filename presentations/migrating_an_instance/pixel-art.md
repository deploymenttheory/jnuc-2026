---
name: jnuc_migrating_an_instance
deliverables:
  - id: motif_clicks_to_code
    kind: canvas
    width: 200
    height: 66
    export: { scale: 1, expect: [200, 66] }
    lint: { banding: info, background_contamination: off }
  - id: icon_sheet
    kind: canvas
    width: 192
    height: 128
    export: { scale: 1, expect: [192, 128] }
    lint: { banding: info, background_contamination: off, orphan_pixels: info }
  - id: hero_sentinel
    kind: canvas
    width: 200
    height: 46
    export: { scale: 1, expect: [200, 46] }
    lint: { banding: info, background_contamination: off }
  - id: hero_wave
    kind: canvas
    width: 240
    height: 76
    export: { scale: 1, expect: [240, 76] }
    lint: { banding: info, background_contamination: off }
  - id: hero_staging
    kind: canvas
    width: 200
    height: 40
    export: { scale: 1, expect: [200, 40] }
    lint: { banding: info, background_contamination: off }
  - id: hero_close
    kind: canvas
    width: 160
    height: 60
    export: { scale: 1, expect: [160, 60] }
    lint: { banding: info, background_contamination: off }
  - id: estate_three_instances
    kind: canvas
    width: 160
    height: 44
    export: { scale: 1, expect: [160, 44] }
    lint: { banding: info, background_contamination: off }
palette:
  max_colors: 40
  colors:
    # 0-10: the deck's own tokens, used exactly. Never substitute an approximation.
    - "#00000000"   # 0  transparent
    - "#F6F8F7"     # 1  --c-bg
    - "#FFFFFF"     # 2  --c-surface
    - "#D9E0DD"     # 3  --c-border
    - "#0F1F1A"     # 4  --c-text
    - "#5B6A64"     # 5  --c-text-muted
    - "#006A4D"     # 6  --c-accent
    - "#0B5FA5"     # 7  --c-accent-2
    - "#BE3A2E"     # 8  --c-danger
    - "#177A4C"     # 9  --c-success
    - "#9A6A00"     # 10 --c-warn
    # 11-18: DERIVED tints of the tokens above, for shading only.
    - "#ECF0EE"     # 11 DERIVED bg/border midpoint - soft shade on white
    - "#C4CFCA"     # 12 DERIVED border, one step darker
    - "#8A9993"     # 13 DERIVED muted/border midpoint
    - "#2E4740"     # 14 DERIVED text/muted midpoint
    - "#00553D"     # 15 DERIVED accent shadow
    - "#1E8A66"     # 16 DERIVED accent highlight
    - "#0A4A80"     # 17 DERIVED accent-2 shadow
    - "#3E8BD1"     # 18 DERIVED accent-2 highlight
    # 19-28: DERIVED wash ramps. These slots held the withdrawn speaker portraits'
    # skin and hair; a palette can be recoloured but never shortened, so they were
    # repurposed rather than left as dead entries.
    - "#E8EFEA"     # 19 DERIVED accent wash, lightest
    - "#CDE0D6"     # 20 DERIVED accent wash, light
    - "#A8CCBB"     # 21 DERIVED accent wash, mid
    - "#6FA98F"     # 22 DERIVED accent, desaturated
    - "#E6D9B8"     # 23 DERIVED warn wash
    - "#F0E4C4"     # 24 DERIVED warn wash, light
    - "#33424D"     # 25 slate - terminal and screen chrome
    - "#4E6373"     # 26 slate light
    - "#D9B3AE"     # 27 DERIVED danger wash
    - "#26313A"     # 28 slate shadow
    # 29-31: estate scene casings.
    - "#C9D4CF"     # 29 machine casing mid
    - "#A6B5AF"     # 30 machine casing shadow
    - "#7C8C86"     # 31 machine casing deep shadow
    - "#EFC7C2"     # 32 DERIVED danger wash, light
  locked: false
rules:
  transparent_background: true
  symmetry: none
  outline: { required: false, color_index: null }
  max_canvas: { width: 256, height: 256 }
  lint: { banding: info }
---

Pixel art for the first three slides of the "From Clicks to Code" deck
(`presentations/migrating_an_instance/index.html`). Everything here is embedded
into that file as a base64 PNG data URI - the deck makes zero requests off the
machine, so nothing may ship as a loose asset.

## Shared direction

The deck is a light, near-white theme (`#F6F8F7`) anchored on LBG green
(`#006A4D`), typeset in a serif display face. The art has to sit inside that
without looking like clip art bolted on. So:

- **Palette indices 0-10 are the deck's own tokens, used exactly.** Indices
  11-18 are tints derived from them for shading. No colour outside this ramp,
  and no "close enough" substitutes - a hex that is nearly `--c-accent` will
  read as a mistake next to the real one.
- **Light comes from the top-left**, consistently across every piece.
  Highlights on top and left faces, shadow on bottom and right.
- Transparent background throughout; each piece sits directly on the slide.
- **Exported at 1x and upscaled by the deck, not by the exporter.** Every piece
  ships at its native grid size and the deck scales it with
  `image-rendering: pixelated` at an exact whole-number factor (motif and estate
  x5, icons x3 or x4, heroes x5 or x6). That keeps the embedded base64 small and
  every pixel square;
  a fractional factor would smear the grid, so the CSS widths below are fixed in
  tokens rather than left to percentages.
- No outline requirement. These are architectural and UI subjects where a
  uniform silhouette outline reads as cartoon rather than diagram - outlines
  are drawn by hand only where an edge needs separating from what is behind it.
- Chunky and legible at distance beats detailed. These are read from the back
  of a conference room, not zoomed into.

## motif_clicks_to_code (200x66, slide s00)

Replaces the inline SVG signature motif on the title slide, at the same
displayed size - the SVG was `viewBox="0 0 1000 330"` at 980px wide, and 200x66
at x5 gives 1000x330, so `--motif-w` is 1000px rather than the old 980.

Three beats, left to right, carrying the deck's title:

1. **Clicks.** A Jamf Pro-ish settings window on the left: white surface, grey
   border, a titlebar with three dots, then rows of checkbox-and-label - a
   ticked box, an unticked box, a radio - each label a flat grey bar. A primary
   button at the bottom with a mouse cursor sitting on it, mid-click. Greys and
   whites only (indices 2, 3, 5, 11, 12, 13), because this half is the past.
2. **The turn.** A short accent-green arrow between the two panels.
3. **Code.** A code panel on the right, same white surface and grey border,
   holding four lines of HCL rendered as word-shaped token bars rather than as
   letters - at this size real glyphs would be unreadable from the back of a
   room. Colour them with the deck's own code tokens so the panel matches every
   other code block in the deck: keywords `--c-accent-2` blue (index 7), strings
   `--c-accent` green (index 6), punctuation muted (index 5), plain identifiers
   in index 14 rather than full `--c-text`, because a solid near-black bar has
   far more visual mass than the text it stands for and reads as redaction.
   Break each line into word-sized chunks with gaps, and keep a real indent
   structure - outer line flush left, two nested lines indented, closing brace
   flush left with the caret after it - so it reads as code, not as a bar chart.

The point of the piece is the shift: grey and inert on the left, the deck's live
code colours on the right. Do not colour the left panel green.

## icon_sheet (192x128, every slide)

A 6x4 grid of 32x32 icons on one canvas, cut in CSS with `background-position`.
One sheet rather than twenty files: the deck embeds everything as base64, and
twenty separate images would cost twenty data URIs for the same pixels.

| | col 0 | col 1 | col 2 | col 3 | col 4 | col 5 |
|---|---|---|---|---|---|---|
| **row 0** | headset (support) | laptop (Mac team) | shield (security) | package (app packaging) | magnifier on a page (auditors) | gavel (governance) |
| **row 1** | blueprint (architecture) | cross (rejected) | key (read-only scopes) | brush (instance prep) | slider pane (singletons) | stacked bands (sequencing) |
| **row 2** | spanner (tools) | one-to-many fan (for_each) | flag (exceptions) | tick (validated) | knot (growing pains) | nested boxes (modules) |
| **row 3** | dial (refinements) | bar chart (numbers) | question mark | chain link (links) | wave (migration waves) | branch (repo) |

Rules for drawing them:

- **32x32, and legible at 96px.** These are read at a glance from the back of a
  room, not studied. One idea per icon, no more than three tones plus the
  accent, and no internal detail finer than 2px.
- Every icon sits on a 2px margin inside its cell so nothing bleeds into a
  neighbour when the sheet is cut. Cells are addressed by `--c`/`--r` in CSS.
- Line weight is 2px throughout. A 1px stroke disappears at distance and makes
  the set look inconsistent next to the 2px ones.
- Colour: greys for the neutral body, `--c-accent` for the one thing the icon is
  about. Danger red only where the deck's own copy says something was rejected
  or blocked, amber only for a warning. Never colour a whole icon accent green -
  the accent is the point of emphasis, not the fill.

## The four heroes

Wide narrative pieces for the four slides with real empty space, each carrying a
beat of the story rather than decorating it. All four read left to right and end
on the accent colour, because in every one of them the story ends well.

**hero_sentinel (200x46, s-sentinel).** Three panels matching the slide's three
numbered cards. A wall with a barred gate and a red stop lamp; the same wall with
a narrow open door and an amber lamp, a small clock above it for the time-bound
exception; the wall with the gate standing open and a green lamp. The wall never
changes - only the way through it does.

**hero_wave (240x76, s08).** The seven-step wave as a conveyor. Grey resource
blocks enter from the left, pass under a gantry hung with a padlock (the change
freeze and the revoked GUI writes - step 3, the one the slide marks in red), and
come out the other side green, stacking up at the end. The block colour is the
only thing that changes across the gantry; the blocks themselves are identical
going in and coming out, because a migration moves who owns a resource, not what
the resource is.

**hero_staging (200x40, s-staging).** Wipe, apply, iterate. A cabinet emptied to
two essential slots (APNS and the cloud IdP, the only things kept); production's
configuration pouring across into it; the same cabinet full and even, with a
clean-run tick. This is the slide the talk builds to, so it gets the most
deliberate composition of the four.

**hero_close (160x60, s18).** The payoff, and the only piece that shows the whole
system at rest: three cabinets, all green-lit, wired back to a single repo mark.
Centred rather than left-aligned, since the closing slide is centred.

## estate_three_instances (160x44, slide s01)

Fills the dead space to the right of the pipeline band on the context slide.
Three server machines in a row, standing for Sandbox, Staging and Production,
wired left to right, matching the reading order of the text pipeline beside it.

Each machine is a front-on rack cabinet in casing grey (29/30/31) with a white
face, drive slots as short horizontal bars, and a status LED. What separates
them is the state their labels claim:

- **Sandbox** (left): the only cabinet at a different size - visibly smaller,
  and sparse, with one filled slot, two empty outlines and an LED in muted grey.
  Nothing much lives here.
- **Staging** (middle): the same cabinet as Production but visibly wrong. Its
  slots do not line up with Production's, one slot sits skewed, and its LED is
  amber (index 10). This is the drift the slide's closing line is about, drawn
  rather than asserted - it is the one piece of narrative the art carries, so
  the misalignment must be obvious at a glance, not a subtlety.
- **Production** (right): full and orderly - five slots at an even pitch, every
  one filled, LED in accent green. It is the same cabinet size as Staging on
  purpose, since Staging was meant to mirror it; the two must not differ in
  outline, only in what is inside them.

The connecting cables run at machine mid-height in muted grey, with the
Staging-to-Production run in the same grey - nothing here is a "good" path yet,
this is the estate as found, before any of the migration work.
