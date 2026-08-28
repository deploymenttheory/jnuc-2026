---
name: s-staging-steps
palette:
  max_colors: 40
  locked: false
  colors:
    - "#00000000"   # 0  transparent
    - "#0A1030"     # 1  outline - derived, the template navy taken down so the marks read on both navy cards and the royal-blue stage
    - "#152143"     # 2  template navy - deepest shadow
    - "#273FAB"     # 3  template royal blue - contact shadow
    - "#F4F4F4"     # 4  template off-white - lit faces
    - "#C9D2F0"     # 5  muted cornflower - the plate and the loop
    - "#9AA7D4"     # 6  derived shade of the muted cornflower
    - "#7E8CBC"     # 7  derived deep shade of the muted cornflower
    - "#D1F682"     # 8  template lime - accent and success
    - "#E8FBB8"     # 9  derived light lime
    - "#A6C95C"     # 10 derived shade lime
    - "#FF9E8A"     # 11 template coral - danger
    - "#FFC8BC"     # 12 derived light coral
    - "#C86E5C"     # 13 derived shade coral
    - "#FFC24B"     # 14 template amber - warn
    - "#FFDA8F"     # 15 derived light amber
    - "#C7913A"     # 16 derived shade amber
    - "#FFFFFF"     # 17 specular highlight
    - "#DCE3F7"     # 18 derived cornflower tint
    - "#B4BFE4"     # 19 derived cornflower mid
    - "#63709C"     # 20 derived cornflower deep
    - "#F2FEDA"     # 21 derived lightest lime
    - "#B9DE6E"     # 22 derived lime mid-shade
    - "#86A544"     # 23 derived deepest lime
    - "#FFE0D8"     # 24 derived lightest coral
    - "#E4836F"     # 25 derived coral mid-shade
    - "#A4523F"     # 26 derived deepest coral
    - "#FFE7BC"     # 27 derived lightest amber
    - "#E0A63C"     # 28 derived amber mid-shade
    - "#A0742C"     # 29 derived deepest amber
    - "#1C2C5C"     # 30 derived mid navy - seams and inner shadow
rules:
  transparent_background: true
  symmetry: none
  max_canvas: { width: 384, height: 384 }
  outline:
    required: true
    color_index: 1
  lint:
    # Every icon is deliberately several separate islands (a falling slab must not touch the
    # stack it is landing on, the arrow must float above it, the debris must be clear of the
    # broom). The index-0 bridge idiom would join them, but a bridged cell then counts as
    # silhouette and fails outline_gaps, so the rule is turned off rather than worked around.
    background_contamination: off
    # Long shading ramps across a 384px slab are exactly what banding reports. They are the
    # shading, not an accident, and dithering them would turn to mush at slide distance.
    banding: info
deliverables:
  - id: s-staging-wipe
    kind: canvas
    width: 384
    height: 384
    export: { scale: 1, expect: [384, 384] }
  - id: s-staging-apply
    kind: canvas
    width: 384
    height: 384
    export: { scale: 1, expect: [384, 384] }
  - id: s-staging-iterate
    kind: canvas
    width: 384
    height: 384
    export: { scale: 1, expect: [384, 384] }
---

# Rebuilding staging - three step icons

Three icons for slide 16 of the `migrating_an_instance` deck ("Rebuilding staging"), one
per rebuild step: Wipe, Apply, Iterate. They sit in the open middle of the three gate cards,
between the step number at the top and the verb at title size at the bottom. They are read
from about ten metres, so silhouette beats detail everywhere - but the canvas is large
enough to carry real material detail underneath that silhouette.

Regenerate with Pixelforge; the exported PNGs live beside this file and are embedded in the
deck as base64 data URIs.

## The set

All three are 384x384 on a transparent background, exported at scale 1 so each PNG is its
native resolution. The slide sizes them with a token width and `image-rendering: pixelated`,
so the on-slide size is independent of the canvas size.

They share one device: a **plate** across the foot of the canvas, the staging instance
itself, drawn identically in all three - a slab with a lit top face, a dark seam, and a
shaded front face, outlined 4px all round. Every step then happens on top of that same
plate, so the three icons read as one story rather than three unrelated marks.

Light comes from the **top left** in all three: lit faces on top and left edges, shade on
bottom and right edges, a hard 4px `#0A1030` outline all round. Nothing is a flat fill -
every mass carries a ramp of at least four tones, plus a bevel where two faces meet.

Colour carries the meaning and matches each card's accent:

- coral is what is being destroyed (the debris, the failing crosses),
- lime is what is kept or what has come good (the two retained integrations, the
  configuration blocks, the tick),
- muted cornflower and off-white are neutral machinery (the plate, the arrow, the loop),
- amber is used once, for the broom handle, and nowhere else.

## s-staging-wipe

A stiff yard broom mid-sweep. The handle runs from the upper right down to the left, amber,
with a lit left edge, a specular streak and four darker grain lines running its length; a
banded steel ferrule with three rivets joins it to the head; the head is a wide off-white
brush that flares outward towards the plate, split into eighteen individual bristle strands
with a ragged tip line so it does not read as a solid wedge. Coral debris blocks tumble away
to the left of the head, three of them, at three different sizes and heights so they read as
motion rather than a row; each is bevelled and carries a chipped notch.

Two lime blocks stand untouched on the right of the plate: the APNS connection and the cloud
identity provider, the two things the wipe deliberately kept. They carry the same
configuration rules as the Apply slabs, so they read as kept configuration rather than
generic bricks, and they are the only lime in the icon.

## s-staging-apply

Production's configuration landing on an empty instance. Two lime slabs are already stacked
on the plate; a third is still in the air above them with a clear gap, and a wide off-white
arrow above that points straight down. Each slab is bevelled on all four edges and carries
three dark configuration rules of different lengths across its face, so it reads as a
document rather than a brick. The arrow is shaded across its width from a white left edge
through to a deep cornflower right edge.

## s-staging-iterate

The pass-after-pass loop. A thick circular arrow runs clockwise round the canvas with a
radial gap at the top and a solid arrowhead closing into it; the ring is shaded by angle,
from white at the top left through five tones to the deepest cornflower at the bottom right,
with a lighter inner rim. Inside the loop sits a heavy lime tick, bevelled, with a specular
highlight on its upper-left face. Two coral crosses ride outside the loop on the left, the
errors being carried round and resolved into the tick. The loop stands on the same plate as
the other two.
