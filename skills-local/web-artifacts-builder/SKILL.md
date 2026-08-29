# Web Artifacts Builder

## Context

Use this skill to create a single-file HTML artifact: a fully self-contained interactive web app that works by opening the file directly in a browser with zero dependencies.

**Trigger phrases:** "create an HTML artifact," "single-file web app," "self-contained HTML," "build an interactive demo."

---

## Instructions

### Step 1: Initialize the Project

1. **Create Vite + React + TypeScript project:**
   ```bash
   npm create vite@latest artifact -- --template react-ts && cd artifact
   npm install tailwindcss @tailwindcss/vite lucide-react class-variance-authority clsx tailwind-merge
   npm install -D @types/node
   ```
2. **Add shadcn/ui components** by copying only the source files needed into `src/components/ui/`.
3. **Configure Tailwind** in `vite.config.ts`: add `tailwindcss()` plugin.

### Step 2: Develop Components

4. **Build with React** using functional components and hooks (`useState`, `useReducer`, `useRef`).
5. **Style with Tailwind only.** No external CSS. Use `cn()` helper for conditional classes.
6. **Icons from Lucide React** only. No icon fonts or CDN SVGs.
7. **Make it responsive.** Test at 375px, 768px, and 1280px.
8. **Wire up interactivity.** The artifact must DO something: calculations, visualizations, games, data exploration.
9. **Use semantic HTML:** `<main>`, `<section>`, `<header>`, `<nav>`. Include `aria-label` where needed.
10. **Handle edge cases:** empty states, loading states, error states. Show inline messages, never blank screens.

### Step 3: Bundle into Single HTML

11. **Build:** `npm run build`
12. **Inline all resources** into the single HTML:
    - Small CSS -> inline `<style>` block
    - Small JS -> inline `<script>` block
    - Images -> base64 data URIs or inline SVGs
    - Fonts -> system fonts or inline `@font-face` (no Google Fonts CDN)
13. **Test offline:** open HTML directly in browser. Verify no 404s, all functionality works.
14. **Test cross-browser:** Chrome, Firefox, Safari. Check for layout shifts.
15. **Optimize:** remove unused code, ensure < 2MB total.

---

## Constraints

- Final output MUST be a single HTML file that works offline when opened directly.
- NEVER use external CDNs, API calls, or network resources.
- NEVER use `alert()`, `prompt()`, or `confirm()`. Use inline UI for feedback.
- NEVER use purple gradients, excessive backdrop blur, or hero sections with centered text as design crutches.
- NEVER use uniform `rounded-3xl` everywhere. Vary border radius intentionally.
- NEVER use "AI slop": purple-to-blue gradients, pink-to-orange, overly decorative dividers, or excessive whitespace without purpose.
- Design MUST serve content. Every visual element needs a reason.
- Icons MUST be Lucide React (bundled). No external icon services.
- Color palette: intentional, muted, high contrast. Avoid rainbow defaults.
- Must be immediately useful when opened. No splash screens or loading spinners.

---

## Examples

### Example 1: Personal Finance Dashboard

Single HTML with:
- Month-by-month expense tracker with add/delete transactions
- Input form (category, amount, date, optional note)
- Donut chart (inline SVG) showing spending by category
- Summary cards: total income, expenses, net savings
- Dark charcoal background (#1a1a2e) with warm amber accent (#f0a500)
- Responsive: single column mobile, two columns desktop
- All data in React state (no persistence needed)
- Keyboard accessible: tab through form, Enter to submit

### Example 2: Sorting Algorithm Visualizer

Single HTML with:
- Bar chart visualization of array values (20-50 bars)
- Algorithm selector: Bubble Sort, Quick Sort, Merge Sort, Insertion Sort
- "Generate New Array" button with randomized values
- Speed control slider (0.5x to 5x)
- Step counter and comparison counter displayed in real-time
- Bars animate: red for comparing, green for swapped, neutral default
- Monochrome palette: dark background, teal (#14b8a6) accent
- Respects `prefers-reduced-motion`: shows final sorted state immediately
- Controls bar at top, visualization area fills remaining viewport
