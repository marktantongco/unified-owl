---
name: ui-ux-pro-max-v8-infra
description: >
  UI/UX Pro Max v8.0 — Part A: Design & Style Infrastructure. Activate this skill when the query
  involves design tokens, color palettes, CSS primitives, theming (dark mode, theme switching),
  typography, spacing systems, OKLCH colors, APCA contrast, Tailwind v4 @theme integration,
  container queries, @starting-style, @layer, @scope, @property, CSS nesting, visual direction,
  style selection, font pairings, industry design rules, or embedded data lookups for styles,
  palettes, fonts, and rules. This is the infrastructure layer — it provides the design system
  foundation (tokens, CSS primitives, theme system, data tables) that Part B (components) and
  Part C (data) consume. Do NOT activate for React component implementations, motion presets,
  validation checklists, or advanced component patterns — those belong in Part B.
version: "8.0.0"
---

# UI/UX Pro Max v8.0 — Part A: Design & Style Infrastructure

> **Design System Foundation** — Tokens, palettes, CSS primitives, data tables, and theming.
> Pair with Part B for component implementations and Part C for data lookups.

---

## SILENT PROTOCOL

Before routing, silently evaluate these 3 diagnostic questions:

1. **Is the query about visual foundations?** (colors, typography, spacing, tokens, palettes, CSS features, theming) → **Part A (this file)**
2. **Is the query about component code?** (React components, a11y patterns, motion presets, validation, form handling) → **Part B** (`ui-ux-pro-max-v8-components`)
3. **Is the query a pure data lookup?** (search styles by name, find palette for industry, look up font pair) → **Part C** (`ui-ux-pro-max-v8-data`)

If the answer to Q1 is YES (even partially), activate this skill. If Q2 or Q3 is also YES, cross-reference the other parts.

---

## Intent Routing Decision Tree

```
INCOMING QUERY
│
├─► Mentions: "design token", "color palette", "OKLCH", "spacing scale",
│   "typography", "CSS primitive", "container query", "@layer", "@scope",
│   "dark mode", "theme", "APCA", "contrast", "font pairing"?
│   └─► YES → Part A (this file)
│
├─► Mentions: "component", "React", "accordion", "modal", "form",
│   "a11y pattern", "animation preset", "validation"?
│   └─► YES → Part B (ui-ux-pro-max-v8-components)
│
├─► Mentions: "what style for...", "palette for SaaS", "font for healthcare",
│   "industry rule for fintech"?
│   └─► YES → Part C (ui-ux-pro-max-v8-data) — may need Part A tokens too
│
└─► Full UI/UX build?
    └─► All three parts: A (tokens/CSS) → B (components) → C (data lookup)
```

---

## Core Philosophy

1. **Motion as Thought** — Every animation must encode an idea. If you cannot name the idea, remove the animation.
2. **Paragraph as Object** — A paragraph is a self-contained unit with internal rhythm. Design its container, spacing, and measure as a first-class object.
3. **Content-First Breakpoints** — Never break at device widths. Break when content strains: line length >75ch, grid <2 columns, touch targets overlap.
4. **Reading Line** — Body text max-width: 65-75ch. Headings may exceed but must re-wrap. Non-negotiable.
5. **Typographic Color** — Control perceived density via font-weight, line-height, letter-spacing — not just font-size.
6. **Muted Foundation Colors** — Start desaturated, low-chroma. Reserve high-chroma for interactive elements and status signals.
7. **Tone Check** — Read every piece of microcopy aloud. If it sounds robotic, condescending, or unsure, rewrite it.

---

# MODULE 2: DESIGN TOKEN SCHEMA

## 2.1 OKLCH Color Space

All color tokens use hex-first declaration with OKLCH progressive enhancement via `@supports`.

```css
/* Hex fallbacks declared first — every browser understands these */
:root {
  --color-primary: #2563eb;
  --color-success: #16a34a;
  --color-warning: #ca8a04;
  --color-error: #dc2626;
  --color-info: #0891b2;
}

/* Progressive enhancement: OKLCH override for perceptually uniform values */
@supports (color: oklch(0 0 0)) {
  :root {
    --color-primary: oklch(0.55 0.2 260);
    --color-success: oklch(0.65 0.17 145);
    --color-warning: oklch(0.72 0.15 85);
    --color-error: oklch(0.55 0.22 25);
    --color-info: oklch(0.58 0.12 210);
  }
}
```

### OKLCH Quick Reference

| Concept | Syntax | Example |
|---------|--------|---------|
| Lightness | 0 (black) to 1 (white) | `oklch(0.7 ...)` = 70% lightness |
| Chroma | 0 (gray) to 0.4 (vivid) | `oklch(... 0.2 ...)` = moderate saturation |
| Hue | 0-360 degrees | `oklch(... ... 260)` = blue |

### Converting Hex to OKLCH

```javascript
import { converter } from 'culori';
const hexToOklch = converter('oklch');
hexToOklch('#2563eb'); // { mode: 'oklch', l: 0.55, c: 0.2, h: 260 }
```

## 2.2 Spacing Scale (8-point grid)

```css
:root {
  --space-0: 0;
  --space-px: 1px;
  --space-0-5: 0.125rem;  /* 2px */
  --space-1: 0.25rem;     /* 4px */
  --space-1-5: 0.375rem;  /* 6px */
  --space-2: 0.5rem;      /* 8px */
  --space-2-5: 0.625rem;  /* 10px */
  --space-3: 0.75rem;     /* 12px */
  --space-3-5: 0.875rem;  /* 14px */
  --space-4: 1rem;        /* 16px */
  --space-5: 1.25rem;     /* 20px */
  --space-6: 1.5rem;      /* 24px */
  --space-8: 2rem;        /* 32px */
  --space-10: 2.5rem;     /* 40px */
  --space-12: 3rem;       /* 48px */
  --space-16: 4rem;       /* 64px */
  --space-20: 5rem;       /* 80px */
  --space-24: 6rem;       /* 96px */
  --space-32: 8rem;       /* 128px */
  --space-40: 10rem;      /* 160px */
  --space-48: 12rem;      /* 192px */
  --space-56: 14rem;      /* 224px */
  --space-64: 16rem;      /* 256px */
}
```

## 2.3 Token Mapping: CSS Custom Properties ↔ Tailwind @theme

| CSS Custom Property | Tailwind @theme Property | Utility Class Generated |
|---------------------|--------------------------|------------------------|
| `--space-1` (0.25rem) | `--spacing-1` | `p-1`, `m-1`, `gap-1` |
| `--space-2` (0.5rem) | `--spacing-2` | `p-2`, `m-2`, `gap-2` |
| `--space-4` (1rem) | `--spacing-4` | `p-4`, `m-4`, `gap-4` |
| `--space-6` (1.5rem) | `--spacing-6` | `p-6`, `m-6`, `gap-6` |
| `--space-8` (2rem) | `--spacing-8` | `p-8`, `m-8`, `gap-8` |
| `--color-primary` | `--color-primary` | `bg-primary`, `text-primary` |
| `--color-success` | `--color-success` | `bg-success`, `text-success` |
| `--radius-sm` (0.25rem) | `--radius-sm` | `rounded-sm` |
| `--radius-md` (0.5rem) | `--radius-md` | `rounded-md` |
| `--radius-lg` (0.75rem) | `--radius-lg` | `rounded-lg` |

> **Important:** Define tokens in `:root` for CSS and mirror them in `@theme` for Tailwind utilities. `@theme` values take precedence for Tailwind utility classes; `:root` values are used for `var(--space-*)` in custom CSS.

## 2.4 Typography Scale

```css
:root {
  --font-size-xs: 0.75rem;     /* 12px */
  --font-size-sm: 0.875rem;    /* 14px */
  --font-size-base: 1rem;      /* 16px */
  --font-size-lg: 1.125rem;    /* 18px */
  --font-size-xl: 1.25rem;     /* 20px */
  --font-size-2xl: 1.5rem;     /* 24px */
  --font-size-3xl: 1.875rem;   /* 30px */
  --font-size-4xl: 2.25rem;    /* 36px */
  --font-size-5xl: 3rem;       /* 48px */
  --font-size-6xl: 3.75rem;    /* 60px */
  --font-size-7xl: 4.5rem;     /* 72px */
  --font-size-8xl: 6rem;       /* 96px */
  --font-size-9xl: 8rem;       /* 128px */
}
```

### Font Weight Tokens

```css
:root {
  --font-weight-thin: 100;
  --font-weight-extralight: 200;
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;
  --font-weight-black: 900;
}
```

### Line Height Tokens

```css
:root {
  --leading-none: 1;
  --leading-tight: 1.1;
  --leading-snug: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 1.75;
}
```

### Border Tokens

```css
:root {
  --border-width-0: 0;
  --border-width-1: 1px;
  --border-width-2: 2px;
  --border-width-4: 4px;
  --border-width-8: 8px;
}

:root {
  --radius-none: 0;
  --radius-sm: 0.25rem;   /* 4px */
  --radius-md: 0.5rem;    /* 8px */
  --radius-lg: 0.75rem;   /* 12px */
  --radius-xl: 1rem;      /* 16px */
  --radius-2xl: 1.5rem;   /* 24px */
  --radius-3xl: 2rem;     /* 32px */
  --radius-full: 9999px;
}
```

### Shadow Tokens

```css
:root {
  --shadow-xs: 0 1px 2px rgb(0 0 0 / 0.05);
  --shadow-sm: 0 1px 3px rgb(0 0 0 / 0.1), 0 1px 2px rgb(0 0 0 / 0.06);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  --shadow-inner: inset 0 2px 4px rgb(0 0 0 / 0.05);
}
```

### Opacity Tokens

```css
:root {
  --opacity-0: 0;  --opacity-5: 0.05;  --opacity-10: 0.1;
  --opacity-20: 0.2;  --opacity-25: 0.25;  --opacity-30: 0.3;
  --opacity-40: 0.4;  --opacity-50: 0.5;  --opacity-60: 0.6;
  --opacity-70: 0.7;  --opacity-75: 0.75;  --opacity-80: 0.8;
  --opacity-90: 0.9;  --opacity-95: 0.95;  --opacity-100: 1;
}
```

### Z-Index Tokens

```css
:root {
  --z-behind: -1;
  --z-base: 0;
  --z-dropdown: 10;
  --z-sticky: 20;
  --z-overlay: 30;
  --z-modal: 40;
  --z-popover: 50;
  --z-toast: 60;
  --z-tooltip: 70;
  --z-max: 9999;
}
```

### Breakpoint Tokens (Content-First)

```css
:root {
  --bp-xs: 375px;    /* Minimum viable mobile */
  --bp-sm: 640px;    /* Content reflow point */
  --bp-md: 768px;    /* Sidebar can appear */
  --bp-lg: 1024px;   /* Two-column comfortable */
  --bp-xl: 1280px;   /* Three-column possible */
  --bp-2xl: 1536px;  /* Maximum readable container */
}
```

## 2.5 Typography Principles

### Reading Line

```css
.prose {
  max-width: 70ch; /* Optimal reading measure */
}
h1, h2, h3 {
  max-width: 30ch; /* Tighter for visual impact */
}
```

### Content-First Breakpoints

Break when:
- Line length exceeds 75 characters → add margin or switch to multi-column
- Grid collapses below 2 usable columns → stack vertically
- Touch targets overlap → increase spacing or change layout
- Navigation items wrap to a second line → convert to hamburger

```css
.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr));
}
```

### Typographic Color

```css
/* Light typographic color — airy, readable */
.body-light {
  font-weight: 400;
  line-height: 1.7;
  letter-spacing: 0.01em;
  color: #374151;
}

/* Dense typographic color — authoritative, compact */
.body-dense {
  font-weight: 500;
  line-height: 1.4;
  letter-spacing: -0.01em;
  color: #111827;
}
```

### Muted Foundation Colors

```css
:root {
  /* Foundation: low chroma (OKLCH chroma < 0.05) */
  --surface-base: oklch(0.98 0.01 260);
  --surface-raised: oklch(1.0 0.00 0);
  --surface-sunken: oklch(0.95 0.01 260);

  /* Interactive: moderate chroma (0.1 - 0.2) */
  --interactive-primary: oklch(0.55 0.20 260);
  --interactive-hover: oklch(0.50 0.22 260);

  /* Status: high chroma (0.15 - 0.25) */
  --status-success: oklch(0.65 0.17 145);
  --status-error: oklch(0.55 0.22 25);
  --status-warning: oklch(0.72 0.15 85);
}
```

## 2.6 APCA Contrast Algorithm (WCAG 3.0)

### APCA Lc Values (Lightness Contrast)

| Use Case | Minimum Lc | Preferred Lc |
|----------|-----------|-------------|
| Body text (< 18px) | Lc 60 | Lc 75 |
| Body text (18px+, 400wt) | Lc 45 | Lc 60 |
| Body text (24px+, 700wt) | Lc 30 | Lc 45 |
| Large text (36px+, 700wt) | Lc 25 | Lc 30 |
| UI components (borders, icons) | Lc 15 | Lc 30 |

### APCA Usage

```javascript
// npm install apca-w3
// Exports: calcAPCA(textColor, bgColor), reverseAPCA(lc, bgColor, direction)
const textRgb = [55, 65, 81];    // #374151
const bgRgb = [255, 255, 255];   // #ffffff
const contrastLc = calcAPCA(textRgb, bgRgb);
// Returns Lc value like 63.5 — compare against thresholds above

// Reverse lookup: find minimum foreground color for Lc 60 on white background
const minForeground = reverseAPCA(60, bgRgb, 'fg');
```

### Dual Validation Strategy (2026 Transition)

```javascript
function meetsContrast(textColor, bgColor, fontSize, fontWeight) {
  // WCAG 2.x check (required for legal compliance)
  const ratio = wcagContrast(textColor, bgColor);
  const wcagPass = fontSize >= 18 && fontWeight >= 700 ? ratio >= 3 : ratio >= 4.5;

  // APCA check (future-proof)
  const lc = calcAPCA(hexToRgb(textColor), hexToRgb(bgColor));
  const apcaPass = fontSize >= 24 && fontWeight >= 700 ? lc >= 30
    : fontSize >= 18 ? lc >= 45 : lc >= 60;

  return { wcagPass, apcaPass, ratio, lc };
}
```

## 2.7 Tailwind v4 @theme Integration

Tailwind v4 eliminates `tailwind.config.js`. All customization in CSS via `@theme`.

```css
@import "tailwindcss";

@theme {
  /* Colors — OKLCH tokens */
  --color-primary: oklch(0.55 0.20 260);
  --color-primary-hover: oklch(0.50 0.22 260);
  --color-success: oklch(0.65 0.17 145);
  --color-warning: oklch(0.72 0.15 85);
  --color-error: oklch(0.55 0.22 25);
  --color-info: oklch(0.58 0.12 210);

  /* Surfaces */
  --color-surface-base: oklch(0.98 0.01 260);
  --color-surface-raised: oklch(1.0 0.00 0);
  --color-surface-sunken: oklch(0.95 0.01 260);

  /* Spacing — 8-point grid */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;

  /* Typography */
  --font-body: "Inter", system-ui, sans-serif;
  --font-heading: "Plus Jakarta Sans", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;

  /* Border radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;

  /* Shadows */
  --shadow-card: 0 1px 3px rgb(0 0 0 / 0.1);
  --shadow-elevated: 0 10px 15px -3px rgb(0 0 0 / 0.1);

  /* Animations */
  --animate-fade-in: fadeIn 0.3s ease-out;
  --animate-slide-up: slideUp 0.3s ease-out;
  --animate-scale-in: scaleIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```

### Usage: v3 vs v4

```html
<!-- Tailwind v3 (deprecated): -->
<button class="bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)]">

<!-- Tailwind v4 (correct): -->
<button class="bg-primary text-white hover:bg-primary-hover">
```

### Migration

```bash
npx @tailwindcss/upgrade
```

Key changes: `tailwind.config.js` → `@theme` in CSS; `extend.colors` → `--color-*` in `@theme`; arbitrary values → direct token references; plugins → mostly built-in; content array → automatic via CSS import detection.

---

# MODULE 3: MODERN CSS PRIMITIVES

## 3.1 Container Queries

Component-level responsiveness — break free from viewport-only media queries.

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: var(--space-4);
  }
}

@container card (max-width: 399px) {
  .card {
    display: flex;
    flex-direction: column;
  }
}
```

### Container Query Units

```css
.sidebar {
  font-size: clamp(0.875rem, 1.5cqw, 1.125rem);
  padding: 2cqh 3cqw;
}
```

### Tailwind v4 Container Query Utilities

```html
<div class="card-container">
  <div class="@md:flex-row @lg:grid-cols-3 flex flex-col gap-4">
    <div class="@md:w-1/2 @lg:w-1/3">Card 1</div>
    <div class="@md:w-1/2 @lg:w-1/3">Card 2</div>
    <div class="@md:w-1/2 @lg:w-1/3">Card 3</div>
  </div>
</div>
```

Custom container breakpoints in `@theme`:

```css
@theme {
  --container-sm: 480px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
}
```

## 3.2 @starting-style

Animate elements entering the DOM. Define BOTH entry (via `@starting-style`) and exit (via transitions on closed state).

```css
/* Entry animation: dialog opening */
dialog[open] {
  opacity: 1;
  transform: scaleY(1);
  transition: opacity 0.3s ease-out, transform 0.3s ease-out,
    overlay 0.3s allow-discrete, display 0.3s allow-discrete;

  @starting-style {
    opacity: 0;
    transform: scaleY(0.9);
  }
}

/* Exit animation: dialog closing */
dialog {
  opacity: 0;
  transform: scaleY(0.9);
  transition: opacity 0.2s ease-in, transform 0.2s ease-in,
    overlay 0.2s allow-discrete, display 0.2s allow-discrete;
}
```

> Exit requires `display: Xs allow-discrete` and `overlay: Xs allow-discrete` to animate before element removal.

### Non-dialog Example

```css
.modal {
  transition: opacity 0.3s, transform 0.3s;
  opacity: 1;
  transform: translateY(0);

  @starting-style {
    opacity: 0;
    transform: translateY(20px);
  }
}
```

## 3.3 @layer

Organize CSS by specificity tier to prevent specificity wars.

```css
@layer base, components, utilities;

@layer base {
  *, *::before, *::after { box-sizing: border-box; }
  body { font-family: var(--font-body); line-height: var(--leading-normal); }
  h1, h2, h3 { line-height: var(--leading-tight); }
}

@layer components {
  .btn { /* ... */ }
  .card { /* ... */ }
  .input { /* ... */ }
}

@layer utilities {
  .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
}
```

## 3.4 @scope CSS

Limit styles to a specific DOM subtree — prevents style leakage without BEM or CSS Modules. `@layer` manages specificity; `@scope` manages reach.

```css
@scope (.card) {
  .title {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
  }

  .body {
    color: var(--color-text-secondary);
  }

  @scope (.card:is(.card)) {
    .title {
      font-size: var(--font-size-lg); /* Nested card titles are smaller */
    }
  }
}

/* Scope with lower boundary */
@scope (.page-layout) to (.user-content) {
  h2 {
    font-family: var(--font-heading);
    margin-top: var(--space-8);
  }
  p {
    max-width: 70ch;
    line-height: var(--leading-relaxed);
  }
}
```

### When to Use @scope vs @layer vs Container Queries

| Feature | Controls | Use Case |
|---------|----------|----------|
| `@scope` | Where styles apply | Component isolation, preventing leakage |
| `@layer` | Specificity order | Organizing base/components/utilities |
| `@container` | Responsive behavior | Component-level responsive design |
| CSS Nesting | Readability | Writing component-scoped styles concisely |

Use all four together: `@layer` for specificity architecture, `@scope` for component boundaries, `@container` for responsive behavior within scopes, and nesting for concise authoring inside scopes.

## 3.5 @property (Animatable Custom Properties)

Register custom properties to enable CSS transitions/animations on gradients, colors, and complex values.

```css
@property --gradient-angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}

@property --hue {
  syntax: '<number>';
  initial-value: 260;
  inherits: false;
}

@property --opacity {
  syntax: '<number>';
  initial-value: 0;
  inherits: false;
}

/* Animate registered properties */
.gradient-border {
  background: conic-gradient(from var(--gradient-angle), oklch(0.55 0.20 var(--hue)), oklch(0.55 0.20 calc(var(--hue) + 60)), oklch(0.55 0.20 var(--hue)));
  animation: rotate-gradient 3s linear infinite;
}

@keyframes rotate-gradient {
  to {
    --gradient-angle: 360deg;
    --hue: 320;
  }
}

.fade-element {
  opacity: var(--opacity);
  transition: --opacity 0.3s ease-out;
}

.fade-element.visible {
  --opacity: 1;
}
```

### Animated Gradient Mesh Background

```css
@property --mesh-hue-1 { syntax: '<number>'; initial-value: 260; inherits: false; }
@property --mesh-hue-2 { syntax: '<number>'; initial-value: 320; inherits: false; }
@property --mesh-hue-3 { syntax: '<number>'; initial-value: 200; inherits: false; }

.mesh-bg {
  background:
    radial-gradient(ellipse at 20% 50%, oklch(0.55 0.20 var(--mesh-hue-1) / 0.3), transparent 50%),
    radial-gradient(ellipse at 80% 20%, oklch(0.55 0.20 var(--mesh-hue-2) / 0.3), transparent 50%),
    radial-gradient(ellipse at 50% 80%, oklch(0.55 0.20 var(--mesh-hue-3) / 0.3), transparent 50%),
    var(--surface-base);
  animation: mesh-shift 8s ease-in-out infinite alternate;
}

@keyframes mesh-shift {
  to {
    --mesh-hue-1: 320;
    --mesh-hue-2: 180;
    --mesh-hue-3: 280;
  }
}
```

## 3.6 CSS Nesting

```css
.card {
  background: var(--surface-raised);
  border-radius: var(--radius-lg);
  padding: var(--space-6);

  & .card-header {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    margin-bottom: var(--space-4);
  }

  & .card-body {
    color: var(--color-text-secondary);
    line-height: var(--leading-relaxed);
  }

  &:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
  }

  @media (prefers-reduced-motion: reduce) {
    &:hover {
      transform: none;
    }
  }
}
```

### Nesting Best Practices

- **Max depth: 3 levels.** Beyond 3, extract inner elements into own `@scope` component.
- **Always use `&`** for pseudo-classes (`&:hover`), pseudo-elements (`&::before`), modifiers (`&.is-active`).
- **`@media` nesting does NOT increase specificity.** `@media` is a conditional rule, not a specificity modifier. Concern is source-order precedence — later rules win at same specificity. Use `@container` or `@layer utilities` for overrides.
- **Prefer `@scope` over deep nesting** for component isolation.

```css
/* BAD: 4+ levels deep */
.card { & .content { & .list { & .item { & .link { /* specificity nightmare */ } } } } }
/* BAD: Universal selector nesting */
.component { & * { /* broad, hard-to-override */ } }

/* GOOD: 2-level nesting with @scope */
@scope (.card) {
  .title { font-size: var(--font-size-xl); }
  .body { color: var(--color-text-secondary); }
  &:hover { box-shadow: var(--shadow-lg); }
}
```

## 3.7 content-visibility

```css
.long-list-item {
  content-visibility: auto;
  contain-intrinsic-size: auto 200px;
}

.below-fold-section {
  content-visibility: hidden;
  contain-intrinsic-size: auto 800px;
}
```

On pages with 1000+ items, `content-visibility: auto` can reduce rendering time by 70-90%.

## 3.8 Anchor Positioning

Position tooltips/popovers relative to their anchor without JavaScript.

```css
.button {
  anchor-name: --my-button;
}

.tooltip {
  position: fixed;
  position-anchor: --my-button;
  top: anchor(bottom);
  left: anchor(center);
  translate: -50% 8px;
}

.tooltip {
  position-try-fallbacks: --bottom, --top, --right;
}

@position-try --bottom {
  top: anchor(bottom);
  left: anchor(center);
}

@position-try --top {
  bottom: anchor(top);
  left: anchor(center);
}
```

## 3.9 View Transitions API

```css
.hero-image { view-transition-name: hero; }
.page-title { view-transition-name: title; }

::view-transition-old(hero) { animation: fade-out 0.25s ease-out; }
::view-transition-new(hero) { animation: fade-in 0.25s ease-in; }
::view-transition-group(*) { animation-duration: 0.3s; }
```

## 3.10 contrast-color() Function

> **Aspirational:** In Interop 2026 focus but not yet baseline. Current syntax only accepts a single color argument.

```css
.button-primary {
  background: var(--color-primary);
  color: contrast-color(var(--color-primary));
}

/* With fallback */
.button-primary {
  background: var(--color-primary);
  color: #ffffff;
  @supports (color: contrast-color(red)) {
    color: contrast-color(var(--color-primary));
  }
}
```

Use `contrast-color()` for simple binary decisions (white vs black). Use APCA for fine-grained contrast auditing with specific Lc values.

## 3.11 Additional Modern CSS Features

### text-wrap: balance

```css
h1, h2, h3 { text-wrap: balance; }
.card-title { text-wrap: balance; max-width: 30ch; }
```

### Popover API

```html
<button popovertarget="menu">Open Menu</button>
<div id="menu" popover="auto">
  <ul><li>Option 1</li><li>Option 2</li></ul>
</div>
```

```css
[popover] {
  margin: auto;
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--color-border);
  transition: opacity 0.2s, transform 0.2s,
    overlay 0.2s allow-discrete, display 0.2s allow-discrete;
  @starting-style {
    opacity: 0;
    transform: scale(0.95);
  }
}
```

### interpolate-size

```css
.accordion-content {
  interpolate-size: allow-keywords;
  overflow: hidden;
  height: 0;
  transition: height 0.3s ease-out;
}
.accordion-content.open {
  height: auto;
}
```

### Scroll-Driven Animations

```css
.parallax-element {
  animation: parallax linear both;
  animation-timeline: scroll();
  animation-range: entry 0% cover 30%;
}

@keyframes parallax {
  from { transform: translateY(50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.reveal-card {
  animation: reveal linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}

@keyframes reveal {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
```

---

# MODULE 7: DATA TABLE REFERENCES

The full data tables (60 UI styles, 48 color palettes, 36 font pairings, 21 industry rules) are stored as CSV files in the `ui-ux-pro-max-v8-data` skill for efficient lookup. Reference them when you need to match an industry/domain to a specific style, palette, font, or rule.

## CSV File Map

| Data Category | CSV Path | Content |
|---------------|----------|---------|
| UI Styles | `ui-ux-pro-max-v8-data/data/styles.csv` | 60 curated styles with performance, a11y, key effects |
| Color Palettes | `ui-ux-pro-max-v8-data/data/colors.csv` | 48 palettes with OKLCH + Hex, primary/secondary/CTA/bg/text |
| Font Pairings | `ui-ux-pro-max-v8-data/data/typography.csv` | 36 verified Google Fonts pairs with mood, best-for, URLs |
| Industry Rules | `ui-ux-pro-max-v8-data/data/ui-reasoning.csv` | 21 rules: pattern, style, color mood, typography, effects, anti-patterns |
| Landing Patterns | `ui-ux-pro-max-v8-data/data/landing.csv` | 8 landing page patterns with conversion focus |
| UX Guidelines | `ui-ux-pro-max-v8-data/data/ux-guidelines.csv` | Accessibility and UX audit guidelines |
| Web Interface | `ui-ux-pro-max-v8-data/data/web-interface.csv` | Web interface audit criteria |
| Charts | `ui-ux-pro-max-v8-data/data/charts.csv` | Chart type recommendations |
| Icons | `ui-ux-pro-max-v8-data/data/icons.csv` | Icon library recommendations |
| Products | `ui-ux-pro-max-v8-data/data/products.csv` | Product type to style mapping |
| React Performance | `ui-ux-pro-max-v8-data/data/react-performance.csv` | React performance patterns |
| Framework Stacks | `ui-ux-pro-max-v8-data/data/stacks/*.csv` | Per-framework implementation guides (nextjs, react, vue, svelte, astro, etc.) |

## Quick Reference: Data Categories

### UI Styles (60)
- **General (42):** Minimalism, Neumorphism, Glassmorphism, Brutalism, 3D, Dark Mode OLED, Accessible & Ethical, Claymorphism, Aurora UI, Retro-Futurism, Flat Design 2.0, Soft UI, Neubrutalism, Bento Grid, Y2K, Cyberpunk, Biophilic, AI-Native UI, Vaporwave, Dimensional Layering, Exaggerated Minimalism, Kinetic Typography, Parallax Storytelling, Swiss Modernism 2.0, HUD/Sci-Fi FUI, Pixel Art, Spatial UI, E-Ink/Paper, Gen Z Chaos, Biomimetic, Anti-Polish/Raw, Tactile Digital, Nature Distilled, Interactive Cursor, Voice-First, 3D Product Preview, Gradient Mesh/Aurora Evolved, Editorial Grid, Chromatic Aberration, Vintage Analog, Liquid Glass
- **Landing (8):** Hero-Centric, Conversion-Optimized, Feature-Rich Showcase, Minimal & Direct, Social Proof-Focused, Interactive Demo, Trust & Authority, Storytelling-Driven
- **Dashboard (10):** Data-Dense, Heat Map, Executive, Real-Time Monitoring, Drill-Down, Comparative, Predictive, User Behavior, Financial, Sales Intelligence

### Color Palettes (48 — OKLCH + Hex)
SaaS & Tech (8), E-Commerce (8), Healthcare (6), Finance & Insurance (6), Beauty & Wellness (6), Creative & Education (8), Restaurant & Hospitality (6)

### Font Pairings (36 — Verified Google Fonts)
Sans-Serif Pairs (16), Serif + Sans Pairs (12), Monospace + Sans Pairs (5), Self-Hosted Fonts (16 alternatives)

### Industry Rules (21)
Technology & SaaS (5), Finance & Insurance (4), Healthcare (4), E-Commerce & Services (4), Creative & Education (4)

---

# MODULE 9: THEME SYSTEM

## 9.1 Dark Mode Implementation

Dark mode must be more than inverting colors. Never simply swap white for black — adjust chroma, lightness, and shadow depth for the dark environment.

### CSS Custom Properties Strategy

```css
:root {
  color-scheme: light dark;
}

/* Light theme (default) */
:root {
  --color-bg-primary: oklch(0.98 0.01 260);
  --color-bg-secondary: oklch(1.0 0.00 0);
  --color-bg-tertiary: oklch(0.95 0.01 260);
  --color-text-primary: oklch(0.15 0.02 260);
  --color-text-secondary: oklch(0.35 0.02 260);
  --color-text-tertiary: oklch(0.55 0.02 260);
  --color-border: oklch(0.88 0.01 260);
  --color-primary: oklch(0.55 0.20 260);
  --color-primary-hover: oklch(0.50 0.22 260);
  --shadow-sm: 0 1px 3px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px rgb(0 0 0 / 0.1);
  --elevation-base: oklch(0.13 0.02 260);
  --elevation-raised: oklch(0.18 0.02 260);
  --elevation-overlay: oklch(0.22 0.02 260);
}

/* Dark theme */
[data-theme="dark"] {
  color-scheme: dark;
  --color-bg-primary: oklch(0.15 0.02 260);
  --color-bg-secondary: oklch(0.18 0.02 260);
  --color-bg-tertiary: oklch(0.22 0.02 260);
  --color-text-primary: oklch(0.90 0.01 260);
  --color-text-secondary: oklch(0.70 0.02 260);
  --color-text-tertiary: oklch(0.55 0.02 260);
  --color-border: oklch(0.30 0.02 260);
  --color-primary: oklch(0.65 0.18 260);
  --color-primary-hover: oklch(0.70 0.20 260);
  --shadow-sm: 0 1px 3px rgb(0 0 0 / 0.3);
  --shadow-md: 0 4px 6px rgb(0 0 0 / 0.4);
  --shadow-lg: 0 10px 15px rgb(0 0 0 / 0.5);
  --elevation-base: oklch(0.13 0.02 260);
  --elevation-raised: oklch(0.18 0.02 260);
  --elevation-overlay: oklch(0.22 0.02 260);
}
```

### Dark Mode Anti-Patterns

1. **Pure black backgrounds** (#000000) — Too harsh. Use oklch(0.12-0.18).
2. **Desaturated accent colors** — Colors appear more vibrant on dark backgrounds. Reduce chroma by 10-20%.
3. **High-contrast white text** — Pure #ffffff causes halation. Use oklch(0.87-0.92).
4. **Elevation via shadows** — In dark mode, use background lightness instead (lighter = higher).
5. **Same border color as light** — Borders need to be lighter in dark mode.

### System Preference Detection

```css
@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    --color-bg-primary: oklch(0.15 0.02 260);
    --color-bg-secondary: oklch(0.18 0.02 260);
    /* ... all dark tokens ... */
  }
}

/* Manual override takes priority over OS preference */
[data-theme="light"] { /* light tokens */ }
[data-theme="dark"] { /* dark tokens */ }
```

## 9.2 React Theme Provider

```tsx
'use client';

import { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';

const ThemeContext = createContext<{
  theme: Theme;
  setTheme: (theme: Theme) => void;
  resolved: 'light' | 'dark';
}>({ theme: 'system', setTheme: () => {}, resolved: 'light' });

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window === 'undefined') return 'system';
    const stored = localStorage.getItem('theme') as Theme | null;
    if (stored) return stored;
    const currentTheme = document.documentElement.getAttribute('data-theme');
    if (currentTheme === 'dark' || currentTheme === 'light') return currentTheme;
    return 'system';
  });
  const [resolved, setResolved] = useState<'light' | 'dark'>(() => {
    if (typeof window === 'undefined') return 'light';
    const currentTheme = document.documentElement.getAttribute('data-theme');
    return currentTheme === 'dark' ? 'dark' : 'light';
  });

  useEffect(() => {
    const root = document.documentElement;
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const applyTheme = () => {
      const isDark = theme === 'dark' || (theme === 'system' && mediaQuery.matches);
      root.setAttribute('data-theme', isDark ? 'dark' : 'light');
      setResolved(isDark ? 'dark' : 'light');
    };

    applyTheme();
    mediaQuery.addEventListener('change', applyTheme);
    return () => mediaQuery.removeEventListener('change', applyTheme);
  }, [theme]);

  const handleSetTheme = (newTheme: Theme) => {
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme: handleSetTheme, resolved }}>
      {children}
    </ThemeContext.Provider>
  );
}

function useTheme() {
  return useContext(ThemeContext);
}
```

### Preventing FOUC

Add this inline script in `<head>` before any CSS loads:

```html
<script>
  (function() {
    const theme = localStorage.getItem('theme');
    if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  })();
</script>
```

## 9.3 Tailwind v4 Dark Mode Integration

```css
@import "tailwindcss";

/* Enable class-based dark mode via data-theme attribute */
@custom-variant dark (&:where([data-theme="dark"], [data-theme="dark"] *));
```

```html
<div class="bg-white dark:bg-gray-900">
  <p class="text-gray-900 dark:text-gray-100">Hello</p>
</div>
```

## 9.4 Complete Dark Mode Token Architecture

```css
/* Light theme (default) */
:root {
  --color-bg-primary: oklch(0.98 0.01 260);
  --color-bg-secondary: oklch(1.0 0.00 0);
  --color-bg-tertiary: oklch(0.95 0.01 260);
  --color-bg-inverse: oklch(0.15 0.02 260);
  --color-text-primary: oklch(0.15 0.02 260);
  --color-text-secondary: oklch(0.35 0.02 260);
  --color-text-tertiary: oklch(0.55 0.02 260);
  --color-text-inverse: oklch(0.98 0.01 260);
  --color-border-default: oklch(0.88 0.01 260);
  --color-border-strong: oklch(0.75 0.02 260);
  --color-primary: oklch(0.55 0.20 260);
  --color-primary-hover: oklch(0.50 0.22 260);
  --color-primary-subtle: oklch(0.55 0.20 260 / 0.1);
  --color-success: oklch(0.65 0.17 145);
  --color-warning: oklch(0.72 0.15 85);
  --color-error: oklch(0.55 0.22 25);
  --color-info: oklch(0.58 0.12 210);
  --shadow-sm: 0 1px 3px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px rgb(0 0 0 / 0.1);
}

/* Dark theme — complete token override */
.dark,
[data-theme="dark"] {
  --color-bg-primary: oklch(0.15 0.02 260);
  --color-bg-secondary: oklch(0.18 0.02 260);
  --color-bg-tertiary: oklch(0.22 0.02 260);
  --color-bg-inverse: oklch(0.98 0.01 260);
  --color-text-primary: oklch(0.90 0.01 260);
  --color-text-secondary: oklch(0.70 0.02 260);
  --color-text-tertiary: oklch(0.55 0.02 260);
  --color-text-inverse: oklch(0.15 0.02 260);
  --color-border-default: oklch(0.30 0.02 260);
  --color-border-strong: oklch(0.40 0.02 260);
  --color-primary: oklch(0.65 0.18 260);
  --color-primary-hover: oklch(0.70 0.20 260);
  --color-primary-subtle: oklch(0.65 0.18 260 / 0.15);
  --color-success: oklch(0.70 0.15 145);
  --color-warning: oklch(0.78 0.13 85);
  --color-error: oklch(0.65 0.20 25);
  --color-info: oklch(0.65 0.10 210);
  --shadow-sm: 0 1px 3px rgb(0 0 0 / 0.3);
  --shadow-md: 0 4px 6px rgb(0 0 0 / 0.4);
  --shadow-lg: 0 10px 15px rgb(0 0 0 / 0.5);
  --elevation-base: oklch(0.13 0.02 260);
  --elevation-raised: oklch(0.18 0.02 260);
  --elevation-overlay: oklch(0.22 0.02 260);
}
```

Key principles: chroma reduced ~10-20% in dark mode; text never pure white (use oklch 0.87-0.92); elevation via background lightness (lighter = higher).

## 9.5 Theme Transition Animation

```css
html.theme-transition,
html.theme-transition *,
html.theme-transition *::before,
html.theme-transition *::after {
  transition:
    background-color 0.3s ease,
    color 0.3s ease,
    border-color 0.3s ease,
    box-shadow 0.3s ease,
    fill 0.3s ease,
    stroke 0.3s ease !important;
}

@media (prefers-reduced-motion: reduce) {
  html.theme-transition,
  html.theme-transition *,
  html.theme-transition *::before,
  html.theme-transition *::after {
    transition: none !important;
  }
}
```

### React Integration

```tsx
'use client';

import { useCallback } from 'react';

function useThemeTransition() {
  const toggleWithTransition = useCallback((toggleFn: () => void) => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      toggleFn();
      return;
    }

    document.documentElement.classList.add('theme-transition');
    toggleFn();

    const cleanup = () => {
      document.documentElement.classList.remove('theme-transition');
      document.documentElement.removeEventListener('transitionend', cleanup);
    };

    document.documentElement.addEventListener('transitionend', cleanup);
    setTimeout(cleanup, 400);
  }, []);

  return toggleWithTransition;
}
```

### Circle Reveal Animation (Advanced)

```css
@keyframes theme-reveal {
  from {
    clip-path: circle(0% at var(--theme-origin-x) var(--theme-origin-y));
  }
  to {
    clip-path: circle(150% at var(--theme-origin-x) var(--theme-origin-y));
  }
}

html.theme-reveal {
  animation: theme-reveal 0.5s ease-out forwards;
}
```

Set `--theme-origin-x` and `--theme-origin-y` to the toggle button coordinates before triggering.

## 9.6 Color Perception in Dark Mode

1. **Reduce chroma by 10-20%** for interactive and status colors
2. **Increase lightness by 5-10%** for accent colors to maintain visibility
3. **Use subtle color tints** on dark surfaces (e.g., `oklch(0.20 0.02 260)` instead of pure neutral gray)
4. **Test with real content** — color perception changes with surrounding elements

### Elevation in Dark Mode

```css
/* Light mode: shadows indicate elevation */
:root {
  --surface-base: oklch(0.98 0.01 260);
  --surface-raised: oklch(1.0 0.00 0);
  --surface-overlay: oklch(1.0 0.00 0);
}

/* Dark mode: lightness indicates elevation (lighter = higher) */
[data-theme="dark"] {
  --surface-base: oklch(0.13 0.02 260);
  --surface-raised: oklch(0.18 0.02 260);
  --surface-overlay: oklch(0.22 0.02 260);
}
```

## 9.7 Dark Mode Patterns for Common Elements

### Images

```css
[data-theme="dark"] img:not([data-no-dark]) {
  filter: brightness(0.9);
}
[data-theme="dark"] img[data-dark-dim] {
  filter: brightness(0.85);
}
```

### Code Blocks

```css
[data-theme="dark"] pre,
[data-theme="dark"] code {
  background: oklch(0.12 0.02 260);
  color: oklch(0.85 0.02 260);
  border-color: oklch(0.25 0.02 260);
}
[data-theme="dark"] .token.keyword { color: oklch(0.75 0.18 290); }
[data-theme="dark"] .token.string { color: oklch(0.75 0.15 145); }
[data-theme="dark"] .token.comment { color: oklch(0.55 0.02 260); }
```

### Charts

```css
[data-theme="dark"] .chart-grid-line { stroke: oklch(0.30 0.02 260); }
[data-theme="dark"] .chart-text { fill: oklch(0.70 0.02 260); }
[data-theme="dark"] .chart-series-1 { fill: oklch(0.65 0.15 260); }
[data-theme="dark"] .chart-series-2 { fill: oklch(0.65 0.15 145); }
[data-theme="dark"] .chart-series-3 { fill: oklch(0.70 0.12 85); }
```

### Tables

```css
[data-theme="dark"] table { border-color: oklch(0.25 0.02 260); }
[data-theme="dark"] thead { background: oklch(0.15 0.02 260); }
[data-theme="dark"] tbody tr:nth-child(even) { background: oklch(0.16 0.02 260); }
[data-theme="dark"] tbody tr:hover { background: oklch(0.20 0.02 260); }
```

### Common Dark Mode Pitfalls

1. Never use pure black (#000000) — use oklch(0.12-0.18)
2. Never use pure white (#ffffff) for body text — use oklch(0.87-0.92)
3. Never simply invert colors — interactive affordance is lost
4. Always test images/media — bright images appear jarring in dark mode
5. Always test with both themes during development

---

# CROSS-REFERENCES

## Part A → Part B Dependencies

| Part A Module | Part B Consumer | What Gets Passed |
|---------------|----------------|-----------------|
| Module 2 (Design Tokens) | Module 4 (Components) | Token references (`var(--space-*)`, `var(--color-*)`) used in component CSS |
| Module 3 (CSS Primitives) | Module 4 (Component Styles) | Container queries, `@scope`, `@starting-style` applied in component code |
| Module 7 (Data Tables) | Module 1 (Creative Brief Engine) | Style/palette/font/rule data for MATCH step |
| Module 9 (Theme System) | Module 4 (dark: variants) | Dark mode token overrides for component dark states |

## When to Cross-Reference

- **Need to build a component** using these tokens? → Part B (`ui-ux-pro-max-v8-components`)
- **Need to look up specific style/palette/font data?** → Part C (`ui-ux-pro-max-v8-data`)
- **Need motion/animation presets?** → Part B Module 5 (motion presets)
- **Need validation/anti-pattern checks?** → Part B Module 6 (validation)
- **Need GSAP-specific animations?** → `gsap-animations` skill
- **Need React/Next.js performance audit?** → `react-best-practices` skill
- **Need accessibility audit?** → `web-design-guidelines` skill

## External Skill Integration Map

| This Module | Cross-Reference |
|---|---|
| Module 2 (Tokens) | visual-design-foundations: typography scale, spacing system, color theory |
| Module 3 (CSS) | web-design-guidelines: semantic HTML, forms, ARIA |
| Module 3 (CSS) | gsap-animations: for when CSS primitives aren't enough |
| Module 9 (Theme) | react-best-practices: SSR hydration, RSC considerations |

---

## Output Standards

- Default to ASCII-only tokens/variables unless the project already uses Unicode
- Include: spacing scale, type scale, 2-3 font pair options, color tokens (OKLCH + hex), component states
- Always cover: empty/loading/error, keyboard navigation, focus states, contrast
- Run anti-pattern checklist (Part B Module 1.2) before delivery
- Run pre-delivery checklist (Part B Module 6.1) before delivery
- Cross-reference other skills when the task exceeds this skill's scope
