# Hermes / Nous Design Tokens

Full spec for reproducing the Hermes Agent (hermes-agent.nousresearch.com) landing-page
aesthetic: engraved classical figures on parchment, ink typography, instrument-panel
precision. "Renaissance print shop meets terminal."

## 1. Color

```css
:root {
  /* surfaces */
  --paper:        #f2efe6;   /* main parchment background */
  --paper-warm:   #ece7d9;   /* alt section background */
  --paper-raised: #f7f5ee;   /* cards, code blocks */

  /* ink */
  --ink:          #16140f;   /* primary text — warm near-black, NEVER pure #000 */
  --ink-soft:     #4d493f;   /* secondary text */
  --ink-faint:    #8a8576;   /* captions, metadata */

  /* lines */
  --rule:         #d8d2c2;   /* hairline borders, dividers */
  --rule-strong:  #b8b19d;

  /* accent — used VERY sparingly (links, one CTA, terminal cursor) */
  --accent:       #b0501f;   /* burnt sienna / printer's red-ochre */
  --accent-ink:   #2b4734;   /* optional deep verdigris green alt */
}
```

Dark variant (terminal sections / footers): invert to `#16140f` background,
`#e8e4d8` text, keep the same accent.

Rules:
- High paper-to-ink ratio. Generous whitespace; the parchment IS the design.
- No gradients except image fades to paper. No shadows except a 1px rule offset
  (`box-shadow: 4px 4px 0 var(--rule)`) for a letterpress feel. No border-radius
  above 2px — corners are square like a printed plate.

## 2. Typography

```css
/* Display serif — old-style, high contrast. Pick one: */
/* 'EB Garamond', 'Cormorant Garamond', 'Playfair Display', 'Spectral' */
--font-display: 'EB Garamond', Georgia, serif;

/* Body — same serif at text sizes, or a quiet grotesque: */
--font-body: 'EB Garamond', Georgia, serif;

/* Mono — for install commands, code, metadata, version strings: */
--font-mono: 'IBM Plex Mono', 'JetBrains Mono', ui-monospace, monospace;
```

Scale & treatment:
- Hero H1: clamp(2.8rem, 7vw, 5.5rem), weight 500–600, line-height 1.05,
  letter-spacing -0.01em. Multi-line with a deliberate break ("The Agent That /
  Grows With You.").
- Section labels / eyebrows: mono, 0.75rem, UPPERCASE, letter-spacing 0.12em,
  color var(--ink-faint). E.g. `OPEN SOURCE • MIT LICENSE`, `FEATURES`,
  `SEE IT IN ACTION`. The bullet `•` separator is a signature detail.
- Body: 1rem–1.125rem, line-height 1.6, max-width 62ch.
- Numbered steps rendered as oversized serif numerals ("1. Install", "2. Configure").

## 3. Texture & atmosphere

- Subtle paper grain over everything: an SVG noise overlay at 2–4% opacity.

```html
<svg style="position:fixed;inset:0;width:100%;height:100%;pointer-events:none;
            opacity:.035;mix-blend-mode:multiply;z-index:9999">
  <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9"
    numOctaves="2" stitchTiles="stitch"/></filter>
  <rect width="100%" height="100%" filter="url(#grain)"/>
</svg>
```

- Hairline rules between sections: `border-top: 1px solid var(--rule)` —
  like rule lines in a printed broadsheet.
- Optional: corner registration marks / crop marks on cards (small `+` glyphs
  positioned absolutely in corners) for the "printer's proof" feel.

## 4. The mythic engraving backgrounds

The figures behind the Hermes hero are classical-statue / mythological etchings,
rendered as ink linework, faded into the parchment so text stays readable.
Reproduce from ANY image with `scripts/engrave.py` (see SKILL.md). Placement:

```css
.hero {
  position: relative;
  isolation: isolate;
}
.hero::before {
  content: "";
  position: absolute; inset: 0;
  background: url('/img/engraving-bg.png') no-repeat;
  background-size: cover;          /* or contain, anchored right */
  background-position: right center;
  opacity: 0.5;                    /* engraving is pre-faded; this is extra safety */
  z-index: -1;
  -webkit-mask-image: linear-gradient(to left, black 30%, transparent 85%);
          mask-image: linear-gradient(to left, black 30%, transparent 85%);
}
```

Good source images for the classical look: public-domain statue photos
(Hermes/Mercury, Winged Victory, Laocoön — Met Open Access, Wikimedia Commons),
or any photo of the user's choosing — the engraver makes anything fit the system.

## 5. Components

**Install/code block** — the centerpiece:
```css
.cmd {
  font-family: var(--font-mono); font-size: .9rem;
  background: var(--paper-raised);
  border: 1px solid var(--rule);
  padding: .9rem 1.1rem;
  display: flex; justify-content: space-between; align-items: center;
}
.cmd .copy { font-family: var(--font-mono); font-size: .7rem;
  text-transform: uppercase; letter-spacing: .1em; color: var(--ink-faint);
  background: none; border: none; cursor: pointer; }
.cmd .copy:hover { color: var(--accent); }
```

**Feature grid**: 2–3 columns, each cell = serif heading (1.25rem, weight 600) +
2-line body in --ink-soft. Cells separated by hairline rules (use grid `gap:1px;
background:var(--rule)` with cells in --paper), not cards with shadows.

**Buttons**: square, 1px ink border, paper background, ink text; hover inverts
(ink bg, paper text). Primary CTA may use --accent border/text.

**Tabs** (macOS/Linux | Windows pattern): mono uppercase labels, active tab gets
a 2px bottom border in --ink.

**Footer**: hairline rule, mono metadata line: `Hermes Agent v0.16.0 · MIT
License · 2026` + external link with `↗` glyph.

## 6. Motion

Minimal. Fade-up on scroll (8px translate, 300ms ease-out) at most.
No parallax, no spring physics. A blinking block cursor `▮` in terminal
demos is the only "alive" element.

## 7. The site frame (printed-plate border)

The whole page sits inside a thin **double rule**, like the border of an engraved
plate or a banknote — and key boxes (the terminal/command block especially) repeat
the same double border. A single hairline reads as a box; a `double` rule reads as
*print*. Keep a margin of bare parchment outside the frame so it breathes.

```css
/* a decorative frame over the whole viewport — persists while scrolling */
.site-frame {
  position: fixed;
  inset: 12px;                       /* margin of paper around the frame */
  border: 3px double var(--rule-strong);
  pointer-events: none;
  z-index: 60;                       /* above content, below grain/modals */
}
@media (max-width: 600px) { .site-frame { inset: 8px; } }

/* the same treatment on a hero box / terminal */
.terminal { border: 3px double var(--rule-strong); }
```

Use `border-style: double` at **≥3px** (thinner collapses to a single line).
Reserve it for the page frame and one or two signature boxes — not every card,
or it gets noisy. Ordinary cells keep the 1px hairline rule from §1.

## 8. Navigation (tall ruled band, logo top-left)

This is the signature Hermes header. It is **not** a row of pill buttons — it is a
**tall ruled band** where the logo sits in the **top-left cell** and the menu items
are cells **clustered to its right**, each separated by a vertical hairline rule.
Those dividers (plus the band's top/bottom rules) are the "boxes" around the items.
Trailing icons (GitHub, Discord…) sit at the far right.

- **Cells fill the band height** (`align-items: stretch`, band ~64–76px) so every
  divider reads as a full-height rule — the ruled-plate look.
- Links: mono **or** the display serif, **UPPERCASE**, wide tracking (~0.18em),
  quiet at **rest opacity ≈ 0.55**, left-clustered after the logo.
- **Hover animation:** a pure **opacity fade** `0.55 → 1` (optionally a faint
  `--paper-raised` cell fill). No movement, no box popping in — just ink coming up.

```css
.site-header .wrap { display: flex; align-items: stretch; min-height: 66px; }
.brand { display: flex; align-items: center; padding-right: 26px;
         border-right: 1px solid var(--rule); }            /* first cell divider */
.nav a {
  display: flex; align-items: center; padding: 0 24px;
  font-family: var(--font-mono); text-transform: uppercase;
  letter-spacing: .18em; font-size: .78rem;
  opacity: .55; border-right: 1px solid var(--rule);        /* cell divider */
  transition: opacity .18s ease, background .18s ease;
}
.nav li:last-child a { border-right: none; }
.nav a:hover { opacity: 1; background: var(--paper-raised); }
.nav-social { margin-left: auto; }                          /* push icons right */
```
