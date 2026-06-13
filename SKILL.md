---
name: hermes-mythic-design
description: Build pages, landing sites, and UI in the Hermes Agent / Nous Research "engraved parchment" aesthetic — cream paper backgrounds, warm ink typography, old-style serif display type, mono code blocks, hairline rules, and classical-engraving figure backgrounds generated from ANY photo. Use this skill whenever the user mentions the Hermes/Nous look, parchment or vintage-print design, etching/engraving/woodcut style backgrounds, converting a photo into an engraved illustration, or wants a landing page that feels like a Renaissance print shop meets a terminal.
---

# Hermes Mythic Design

Reproduces the design language of hermes-agent.nousresearch.com: ink-on-parchment,
classical engraved figures as faded backgrounds, serif display type, monospace
instrument details. Two capabilities:

1. **Design system** — colors, type, components, texture. Full spec in
   `references/design-tokens.md`. Read it before writing any CSS/HTML/JSX.
2. **Engraving generator** — turn ANY image into a mythic-style etched
   illustration with `scripts/engrave.py`.

## Workflow

### Building a page in this style

1. Read `references/design-tokens.md` (always — it has the exact hex values,
   font stack, and component recipes).
2. If a hero/section background is wanted, generate an engraving first (below),
   then build the page around it.
3. Core rules that must never be broken:
   - Background is parchment `#f2efe6`, text is warm ink `#16140f` — never pure
     white or pure black.
   - Serif for display (EB Garamond / Cormorant), mono for commands and labels
     (IBM Plex Mono), uppercase letter-spaced mono eyebrows with `•` separators.
   - Square corners, hairline `1px` rules instead of shadows, max one accent
     color (`#b0501f`) used sparingly.
   - Engraving backgrounds always fade into the paper (mask-image gradient) so
     text sits on clean parchment.
   - Frame the whole page in a thin **double rule** (`border-style: double`, ≥3px)
     inset from the viewport — the "printed-plate" edge — and repeat it on the
     terminal/command box. See §7 of the reference.
   - Navigation is a **tall ruled band**: logo in the top-left cell, menu items as
     left-clustered cells divided by vertical hairline rules (those are the
     "boxes"), quiet at rest (opacity ≈0.55) with a pure opacity-fade hover — not a
     row of pill buttons. See §8 of the reference.
4. Add the SVG paper-grain overlay (snippet in the reference file).

### Turning any photo into an engraving

Yes, this works on any picture — portraits, statues, pets, boats, products.

```bash
pip install pillow numpy --quiet
# closest match to the Hermes mythic figures:
python scripts/engrave.py photo.jpg engraving.png --style hatch

# ready-to-use hero background (pre-faded toward the paper color):
python scripts/engrave.py photo.jpg hero-bg.png --background --fade-direction left

# other looks:
python scripts/engrave.py photo.jpg out.png --style contour   # banknote/currency lines
python scripts/engrave.py photo.jpg out.png --style stipple   # dotted etching
```

Tuning:
- `--period` 5–10: line spacing. 6–7 for detailed subjects (faces), 9–10 for
  large abstract backgrounds.
- `--contrast` raise to ~1.6 for flat/hazy photos.
- `--gamma` tone curve applied before hatching. Use `0.5–0.8` to lift shadows on
  dark / night photos so they stop blocking up into solid ink (cleaner than just
  dropping contrast); use `1.2–1.6` to deepen a washed-out image. Default `1.0`.
- `--ink` / `--paper`: keep defaults to match the system; they're already the
  token values.
- Subjects with clean silhouettes against plain backgrounds engrave best. If a
  busy photo muddies, suggest cropping the subject first or raising contrast.
- `--background` adds a directional fade to paper; pick `--fade-direction`
  opposite to where the page text will sit.

Always view the output image after generating and iterate on `--period` /
`--contrast` if tones are blocked-up (too dark = lower contrast or raise period).

### Quality checklist before delivering

- [ ] No pure #fff or #000 anywhere
- [ ] Engraving fades into paper; headline text fully readable
- [ ] Mono uppercase eyebrow labels present (e.g. `OPEN SOURCE • MIT LICENSE`)
- [ ] Hairline rules, square corners, letterpress offset shadow at most
- [ ] Grain overlay applied at ≤4% opacity
- [ ] One accent color max, used in ≤3 places
- [ ] Double-rule frame around the page (and the terminal box)
- [ ] Nav is a tall ruled band (logo top-left, cell-divided menu), opacity-fade hover
