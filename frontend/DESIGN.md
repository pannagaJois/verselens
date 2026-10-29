---
name: Field Notebook & Literary Lens
colors:
  surface: '#fff8f3'
  surface-dim: '#dfd9d4'
  surface-bright: '#fff8f3'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f9f2ed'
  surface-container: '#f3ede8'
  surface-container-high: '#ede7e2'
  surface-container-highest: '#e7e1dc'
  on-surface: '#1d1b18'
  on-surface-variant: '#4c463c'
  inverse-surface: '#32302d'
  inverse-on-surface: '#f6f0ea'
  outline: '#7d766a'
  outline-variant: '#cec5b7'
  surface-tint: '#6c5d38'
  primary: '#6c5c38'
  on-primary: '#ffffff'
  primary-container: '#86754e'
  on-primary-container: '#080400'
  inverse-primary: '#d9c497'
  secondary: '#665e48'
  on-secondary: '#ffffff'
  secondary-container: '#ebdec3'
  on-secondary-container: '#6b624c'
  tertiary: '#585d77'
  on-tertiary: '#ffffff'
  tertiary-container: '#707591'
  on-tertiary-container: '#ffffff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#f6e0b2'
  primary-fixed-dim: '#d9c497'
  on-primary-fixed: '#251a00'
  on-primary-fixed-variant: '#534522'
  secondary-fixed: '#eee1c6'
  secondary-fixed-dim: '#d2c5ab'
  on-secondary-fixed: '#211b0a'
  on-secondary-fixed-variant: '#4e4632'
  tertiary-fixed: '#dde1ff'
  tertiary-fixed-dim: '#c1c5e4'
  on-tertiary-fixed: '#151a31'
  on-tertiary-fixed-variant: '#41455f'
  background: '#fff8f3'
  on-background: '#1d1b18'
  surface-variant: '#e7e1dc'
typography:
  display-lg:
    fontFamily: Source Serif 4
    fontSize: 44px
    fontWeight: '400'
    lineHeight: 54px
    letterSpacing: -0.02em
  display-md:
    fontFamily: Source Serif 4
    fontSize: 36px
    fontWeight: '400'
    lineHeight: 46px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Source Serif 4
    fontSize: 28px
    fontWeight: '500'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Source Serif 4
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Source Serif 4
    fontSize: 22px
    fontWeight: '500'
    lineHeight: 30px
  poem-verse:
    fontFamily: Source Serif 4
    fontSize: 19px
    fontWeight: '400'
    lineHeight: 34px
    letterSpacing: 0.01em
  body-lg:
    fontFamily: Source Serif 4
    fontSize: 17px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Source Serif 4
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  marginalia:
    fontFamily: Source Serif 4
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.03em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.05em
  code-scansion:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.1em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-compact: 1rem
  margin: 2.5rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system defines a desktop poetry analysis workspace that bridges the tactile intimacy of an analog writer’s journal with the clarity and rigor of a modern computational tool. The aesthetic pairs warm, aged paper surfaces with crisp typographic craft—honoring the slow, contemplative act of close reading while maintaining structured precision for linguistic evidence and thematic inquiry.

The style fuses **Editorial Papercraft** and **Calm Minimalist Workspace**:
- **Tactile Paper Surfaces:** Warm ivory, oatmeal, and aged parchment card sheets layered over a quiet desk ground.
- **Deep Pigment & Ink:** Text and borders simulate rich iron-gall ink and charcoal pencil lines rather than cold, neutral digital greys.
- **Literary Restraint:** Muted deep bronze-olive serves as an intellectual anchor, paired with faded warm grey and midnight navy accents for semantic tagging, marginalia, and rhyme/meter visualization.
- **Quiet Depth:** Subtle deckled paper borders, fine hairlines, and ambient warm shadows evoke sheets lying flat across a study desk without intrusive skeuomorphic clutter.

## Colors

The palette reproduces the tactile environment of an archivist's desk. The ground canvas evokes weathered parchment (`#ECE5D8`), upon which rested surfaces appear in warm, natural ivory (`#FAF7F0`). 

- **Primary (`#86754E`):** Muted bronze olive. Represents analysis certainty, primary interactive highlights, deep annotations, and active analytical threads.
- **Secondary (`#CCC0A6`):** Soft parchment taupe. Used for secondary accents, subtle container backgrounds, tone shifts, and tactile highlights.
- **Tertiary (`#282D45`):** Midnight navy. Used for structural markers, formal metrics, and rhyme schemes.
- **Neutral (`#7A7672`):** Muted stone neutral used to derive subtle dividers, secondary text, and inactive workspace panels.
- **Text & Structure:** Rendered in rich carbon ink (`#1C1C1A`) for unyielding legibility, supported by pencil lead tones (`#48463F`, `#7B776E`) for metadata, line counts, and secondary notes.

Never use saturated electric tech blues or synthetic purple AI gradients. Every hue should appear naturally pigmented as if absorbed by raw cotton paper.

## Typography

The typographic hierarchy intentionally bifurcates into two distinct voices:

1. **The Poetic & Analytical Voice (Source Serif 4):**
   A classical, human-hewn literary serif used for titles, the central poetry viewport (`poem-verse`), critical essays, and interpretive annotations. In verse display, generous vertical rhythm (`34px` line-height on `19px` font-size) accommodates stanza breaks, inline scansion glyphs, and verse-level highlight brackets.

2. **The Workspace Instrument Voice (Plus Jakarta Sans):**
   A crisp, highly legible contemporary sans-serif engineered for workspace chrome: toolbars, metric tags, scansion notation, line-number coordinates, status indicators, and collapsible inspector panels.

For marginal notes and glosses, use `marginalia` in italics to evoke quick pencil annotations penned in the book margin.

## Layout & Spacing

The workspace employs an **asymmetric 3-pane workbench layout** anchored within a max-width desk bounds of `1560px`:
- **Left Rail (Document & Stanza Navigator):** 280px fixed width. Provides table of contents, historical draft selector, and meter distribution miniatures.
- **Center Canvas (The Reading Sheet):** Fluid (min 600px, max 820px). A clean paper sheet holding the active poem with generous margins, line numbers, and inline highlights.
- **Right Pane (Literary Dimension Inspector):** 380px fixed width. Houses context cards: tonal shifts, rhythmic scansion, thematic clustering, and textual evidence.

### Responsive Reflow
- **Desktop (≥ 1280px):** Full three-pane simultaneous workbench.
- **Tablet / Small Desktop (960px – 1279px):** Left rail collapses into an off-canvas drawer; center canvas and right inspector share the split screen.
- **Mobile (< 960px):** Single-column stacked mode. The poem canvas occupies full width. The inspector transforms into a pull-up bottom sheet triggered by tapping marked verse fragments.

## Elevation & Depth

Visual hierarchy does not rely on synthetic blurred glow or heavy drop-shadows. Instead, elevation simulates the physics of paper cards resting on top of one another:

- **Surface Level 0 (Ground Canvas):** `#ECE5D8` with faint paper pulp texture.
- **Surface Level 1 (Workbench Sheets & Containers):** `#FAF7F0` bordered by a faint ink hairline (`1px solid #DCD5C5`) and cast with a soft, warm ambient shadow:
  `box-shadow: 0 1px 3px rgba(35, 30, 20, 0.04), 0 4px 12px rgba(35, 30, 20, 0.03);`
- **Surface Level 2 (Selected Cards, Modals & Menus):** `#FFFFFF` paired with an elevated paper shadow:
  `box-shadow: 0 4px 6px -1px rgba(28, 28, 26, 0.05), 0 12px 24px -4px rgba(28, 28, 26, 0.07);`
- **Taped & Pinned Notes:** Marginal notes feature slight decorative tilts (`rotate(-0.5deg)` to `rotate(0.8deg)`) and translucent masking tape strips on top edges (`background: rgba(238, 230, 210, 0.65)`).

## Shapes

The geometric form language balances organic softness with typographic discipline:

- **Standard Cards & Panels:** Medium rounding (`0.5rem` / `8px`) softens edges without making cards look bubbly or juvenile, preserving a hand-trimmed stationery appearance.
- **Tags, Pills, & Verse Chips:** Large rounding (`1rem` / `16px`) for tactile ease.
- **Selection Brackets & Evidence Connectors:** Square right-angled pins with fine line weights (`1.5px`) that mirror printing press marks and editorial proofreading notations.

## Components

### Buttons
- **Primary Button:** Background in deep bronze olive (`#86754E`), text in `#FAF7F0`, font `Plus Jakarta Sans` semi-bold (`14px`). Hover drops to `#72633e` with a subtle `translateY(-1px)`.
- **Secondary / Ghost Button:** Transparent background, `1px solid #DCD5C5`, text in `#1C1C1A`. Hover states reveal a paper-tint fill (`#FAF7F0`).
- **Marginal Action Button:** Understated text link with a subtle pencil underline effect that expands on hover.

### Verse Highlights & Annotation Anchors
- Words or lines with attached evidence are highlighted with a soft parchment wash (e.g., `#E5EEEE` for bronze inquiries, `#F6ECE8` for emotional shifts, or pencil yellow `#EED888`).
- Hovering a highlight triggers a `1.5px` solid indicator underline in the matching accent color and brings the corresponding card into focus in the right inspector.

### Cards (Literary Dimension Cards)
- Background `#FAF7F0`, `1px solid #DCD5C5`, `rounded-md` with `space-md` padding.
- Contains a category badge (`label-sm`), card title (`headline-md`), explanatory synthesis (`body-md`), and a blockquote fragment referencing specific line numbers.

### Inputs & Text Areas
- Unfilled poem paste area: Crisp `#FFFFFF` container with faint graph-paper or notebook line rules (`rgba(220, 213, 197, 0.3)` horizontal repeats).
- Active focus state: Accent border (`#86754E`) with zero chromatic glow, maintaining clean, disciplined ink lines.

### Visualizations (Data & Form)
- **Meter & Stress Indicators:** Small, quiet pill sequences above syllables (`˘` unstressed in muted ink, `´` stressed in deep bronze olive).
- **Sentiment & Cadence Trajectory:** Minimalist sparklines drawn with a `1.5px` ink stroke over oatmeal graph-paper tracks, avoiding flashy neon gradients.

### Workspace States
- **Empty State:** Visual metaphor of an open notebook spread with pencil-sketch floral motif and an understated prompt: "Paste a stanza or choose an archival poem to begin close reading."
- **Loading State:** Faint pulsating ink-wash skeleton blocks accompanied by literary status microcopy ("Scanning poetic meter…", "Mapping metaphoric clusters…").
- **Finished Analysis:** Evidence count tag with an option to download a compiled "Field Notebook PDF" report.