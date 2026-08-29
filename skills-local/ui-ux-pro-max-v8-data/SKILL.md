---
name: ui-ux-pro-max-v8-data
description: >
  Data Lookup Engine for UI/UX PRO MAX v8.0. Provides programmatic access to
  style specifications, color palettes, font pairings, UX rules, chart
  recommendations, icon mappings, landing page patterns, and framework-specific
  guidelines stored as searchable CSV/JSON data files.
version: 8.0.0
---

# UI/UX PRO MAX v8.0 — Part C: Data Lookup Engine

Programmatic data access layer for all Module 7 reference tables. Use this
skill when you need to **look up** specific values, palettes, font pairings,
style specifications, or UX rules — not generate them from scratch.

## Intent Routing

Activate this skill when the query involves:

- Looking up a **color palette** for a specific industry or product type
- Finding **font pairings** that match a mood, category, or use case
- Retrieving **style specifications** (CSS variables, effects, framework compatibility)
- Checking **UX rules** (do/don't guidelines, severity levels)
- Getting **chart type recommendations** for a data visualization need
- Finding the right **icon** for a UI action or category
- Looking up **landing page patterns** for conversion optimization
- Retrieving **framework-specific guidelines** (Next.js, React, Vue, etc.)
- Getting **product-type-to-UI mappings** (what style/pattern for fintech, healthcare, etc.)
- Counting or searching across any data domain

**Do NOT activate** for: generating new designs from scratch, writing component
code (use Part B), or understanding design system philosophy (use Part A).

## Data Inventory

| Domain | File | Records | Description |
|--------|------|---------|-------------|
| `color` | `data/colors.csv` | 96 | Color palettes per product type/industry |
| `style` | `data/styles.csv` | 67 | UI style specifications (22 columns) |
| `typography` | `data/typography.csv` | 56 | Font pairing recommendations |
| `ux` | `data/ux-guidelines.csv` | 98 | UX do/don't guidelines |
| `chart` | `data/charts.csv` | 25 | Chart type recommendations |
| `icon` | `data/icons.csv` | 100 | Lucide icon mappings |
| `reasoning` | `data/ui-reasoning.csv` | 100 | Product → UI pattern reasoning engine |
| `web` | `data/web-interface.csv` | 30 | Web interface guidelines (React/Next.js) |
| `performance` | `data/react-performance.csv` | 44 | React/Next.js performance patterns |
| `landing` | `data/landing.csv` | 30 | Landing page pattern specs |
| `product` | `data/products.csv` | 95 | Product type → style/pattern mapping |
| `stack:astro` | `data/stacks/astro.csv` | 53 | Astro framework best practices |
| `stack:flutter` | `data/stacks/flutter.csv` | 52 | Flutter framework best practices |
| `stack:html-tailwind` | `data/stacks/html-tailwind.csv` | 55 | HTML + Tailwind CSS best practices |
| `stack:jetpack-compose` | `data/stacks/jetpack-compose.csv` | 52 | Jetpack Compose best practices |
| `stack:nextjs` | `data/stacks/nextjs.csv` | 52 | Next.js best practices |
| `stack:nuxt-ui` | `data/stacks/nuxt-ui.csv` | 50 | Nuxt UI best practices |
| `stack:nuxtjs` | `data/stacks/nuxtjs.csv` | 58 | Nuxt.js best practices |
| `stack:react-native` | `data/stacks/react-native.csv` | 51 | React Native best practices |
| `stack:react` | `data/stacks/react.csv` | 53 | React best practices |
| `stack:shadcn` | `data/stacks/shadcn.csv` | 60 | shadcn/ui best practices |
| `stack:svelte` | `data/stacks/svelte.csv` | 53 | Svelte best practices |
| `stack:swiftui` | `data/stacks/swiftui.csv` | 50 | SwiftUI best practices |
| `stack:vue` | `data/stacks/vue.csv` | 49 | Vue.js best practices |

**Total: 24 data files, 1,321 records across 11 core domains + 13 framework stacks.**

## Lookup Script Usage

The primary interface is the Python lookup script at `scripts/lookup.py`.

### List Available Domains

```bash
python3 skills/ui-ux-pro-max-v8-data/scripts/lookup.py --list-domains
```

### Search a Domain

```bash
# Search colors for SaaS industry
python3 skills/ui-ux-pro-max-v8-data/scripts/lookup.py --domain color --query "SaaS" --format json

# Search styles for glassmorphism
python3 skills/ui-ux-pro-max-v8-data/scripts/lookup.py --domain style --query "glassmorphism" --format table

# Search Next.js guidelines for routing
python3 skills/ui-ux-pro-max-v8-data/scripts/lookup.py --domain stack:nextjs --query "routing" --format csv

# Search typography for luxury fonts
python3 skills/ui-ux-pro-max-v8-data/scripts/lookup.py --domain typography --query "luxury" --format json

# Search icons for navigation
python3 skills/ui-ux-pro-max-v8-data/scripts/lookup.py --domain icon --query "navigation" --format table

# Search product mappings for fintech
python3 skills/ui-ux-pro-max-v8-data/scripts/lookup.py --domain product --query "fintech" --format json
```

### Count Matching Records

```bash
python3 skills/ui-ux-pro-max-v8-data/scripts/lookup.py --domain ux --query "animation" --count
```

### Exact Match Only (No Fuzzy)

```bash
python3 skills/ui-ux-pro-max-v8-data/scripts/lookup.py --domain style --query "Glassmorphism" --exact --format json
```

### Search a Specific Column

```bash
python3 skills/ui-ux-pro-max-v8-data/scripts/lookup.py --domain color --query "SaaS" --column "Product Type" --format json
```

### Command-Line Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--domain` | `-d` | Data domain to search |
| `--query` | `-q` | Search term |
| `--format` | `-f` | Output: `json`, `csv`, or `table` (default) |
| `--list-domains` | `-l` | Show all available domains |
| `--count` | `-c` | Return only match count |
| `--exact` | `-e` | Disable fuzzy matching |
| `--column` | | Search only in a specific column |

### Domain Aliases

Short aliases are supported for convenience:
`colors` → `color`, `fonts`/`typo` → `typography`, `next`/`nextjs` → `stack:nextjs`,
`nuxt` → `stack:nuxtjs`, `rn` → `stack:react-native`, `shadcn` → `stack:shadcn`,
`tailwind` → `stack:html-tailwind`, `perf` → `performance`, etc.

## Direct CSV Reference

### colors.csv (96 records)

| Column | Type | Description |
|--------|------|-------------|
| No | int | Row index |
| Product Type | string | Industry/category name (e.g., "SaaS (General)", "Healthcare App") |
| Primary (Hex) | string | Primary brand color |
| Secondary (Hex) | string | Secondary brand color |
| CTA (Hex) | string | Call-to-action button color |
| Background (Hex) | string | Page background color |
| Text (Hex) | string | Text color |
| Border (Hex) | string | Border/divider color |
| Notes | string | Design rationale |

### styles.csv (67 records, 22 columns)

| Column | Type | Description |
|--------|------|-------------|
| No | int | Row index |
| Style Category | string | Style name (e.g., "Glassmorphism", "Brutalism") |
| Type | string | "General", "Landing Page", or "BI/Analytics" |
| Keywords | string | Comma-separated search keywords |
| Primary Colors | string | Primary color palette description |
| Secondary Colors | string | Secondary color palette description |
| Effects & Animation | string | Animation/effect specifications |
| Best For | string | Recommended use cases |
| Do Not Use For | string | Inappropriate use cases |
| Light Mode | string | Light mode compatibility |
| Dark Mode | string | Dark mode compatibility |
| Performance | string | Performance impact rating |
| Accessibility | string | Accessibility compliance level |
| Mobile-Friendly | string | Mobile compatibility rating |
| Conversion-Focused | string | Conversion optimization rating |
| Framework Compatibility | string | Framework-specific ratings |
| Era/Origin | string | Historical origin |
| Complexity | string | Implementation complexity |
| AI Prompt Keywords | string | AI prompt generation keywords |
| CSS/Technical Keywords | string | Technical CSS specifications |
| Implementation Checklist | string | Checklist items |
| Design System Variables | string | CSS custom property definitions |

### typography.csv (56 records)

| Column | Type | Description |
|--------|------|-------------|
| No | int | Row index |
| Font Pairing Name | string | Name (e.g., "Classic Elegant", "Tech Startup") |
| Category | string | "Serif + Sans", "Sans + Sans", "Mono + Sans", etc. |
| Heading Font | string | Font for headings |
| Body Font | string | Font for body text |
| Mood/Style Keywords | string | Mood descriptors |
| Best For | string | Recommended use cases |
| Google Fonts URL | string | Google Fonts sharing URL |
| CSS Import | string | CSS @import statement |
| Tailwind Config | string | Tailwind CSS fontFamily config |
| Notes | string | Usage notes |

### ux-guidelines.csv (98 records)

| Column | Type | Description |
|--------|------|-------------|
| No | int | Row index |
| Category | string | Navigation, Animation, Layout, Touch, Interaction, Accessibility, Performance, Forms, Responsive, Typography, Feedback, Content, Onboarding, Search, Data Entry, AI Interaction, Spatial UI, Sustainability |
| Issue | string | Specific UX issue name |
| Platform | string | Web, Mobile, All, VisionOS |
| Description | string | Issue description |
| Do | string | Best practice |
| Don't | string | What to avoid |
| Code Example Good | string | Good code example |
| Code Example Bad | string | Bad code example |
| Severity | string | High, Medium, Low |

### ui-reasoning.csv (100 records)

| Column | Type | Description |
|--------|------|-------------|
| No | int | Row index |
| UI_Category | string | Product type/industry |
| Recommended_Pattern | string | Landing page pattern recommendation |
| Style_Priority | string | Primary + secondary styles |
| Color_Mood | string | Color palette direction |
| Typography_Mood | string | Typography style |
| Key_Effects | string | Animation/effect specs |
| Decision_Rules | string | JSON conditional rules |
| Anti_Patterns | string | What to avoid |
| Severity | string | Priority level (HIGH/MEDIUM) |

### products.csv (95 records)

| Column | Type | Description |
|--------|------|-------------|
| No | int | Row index |
| Product Type | string | Industry/category name |
| Keywords | string | Search keywords |
| Primary Style Recommendation | string | Primary design style |
| Secondary Styles | string | Alternative styles |
| Landing Page Pattern | string | Recommended landing page pattern |
| Dashboard Style | string | Dashboard pattern (if applicable) |
| Color Palette Focus | string | Color palette direction |
| Key Considerations | string | Important design considerations |

### Stack CSV files (13 frameworks, 49–60 records each)

All stack files share a common schema:

| Column | Type | Description |
|--------|------|-------------|
| No | int | Row index |
| Category | string | Guideline category (Routing, Rendering, etc.) |
| Guideline | string | Guideline name |
| Description | string | Guideline description |
| Do | string | Best practice |
| Don't | string | What to avoid |
| Code Good | string | Good code example |
| Code Bad | string | Bad code example |
| Severity | string | Severity level |
| Docs URL | string | Documentation link |

## Combined JSON Index

The file `data/index.json` contains:
- A complete list of all data files with paths and record counts
- A schema for each file (column names, types, descriptions)
- A `domainMap` object mapping domain keys to file paths

## Cross-References

- **Part A (Design System Context)**: Use Part A for understanding the philosophy
  and principles behind these data tables. Part C provides the raw data; Part A
  explains how to apply it.

- **Part B (Component Implementations)**: Use Part B for ready-made component code.
  Look up the style specifications in Part C first, then find the matching
  component implementation in Part B.

**Data flow**: Part C (lookup) → Part B (components) → Part A (system context)
