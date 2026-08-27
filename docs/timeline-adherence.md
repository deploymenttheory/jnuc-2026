# Timeline adherence: Migrating an instance

This doc is for Joseph to review that each slide in the "From Clicks to Code" deck sits
where it belongs on the migration timeline, ahead of a round of `data-when` corrections.

The deck places slides on a timeline using each `<section>`'s `data-when` attribute. The
value is a single month (`YYYY-MM`) or a month range (`YYYY-MM:YYYY-MM`). A fixed strip at
the bottom of the stage runs Nov 2025 to Jul 2026 (present day); the active slide's month
or range is highlighted on the strip, earlier months are tinted, and the highlight only
turns accent colour when a slide's range moves on from the one before it. Slide order and
`data-when` values below are exactly as they stand on `main` today; nothing has been
changed to produce this doc.

To use the table: fill in the "Month (fill in)" column for each slide with what you think
that slide's true month or range should be. Write a single month like `2025-11`, a range
like `2026-02 to 2026-03`, or the words `no time` if a slide should not sit on the timeline
at all (for example the title, Questions, Links or Thank You slides). The column is left
empty for you. Once it is filled in, a later round will align the deck's `data-when`
attributes to match.

| # | id | Title | Speaker | Timer | Current data-when | Month (fill in) |
|---|---|---|---|---|---|---|
| 1 | s00 | Title | All | 90 | 2025-11 | |
| 2 | s01 | Context, requirements, constraints | Dafydd | 90 | 2025-11 | |
| 3 | s02 | Who touches Jamf Pro | Dafydd | 45 | 2025-11 | |
| 4 | s-workspace | What a Terraform workspace is | Dafydd | 60 | 2025-11 | |
| 5 | s04 | Migration outcomes we considered and rejected | Joseph | 75 | 2025-11 | |
| 6 | s05 | Migration path options | Joseph | 90 | 2025-11 | |
| 7 | s07 | Prerequisites | Gordon | 30 | 2025-11 | |
| 8 | s-singletons | Singletons first | Gordon | 75 | 2025-11 | |
| 9 | s-sentinel | Guardrails you don't own | Gordon | 90 | 2025-11:2026-01 | |
| 10 | s10 | Resource sequencing | Dafydd | 75 | 2025-12:2026-01 | |
| 11 | s08 | Migration wave workflow | Dafydd | 60 | 2025-12:2026-01 | |
| 12 | s11 | Tools and helpers | Gordon | 75 | 2025-12:2026-01 | |
| 13 | s12 | Dynamic creation with for_each | Joseph | 120 | 2026-02:2026-03 | |
| 14 | s13 | for_each exceptions | Joseph | 45 | 2026-02:2026-03 | |
| 15 | s14 | Validating a migration | Joseph | 60 | 2026-02:2026-03 | |
| 16 | s-staging | Rebuilding staging | Dafydd | 120 | 2026-04:2026-05 | |
| 17 | s-pivot | Growing pains | Joseph | 60 | 2026-03 | |
| 18 | s15b | The module structure | Dafydd | 90 | 2026-03 | |
| 19 | s16b | By the numbers | Gordon | 45 | 2026-07 | |
| 20 | s17 | Questions | Anyone | 360 | 2026-07 | |
| 21 | s18 | Links | Anyone | 30 | 2026-07 | |
| 22 | s-thanks | Thank you | none | 15 | 2026-07 | |

## Current stops on the strip

Distinct months the strip currently spans, in the order they occur, with the slides that
land on each:

- **2025-11**: s00, s01, s02, s-workspace, s04, s05, s07, s-singletons, s-sentinel (range start)
- **2025-12**: s10, s08, s11 (range start)
- **2026-01**: s-sentinel (range end), s10, s08, s11 (range end)
- **2026-02**: s12, s13, s14 (range start)
- **2026-03**: s12, s13, s14 (range end), s-pivot, s15b
- **2026-04**: s-staging (range start)
- **2026-05**: s-staging (range end)
- **2026-06**: no slide (gap on the strip)
- **2026-07**: s16b, s17, s18, s-thanks

Two things stand out at a glance: nine slides pile up on 2025-11 at the start of the deck,
and four pile up on 2026-07 at the end, while 2026-06 has no slide at all.

The deck has 22 slides. This doc was generated on 2026-08-27 from `main` at commit f46ff77.
