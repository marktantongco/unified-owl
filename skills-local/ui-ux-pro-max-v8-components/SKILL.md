---
name: ui-ux-pro-max-components
description: >
  UI/UX Pro Max v8.0 — Components, Patterns & Validation. Use this file when the query is about
  React components, accessibility (a11y), motion presets, validation/audit, advanced patterns,
  or creative brief workflows. Contains Module 1 (Creative Brief Engine), Module 4 (Component Library),
  Module 5 (Motion Presets), Module 6 (Validation & Audit), Module 8 (Cross-Reference Integration),
  and Module 10 (Advanced Patterns). For design tokens, CSS primitives, data tables, and theming,
  see PART-A-INFRASTRUCTURE.md.
version: "8.0.0"
---

# UI/UX Pro Max v8.0 — Part B: Components & Patterns

> **Component Library and Implementation Patterns** — Components, motion, validation, and advanced patterns.
> Pair with Part A for design tokens, CSS primitives, and theming.

## Cross-Reference: Part A Dependencies

This file provides component implementations and patterns. For design tokens, CSS primitives, data tables, and theming, see PART-A-INFRASTRUCTURE.md.
- Module 4 components → consume Part A Module 2 tokens and Module 9 themes
- Module 1 MATCH step → queries Part A Module 7 data tables
- Module 5 motion presets → reference Part A Module 3 CSS primitives
- Module 6 validation → checks Part A Module 2 contrast compliance

---

# MODULE 1: CREATIVE BRIEF ENGINE

## 1.1 Triage Questions (Ask Only What You Must)

| # | Question | Why | Default |
|---|----------|-----|---------|
| 1 | Target platform? | Determines component model and input model | web |
| 2 | Stack (if code)? | Determines syntax and available primitives | html-tailwind |
| 3 | Goal and constraints? | Conversion, speed, brand vibe, WCAG level | conversion + WCAG AA |
| 4 | Existing assets? | Screenshot, Figma, repo, URL, user journey | none |
| 5 | Industry / product type? | Determines palette, typography, pattern | General SaaS |

If the user says "all of it" (design + UX + code + design system), treat as four deliverables and ship in that order.

## 1.2 Anti-Pattern Detection Checklist

Before generating ANY UI, scan the request and existing code for these 34 red flags:

### Critical (Block shipping)

| # | Red Flag | Detection | Fix |
|---|----------|-----------|-----|
| 1 | Math.random() in SSR component | Search for Math.random inside render | Use deterministic pseudo-random: `(index * 9301 + 49297) % 233280 / 233280` |
| 2 | Broken Google Fonts URLs | Font not on fonts.google.com | Replace with verified alternatives (see Part A Module 7.3) |
| 3 | Zero keyboard navigation | Tabs/Accordion with no key handlers | Add roving tabindex + arrow keys + Home/End (see Module 4) |
| 4 | Modal without focus trap | aria-describedby, aria-controls missing | Add focus trap + inert backdrop + aria-describedby |
| 5 | color-scheme without OKLCH fallback | Only hex in dark mode tokens | Add OKLCH with hex fallback for older browsers |
| 6 | Conditional hook calls | useId/useEffect inside if/ternary | Always call hooks unconditionally; use `id ?? generatedId` |
| 7 | forwardRef in React 19 | Using forwardRef() wrapper | Use ref as a regular prop: `function Comp({ ref, ...props })` |
| 8 | useId() called conditionally | `id || useId()` — useId only runs when id is falsy | Always call useId: `const generatedId = useId(); const inputId = id ?? generatedId` |

### High (Must fix before delivery)

| # | Red Flag | Detection | Fix |
|---|----------|-----------|-----|
| 9 | No prefers-reduced-motion | Animation without reduced-motion check | Wrap all animations in motion preference check |
| 10 | Layout-shifting hover states | scale/transform on hover without reserve space | Use opacity/color transitions or reserve transform space |
| 11 | Low-contrast text | Contrast ratio < 4.5:1 for body text | Verify with WCAG contrast checker |
| 12 | Emoji used as UI icons | Emoji characters in button/icon context | Replace with SVG icons (Lucide, Heroicons) |
| 13 | Missing cursor-pointer | Clickable elements without cursor:pointer | Add cursor-pointer to all interactive elements |
| 14 | Instant state changes | No transition on interactive elements | Add transition 150-300ms |
| 15 | Invisible focus states | No :focus-visible styling | Add focus ring with 3px offset |
| 16 | No skip link | Page missing skip-to-content link | Add skip link as first focusable element |
| 17 | Images without alt text | img tags without alt attribute | Add descriptive alt text |
| 18 | Form inputs without labels | Input without associated label | Add label + htmlFor/id association |
| 19 | Contradictory ARIA | e.g., role="status" + aria-hidden="true" | Remove aria-hidden from live regions |
| 20 | Redundant ARIA roles | e.g., role="radiogroup" on fieldset | Remove redundant role when semantic HTML suffices |

### Medium (Should fix)

| # | Red Flag | Detection | Fix |
|---|----------|-----------|-----|
| 21 | Barrel file imports | import { X } from '@/components' | Import directly: import X from '@/components/X' |
| 22 | No content-visibility | Long lists without content-visibility | Add content-visibility: auto on off-screen list items |
| 23 | No CSS nesting | Deep BEM or excessive utility repetition | Use native CSS nesting (see Part A Module 3) |
| 24 | Missing design tokens | Hard-coded color/spacing values | Extract to CSS custom properties |
| 25 | Stale tool references | References to deprecated tools | Update to 2026 ecosystem (see Part A Module 7.4) |
| 26 | No container queries | Responsive via media queries only | Add container queries for component-level responsive |
| 27 | Missing loading/empty/error states | Only happy path implemented | Add all three states for every data-dependent component |
| 28 | No @layer usage | All CSS at same specificity level | Organize into @layer base, components, utilities |
| 29 | Unoptimized images | Raw img tags without lazy loading or optimization | Use framework image component or native loading="lazy" |
| 30 | useCallback + IIFE for derived data | useCallback(() => { ... }, deps)() | Replace with useMemo(() => { ... }, deps) |
| 31 | No useEffect cleanup | Event listeners/timers without cleanup | Add return () => cleanup in useEffect |
| 32 | Hard-coded DOM IDs in forms | id="name" instead of register-managed IDs | Let register() manage IDs via useId() |
| 33 | window.location.reload() for retry | Full page reload on error | Pass onRetry callback prop |
| 34 | No dark: variants on components | Components only styled for light mode | Add dark: variants to all Tailwind classes |

## 1.3 AI-Executable Workflow

```
IDENTIFY  → Parse request, detect industry, stack, constraints
MATCH     → Search data tables (Part A Module 7) for best-fit style/palette/font/rule
COMMIT    → Generate design system with OKLCH tokens (Part A Module 2)
CHECK     → Run anti-pattern checklist (1.2) + validation (Module 6)
```

### IDENTIFY Step
```
Extract from user request:
- product_type: SaaS | e-commerce | healthcare | fintech | ...
- style_keywords: [minimal, dark, playful, ...]
- stack: react | nextjs | vue | svelte | html-tailwind | ...
- a11y_level: AA (default) | AAA | none
- motion_budget: full | reduced | none
```

### MATCH Step
Run the design system generator:
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<product_type> <style_keywords>" --design-system -p "Project Name"
```

Or search individual domains:
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

Available domains: product, style, color, landing, typography, chart, ux, icons, react, web

### COMMIT Step
Generate the design system with persistence:
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name"
```

This creates:
- `design-system/MASTER.md` — Global source of truth
- `design-system/pages/<page>.md` — Page-specific overrides (only deviations)

### CHECK Step
Run the pre-delivery checklist from Module 6 before delivering any code.

---

# MODULE 4: COMPONENT LIBRARY

## 4.0 Component Standards

Every component in this module follows these standards:
- **React 19 patterns**: No forwardRef (use ref prop directly), use() for async data, ref prop exposed on key components
- **Accessibility**: Full keyboard navigation, ARIA attributes, screen reader support
- **Motion**: GSAP integration via useGSAP hook, prefers-reduced-motion respected
- **Deterministic**: No Math.random() in render — use index-based pseudo-random or counters
- **Dark mode**: All components include `dark:` Tailwind variants
- **TypeScript**: All components export their interface types

### Type Exports

All components export their TypeScript interfaces for external use:

```typescript
// Example exported interfaces
export interface AccordionItem { id: string; title: string; content: React.ReactNode; disabled?: boolean; }
export interface SelectOption { value: string; label: string; disabled?: boolean; }
export interface Toast { id: string; message: string; variant: 'success' | 'error' | 'warning' | 'info'; duration?: number; }
// ... etc for all components
```

## 4.1 Accordion

```tsx
'use client';

import { useRef, useState, useCallback, useId } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';

export interface AccordionItem {
  id: string;
  title: string;
  content: React.ReactNode;
  disabled?: boolean;
}

export interface AccordionProps {
  items: AccordionItem[];
  allowMultiple?: boolean;
  ref?: React.Ref<HTMLDivElement>;
}

function Accordion({ items, allowMultiple = false, ref }: AccordionProps) {
  const [openItems, setOpenItems] = useState<Set<string>>(new Set());
  const accordionId = useId();

  const toggle = useCallback((id: string) => {
    setOpenItems(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        if (!allowMultiple) next.clear();
        next.add(id);
      }
      return next;
    });
  }, [allowMultiple]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    const buttons = items.filter(i => !i.disabled);
    const currentIdx = buttons.findIndex(
      b => b.id === (e.target as HTMLElement).getAttribute('data-item-id')
    );

    switch (e.key) {
      case 'ArrowDown': {
        e.preventDefault();
        const next = buttons[(currentIdx + 1) % buttons.length];
        document.getElementById(`${accordionId}-trigger-${next.id}`)?.focus();
        break;
      }
      case 'ArrowUp': {
        e.preventDefault();
        const prev = buttons[(currentIdx - 1 + buttons.length) % buttons.length];
        document.getElementById(`${accordionId}-trigger-${prev.id}`)?.focus();
        break;
      }
      case 'Home': {
        e.preventDefault();
        document.getElementById(`${accordionId}-trigger-${buttons[0].id}`)?.focus();
        break;
      }
      case 'End': {
        e.preventDefault();
        const last = buttons[buttons.length - 1];
        document.getElementById(`${accordionId}-trigger-${last.id}`)?.focus();
        break;
      }
    }
  }, [items, accordionId]);

  return (
    <div
      ref={ref}
      role="region"
      aria-label="Accordion"
      onKeyDown={handleKeyDown}
    >
      {items.map((item) => (
        <AccordionItemComponent
          key={item.id}
          item={item}
          isOpen={openItems.has(item.id)}
          onToggle={() => toggle(item.id)}
          accordionId={accordionId}
        />
      ))}
    </div>
  );
}

function AccordionItemComponent({
  item, isOpen, onToggle, accordionId
}: {
  item: AccordionItem;
  isOpen: boolean;
  onToggle: () => void;
  accordionId: string;
}) {
  const contentRef = useRef<HTMLDivElement>(null);
  const triggerId = `${accordionId}-trigger-${item.id}`;
  const contentId = `${accordionId}-content-${item.id}`;

  useGSAP(() => {
    if (!contentRef.current) return;
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    if (isOpen) {
      gsap.to(contentRef.current, {
        height: 'auto',
        opacity: 1,
        duration: 0.3,
        ease: 'power2.out',
      });
    } else {
      gsap.to(contentRef.current, {
        height: 0,
        opacity: 0,
        duration: 0.2,
        ease: 'power2.in',
      });
    }
  }, { dependencies: [isOpen], scope: contentRef });

  return (
    <div>
      <h3>
        <button
          id={triggerId}
          aria-expanded={isOpen}
          aria-controls={contentId}
          aria-disabled={item.disabled}
          data-item-id={item.id}
          onClick={item.disabled ? undefined : onToggle}
          className="w-full flex items-center justify-between py-4 text-left dark:text-gray-100"
        >
          {item.title}
          <svg
            className={`w-5 h-5 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''} dark:text-gray-300`}
            aria-hidden="true"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
          </svg>
        </button>
      </h3>
      <div
        ref={contentRef}
        id={contentId}
        role="region"
        aria-labelledby={triggerId}
        style={{ height: isOpen ? 'auto' : 0, overflow: 'hidden', opacity: isOpen ? 1 : 0 }}
      >
        <div className="pb-4 dark:text-gray-300">{item.content}</div>
      </div>
    </div>
  );
}
```

## 4.2 Tabs

```tsx
'use client';

import { useState, useCallback, useRef, useId } from 'react';

export interface TabItem {
  id: string;
  label: string;
  content: React.ReactNode;
  disabled?: boolean;
}

export interface TabsProps {
  items: TabItem[];
  defaultTab?: string;
  ref?: React.Ref<HTMLDivElement>;
}

function Tabs({ items, defaultTab, ref }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || items[0]?.id);
  const tabListId = useId();

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    const enabledTabs = items.filter(i => !i.disabled);
    const currentIdx = enabledTabs.findIndex(t => t.id === activeTab);

    let nextIdx = currentIdx;
    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        e.preventDefault();
        nextIdx = (currentIdx + 1) % enabledTabs.length;
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        e.preventDefault();
        nextIdx = (currentIdx - 1 + enabledTabs.length) % enabledTabs.length;
        break;
      case 'Home':
        e.preventDefault();
        nextIdx = 0;
        break;
      case 'End':
        e.preventDefault();
        nextIdx = enabledTabs.length - 1;
        break;
      default:
        return;
    }

    const nextTab = enabledTabs[nextIdx];
    setActiveTab(nextTab.id);
    document.getElementById(`${tabListId}-tab-${nextTab.id}`)?.focus();
  }, [items, activeTab, tabListId]);

  return (
    <div ref={ref}>
      <div role="tablist" aria-label="Content tabs" onKeyDown={handleKeyDown}>
        {items.map((item) => (
          <button
            key={item.id}
            id={`${tabListId}-tab-${item.id}`}
            role="tab"
            aria-selected={activeTab === item.id}
            aria-controls={`${tabListId}-panel-${item.id}`}
            aria-disabled={item.disabled}
            tabIndex={activeTab === item.id ? 0 : -1}
            onClick={() => !item.disabled && setActiveTab(item.id)}
            className="px-4 py-2 dark:text-gray-300 dark:hover:text-white"
          >
            {item.label}
          </button>
        ))}
      </div>
      {items.map((item) => (
        <div
          key={item.id}
          id={`${tabListId}-panel-${item.id}`}
          role="tabpanel"
          aria-labelledby={`${tabListId}-tab-${item.id}`}
          hidden={activeTab !== item.id}
          tabIndex={0}
        >
          {item.content}
        </div>
      ))}
    </div>
  );
}
```

## 4.3 Modal / Dialog

```tsx
'use client';

import { useRef, useEffect, useCallback, useId } from 'react';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  ref?: React.Ref<HTMLDialogElement>;
}

function Modal({ isOpen, onClose, title, description, children, ref }: ModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  // Merge external ref with internal ref
  const setDialogRef = useCallback((node: HTMLDialogElement | null) => {
    (dialogRef as React.MutableRefObject<HTMLDialogElement | null>).current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) (ref as React.MutableRefObject<HTMLDialogElement | null>).current = node;
  }, [ref]);

  const previousFocusRef = useRef<HTMLElement | null>(null);
  const titleId = useId();
  const descId = useId();

  // Open/close dialog
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      dialog.showModal();
    } else {
      // Guard: only close if dialog is actually open (prevents double-close)
      if (dialog.open) {
        dialog.close();
      }
      previousFocusRef.current?.focus();
    }
  }, [isOpen]);

  // Focus trap
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
      return;
    }

    if (e.key !== 'Tab') return;

    const dialog = dialogRef.current;
    if (!dialog) return;

    const focusable = dialog.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'
    );
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last?.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first?.focus();
    }
  }, [onClose]);

  return (
    <dialog
      ref={setDialogRef}
      onClose={onClose}
      onKeyDown={handleKeyDown}
      aria-labelledby={titleId}
      aria-describedby={description ? descId : undefined}
      className="rounded-xl p-0 backdrop:bg-black/50 backdrop:backdrop-blur-sm dark:bg-gray-900 dark:text-gray-100"
    >
      <div className="p-6">
        <h2 id={titleId} className="text-xl font-semibold">{title}</h2>
        {description && (
          <p id={descId} className="mt-2 text-sm text-gray-500 dark:text-gray-400">{description}</p>
        )}
        <div className="mt-4">{children}</div>
        <button
          onClick={onClose}
          className="mt-4 px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-100"
          autoFocus
        >
          Close
        </button>
      </div>
    </dialog>
  );
}
```

> **Fix:** Added `if (dialog.open)` guard before `dialog.close()` to prevent double-close when `onClose` is called while the dialog is already closing. This was caused by both the Escape key handler and the `<dialog>` element's native `onClose` event both calling `onClose`.

### ModalStackProvider for Nested Dialogs

When multiple modals are open simultaneously (e.g., a confirmation dialog on top of a form dialog), screen readers must know which modal is active. The `ModalStackProvider` manages `aria-hidden` across nested modals, ensuring only the topmost modal is accessible to assistive technologies.

```tsx
'use client';
import { createContext, useContext, useState, useCallback, useRef } from 'react';

interface ModalStackEntry {
  id: string;
  element: HTMLElement;
}

const ModalStackContext = createContext<{
  push: (entry: ModalStackEntry) => void;
  pop: (id: string) => void;
} | null>(null);

function ModalStackProvider({ children }: { children: React.ReactNode }) {
  const stackRef = useRef<ModalStackEntry[]>([]);

  const push = useCallback((entry: ModalStackEntry) => {
    if (stackRef.current.length > 0) {
      const prev = stackRef.current[stackRef.current.length - 1];
      prev.element.setAttribute('aria-hidden', 'true');
    }
    stackRef.current.push(entry);
  }, []);

  const pop = useCallback((id: string) => {
    stackRef.current = stackRef.current.filter(e => e.id !== id);
    if (stackRef.current.length > 0) {
      const prev = stackRef.current[stackRef.current.length - 1];
      prev.element.removeAttribute('aria-hidden');
    }
  }, []);

  return (
    <ModalStackContext.Provider value={{ push, pop }}>
      {children}
    </ModalStackContext.Provider>
  );
}
```

## 4.4 Deterministic Skeleton

No Math.random() — SSR-safe with deterministic shimmer patterns. `role="status"` communicates loading state to screen readers; `aria-hidden` is NOT used because it contradicts `role="status"`.

```tsx
export interface SkeletonProps {
  width?: string;
  height?: string;
  index?: number;
}

function Skeleton({ width, height, index = 0 }: SkeletonProps) {
  // Deterministic pseudo-random offset based on index
  const offset = ((index * 9301 + 49297) % 233280) / 233280;
  const delay = `${offset * 1.5}s`;

  return (
    <div
      role="status"
      aria-label="Loading"
      className="animate-pulse rounded-md bg-gray-200 dark:bg-gray-700"
      style={{
        width: width || '100%',
        height: height || '1rem',
        animationDelay: delay,
      }}
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
}

function SkeletonCard({ index }: { index: number }) {
  return (
    <div className="rounded-xl p-4 border border-gray-200 dark:border-gray-700 space-y-3">
      <Skeleton height="2rem" index={index} />
      <Skeleton height="1rem" width="80%" index={index + 1} />
      <Skeleton height="1rem" width="60%" index={index + 2} />
    </div>
  );
}
```

> **Fix:** Removed `aria-hidden="true"` from the Skeleton component. `role="status"` makes this a live region that screen readers should announce — adding `aria-hidden="true"` contradicts that purpose and makes the loading state invisible to assistive technologies.

## 4.5 Skip Link

```tsx
function SkipLink() {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:z-[9999] focus:top-4 focus:left-4 focus:px-4 focus:py-2 focus:bg-white focus:text-black dark:focus:bg-gray-900 dark:focus:text-white focus:rounded focus:shadow-lg"
    >
      Skip to main content
    </a>
  );
}

// Usage: <SkipLink /> must be the FIRST focusable element in the page
// And <main id="main-content"> must exist as the target
```

## 4.6 Focus Trap Utility

```tsx
import { useEffect, useRef } from 'react';

function useFocusTrap(active: boolean) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!active || !containerRef.current) return;

    const container = containerRef.current;
    const focusableSelector = 'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])';

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      const focusable = container.querySelectorAll<HTMLElement>(focusableSelector);
      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last?.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first?.focus();
      }
    };

    container.addEventListener('keydown', handleKeyDown);

    // Auto-focus first element
    const firstFocusable = container.querySelector<HTMLElement>(focusableSelector);
    firstFocusable?.focus();

    return () => container.removeEventListener('keydown', handleKeyDown);
  }, [active]);

  return containerRef;
}
```

## 4.7 Screen Reader Announcer

```tsx
function ScreenReaderAnnouncer() {
  return (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
      id="sr-announcer"
    />
  );
}

// Usage: Update the announcer to communicate state changes
function announceToScreenReader(message: string) {
  const announcer = document.getElementById('sr-announcer');
  if (announcer) {
    announcer.textContent = '';
    requestAnimationFrame(() => {
      announcer.textContent = message;
    });
  }
}
```

## 4.8 Cursor Follower

```tsx
'use client';

import { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';

function CursorFollower() {
  const cursorRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    const cursor = cursorRef.current;
    if (!cursor) return;

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      cursor.style.display = 'none';
      return;
    }

    const moveCursor = (e: MouseEvent) => {
      gsap.to(cursor, {
        x: e.clientX,
        y: e.clientY,
        duration: 0.5,
        ease: 'power2.out',
      });
    };

    window.addEventListener('mousemove', moveCursor);
    return () => window.removeEventListener('mousemove', moveCursor);
  }, { scope: cursorRef });

  return (
    <div
      ref={cursorRef}
      className="pointer-events-none fixed top-0 left-0 z-[9999] w-6 h-6 -ml-3 -mt-3 rounded-full border-2 border-blue-500 mix-blend-difference hidden md:block"
      aria-hidden="true"
    />
  );
}
```

## 4.9 AI-Specific Patterns

### Thinking Indicator

```tsx
function ThinkingIndicator() {
  return (
    <div
      role="status"
      aria-label="AI is thinking"
      className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400"
    >
      <div className="flex gap-1">
        <span className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span>Thinking...</span>
    </div>
  );
}
```

### Uncertainty Notice

```tsx
function UncertaintyNotice({ confidence }: { confidence: 'low' | 'medium' | 'high' }) {
  if (confidence === 'high') return null;

  return (
    <div
      role="note"
      className="flex items-start gap-2 p-3 rounded-lg bg-amber-50 border border-amber-200 dark:bg-amber-900/20 dark:border-amber-800 text-sm"
    >
      <svg className="w-5 h-5 text-amber-500 dark:text-amber-400 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
        <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.168 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
      </svg>
      <div>
        <p className="font-medium text-amber-800 dark:text-amber-300">
          {confidence === 'low' ? 'Low confidence response' : 'Verify this information'}
        </p>
        <p className="text-amber-700 dark:text-amber-400 mt-1">
          {confidence === 'low'
            ? 'This response may contain inaccuracies. Please verify important details independently.'
            : 'This response should be verified before relying on it for critical decisions.'}
        </p>
      </div>
    </div>
  );
}
```

### Composer / Chat Input

```tsx
'use client';

import { useState, useRef, useCallback } from 'react';

function ChatComposer({ onSend, disabled }: {
  onSend: (message: string) => void;
  disabled?: boolean;
}) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = useCallback(() => {
    const trimmed = message.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setMessage('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  }, [message, disabled, onSend]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit]);

  const handleInput = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
  }, []);

  return (
    <div className="flex items-end gap-2 p-3 border rounded-xl dark:border-gray-700 dark:bg-gray-900">
      <textarea
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        onInput={handleInput}
        placeholder="Type a message..."
        disabled={disabled}
        rows={1}
        className="flex-1 resize-none border-0 bg-transparent focus:ring-0 focus:outline-none text-sm dark:text-gray-100"
        aria-label="Chat message input"
      />
      <button
        onClick={handleSubmit}
        disabled={!message.trim() || disabled}
        className="px-3 py-2 rounded-lg bg-blue-600 text-white disabled:opacity-50 disabled:cursor-not-allowed dark:bg-blue-500"
        aria-label="Send message"
      >
        <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path d="M3.105 2.289a.75.75 0 010 1.414l5.372 2.267-5.372 2.267a.75.75 0 000 1.414l14.5 6.125a.75.75 0 001.035-.936l-5.372-13.5a.75.75 0 00-1.398 0L6.893 8.704l-3.788-1.6z" />
        </svg>
      </button>
    </div>
  );
}
```

### AI Controls Panel

```tsx
function AIControlsPanel({ model, temperature, onModelChange, onTemperatureChange }: {
  model: string;
  temperature: number;
  onModelChange: (model: string) => void;
  onTemperatureChange: (temp: number) => void;
}) {
  return (
    <fieldset className="border rounded-lg p-4 space-y-3 dark:border-gray-700">
      <legend className="text-sm font-medium px-2 dark:text-gray-300">AI Settings</legend>
      <div className="flex items-center gap-3">
        <label htmlFor="ai-model" className="text-sm text-gray-600 dark:text-gray-400 w-24">Model</label>
        <select
          id="ai-model"
          value={model}
          onChange={(e) => onModelChange(e.target.value)}
          className="flex-1 px-3 py-1.5 rounded border text-sm dark:bg-gray-800 dark:border-gray-600 dark:text-gray-200"
        >
          <option value="gpt-4o">GPT-4o</option>
          <option value="claude-4">Claude 4</option>
          <option value="gemini-2.5">Gemini 2.5</option>
        </select>
      </div>
      <div className="flex items-center gap-3">
        <label htmlFor="ai-temp" className="text-sm text-gray-600 dark:text-gray-400 w-24">Temperature: {temperature}</label>
        <input
          id="ai-temp"
          type="range"
          min="0"
          max="2"
          step="0.1"
          value={temperature}
          onChange={(e) => onTemperatureChange(parseFloat(e.target.value))}
          className="flex-1"
        />
      </div>
    </fieldset>
  );
}
```

### Conversation Thread

```tsx
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  confidence?: 'low' | 'medium' | 'high';
}

function ConversationThread({ messages }: { messages: Message[] }) {
  return (
    <div
      role="log"
      aria-label="Conversation"
      aria-live="polite"
      className="space-y-4"
    >
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[70ch] rounded-xl px-4 py-3 text-sm ${
              msg.role === 'user'
                ? 'bg-blue-600 text-white dark:bg-blue-500'
                : 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100'
            }`}
          >
            <p>{msg.content}</p>
            {msg.confidence && msg.confidence !== 'high' && (
              <UncertaintyNotice confidence={msg.confidence} />
            )}
            <time
              className="block mt-1 text-xs opacity-60"
              dateTime={msg.timestamp.toISOString()}
            >
              {msg.timestamp.toLocaleTimeString()}
            </time>
          </div>
        </div>
      ))}
    </div>
  );
}
```

### Contextual Actions

```tsx
function ContextualActions({ actions }: {
  actions: Array<{ label: string; icon: string; onClick: () => void; destructive?: boolean }>;
}) {
  return (
    <menu className="flex gap-1" aria-label="Contextual actions">
      {actions.map((action) => (
        <button
          key={action.label}
          onClick={action.onClick}
          className={`p-2 rounded-lg transition-colors text-sm ${
            action.destructive
              ? 'hover:bg-red-100 hover:text-red-700 dark:hover:bg-red-900/30 dark:hover:text-red-400'
              : 'hover:bg-gray-100 dark:hover:bg-gray-800'
          }`}
          aria-label={action.label}
        >
          <span aria-hidden="true">{action.icon}</span>
          <span className="sr-only">{action.label}</span>
        </button>
      ))}
    </menu>
  );
}
```

## 4.10 Image Reveal Component

```tsx
'use client';

import { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger);

function ImageReveal({ src, alt }: { src: string; alt: string }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    gsap.from(containerRef.current, {
      clipPath: 'inset(0 100% 0 0)',
      duration: 0.8,
      ease: 'power3.inOut',
      scrollTrigger: {
        trigger: containerRef.current,
        start: 'top 80%',
        once: true,
      },
    });
  }, { scope: containerRef });

  return (
    <div ref={containerRef} className="overflow-hidden rounded-lg">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={src} alt={alt} className="w-full h-auto object-cover" loading="lazy" />
    </div>
  );
}
```

> **Fix:** Added `gsap.registerPlugin(ScrollTrigger)` before using ScrollTrigger in the animation. Without this registration, GSAP will throw a runtime error.

## 4.11 Select / Dropdown

```tsx
'use client';

import { useState, useRef, useCallback, useId, useEffect } from 'react';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps {
  options: SelectOption[];
  value?: string;
  onChange: (value: string) => void;
  label: string;
  placeholder?: string;
  ref?: React.Ref<HTMLDivElement>;
}

function Select({
  options, value, onChange, label, placeholder = 'Select...', ref
}: SelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const listboxId = useId();
  const buttonId = useId();

  const selectedOption = options.find(o => o.value === value);
  const enabledOptions = options.filter(o => !o.disabled);

  // Close on outside click
  useEffect(() => {
    if (!isOpen) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (!isOpen) { setIsOpen(true); setActiveIndex(0); }
        else { setActiveIndex(prev => Math.min(prev + 1, enabledOptions.length - 1)); }
        break;
      case 'ArrowUp':
        e.preventDefault();
        setActiveIndex(prev => Math.max(prev - 1, 0));
        break;
      case 'Home':
        e.preventDefault();
        setActiveIndex(0);
        break;
      case 'End':
        e.preventDefault();
        setActiveIndex(enabledOptions.length - 1);
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (isOpen && activeIndex >= 0) {
          const option = enabledOptions[activeIndex];
          onChange(option.value);
          setIsOpen(false);
        } else {
          setIsOpen(true);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        break;
    }
  }, [isOpen, activeIndex, enabledOptions, onChange]);

  // Merge refs
  const setRef = useCallback((node: HTMLDivElement | null) => {
    (containerRef as React.MutableRefObject<HTMLDivElement | null>).current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) (ref as React.MutableRefObject<HTMLDivElement | null>).current = node;
  }, [ref]);

  return (
    <div ref={setRef} className="relative">
      <label htmlFor={buttonId} className="block text-sm font-medium mb-1 dark:text-gray-300">{label}</label>
      <button
        id={buttonId}
        role="combobox"
        aria-expanded={isOpen}
        aria-controls={listboxId}
        aria-activedescendant={activeIndex >= 0 ? `${listboxId}-${enabledOptions[activeIndex]?.value}` : undefined}
        aria-haspopup="listbox"
        onClick={() => setIsOpen(prev => !prev)}
        onKeyDown={handleKeyDown}
        className="w-full px-3 py-2 text-left rounded-lg border border-gray-300 bg-white hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/40 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100"
      >
        {selectedOption ? selectedOption.label : <span className="text-gray-400 dark:text-gray-500">{placeholder}</span>}
      </button>
      {isOpen && (
        <ul
          id={listboxId}
          role="listbox"
          aria-label={label}
          className="absolute z-50 mt-1 w-full max-h-60 overflow-auto rounded-lg border border-gray-200 bg-white shadow-lg dark:bg-gray-800 dark:border-gray-600"
        >
          {options.map((option) => {
            const isActive = enabledOptions[activeIndex]?.value === option.value;
            const isSelected = value === option.value;
            return (
              <li
                key={option.value}
                id={`${listboxId}-${option.value}`}
                role="option"
                aria-selected={isSelected}
                aria-disabled={option.disabled}
                onClick={() => !option.disabled && (onChange(option.value), setIsOpen(false))}
                className={`px-3 py-2 cursor-pointer ${
                  option.disabled ? 'opacity-50 cursor-not-allowed' : ''
                } ${isActive ? 'bg-primary/10 dark:bg-primary/20' : ''} ${isSelected ? 'font-semibold' : ''} dark:text-gray-200`}
              >
                {option.label}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
```

## 4.12 Checkbox & Switch

```tsx
export interface CheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  disabled?: boolean;
  id?: string;
}

function Checkbox({
  checked, onChange, label, disabled = false, id
}: CheckboxProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;
  return (
    <div className="flex items-center gap-2">
      <input
        id={inputId}
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary/40 accent-primary dark:border-gray-600"
      />
      <label htmlFor={inputId} className={`text-sm ${disabled ? 'text-gray-400 dark:text-gray-600' : 'text-gray-700 dark:text-gray-300'}`}>
        {label}
      </label>
    </div>
  );
}

export interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  disabled?: boolean;
  id?: string;
}

function Switch({
  checked, onChange, label, disabled = false, id
}: SwitchProps) {
  const generatedId = useId();
  const switchId = id ?? generatedId;
  return (
    <div className="flex items-center gap-3">
      <button
        id={switchId}
        role="switch"
        aria-checked={checked}
        aria-label={label}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary/40 focus:ring-offset-2 dark:focus:ring-offset-gray-900 ${
          checked ? 'bg-primary' : 'bg-gray-200 dark:bg-gray-700'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <span
          aria-hidden="true"
          className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
      <label htmlFor={switchId} className={`text-sm ${disabled ? 'text-gray-400 dark:text-gray-600' : 'text-gray-700 dark:text-gray-300'}`}>
        {label}
      </label>
    </div>
  );
}
```

> **Fix:** Changed from `const inputId = id || useId()` to `const generatedId = useId(); const inputId = id ?? generatedId`. The previous version called `useId()` conditionally — when `id` was provided, `useId()` would not be called due to short-circuit evaluation, violating React's Rules of Hooks. Now `useId()` is always called unconditionally.

## 4.13 Textarea with Character Count

```tsx
export interface TextareaProps {
  value: string;
  onChange: (value: string) => void;
  label: string;
  maxLength?: number;
  placeholder?: string;
  required?: boolean;
  error?: string;
  id?: string;
}

function Textarea({
  value, onChange, label, maxLength, placeholder, required = false, error, id
}: TextareaProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;
  const errorId = `${inputId}-error`;
  const countId = `${inputId}-count`;

  return (
    <div>
      <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {label}
        {required && <span aria-hidden="true" className="text-red-500 ml-1">*</span>}
      </label>
      <textarea
        id={inputId}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        maxLength={maxLength}
        required={required}
        aria-invalid={!!error}
        aria-describedby={`${error ? errorId : ''} ${maxLength ? countId : ''}`.trim() || undefined}
        aria-required={required}
        className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 dark:bg-gray-800 dark:text-gray-100 ${
          error ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
        }`}
        rows={4}
      />
      <div className="flex justify-between mt-1">
        {error && <p id={errorId} role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p>}
        {maxLength && (
          <p id={countId} className="text-xs text-gray-400 dark:text-gray-500 ml-auto" aria-live="polite">
            {value.length}/{maxLength}
          </p>
        )}
      </div>
    </div>
  );
}
```

## 4.14 Form with React Hook Form + Zod

```tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const contactSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email'),
  message: z.string().min(10, 'Message must be at least 10 characters').max(500, 'Message too long'),
  subscribe: z.boolean().optional(),
});

type ContactForm = z.infer<typeof contactSchema>;

function ContactForm({ onSubmit }: { onSubmit: (data: ContactForm) => Promise<void> }) {
  const {
    register, handleSubmit, formState: { errors, isSubmitting }, reset
  } = useForm<ContactForm>({
    resolver: zodResolver(contactSchema),
  });

  const handleFormSubmit = async (data: ContactForm) => {
    await onSubmit(data);
    reset();
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} noValidate className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Name <span aria-hidden="true" className="text-red-500">*</span>
        </label>
        <input
          type="text"
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? 'name-error' : undefined}
          aria-required="true"
          className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 dark:bg-gray-800 dark:text-gray-100 ${
            errors.name ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
          }`}
          {...register('name')}
        />
        {errors.name && <p id="name-error" role="alert" className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.name.message}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Email <span aria-hidden="true" className="text-red-500">*</span>
        </label>
        <input
          type="email"
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
          aria-required="true"
          className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 dark:bg-gray-800 dark:text-gray-100 ${
            errors.email ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
          }`}
          {...register('email')}
        />
        {errors.email && <p id="email-error" role="alert" className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.email.message}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Message <span aria-hidden="true" className="text-red-500">*</span>
        </label>
        <textarea
          rows={4}
          aria-invalid={!!errors.message}
          aria-describedby={errors.message ? 'message-error' : undefined}
          aria-required="true"
          className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 dark:bg-gray-800 dark:text-gray-100 ${
            errors.message ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
          }`}
          {...register('message')}
        />
        {errors.message && <p id="message-error" role="alert" className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.message.message}</p>}
      </div>

      <div className="flex items-center gap-2">
        <input type="checkbox" className="h-4 w-4 rounded accent-primary" {...register('subscribe')} />
        <label className="text-sm text-gray-700 dark:text-gray-300">Subscribe to newsletter</label>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary-hover focus:outline-none focus:ring-2 focus:ring-primary/40 focus:ring-offset-2 dark:focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isSubmitting ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  );
}
```

> **Fix:** Removed hard-coded `id="name"`, `id="email"`, `id="message"` from form inputs. React Hook Form's `register()` manages IDs internally when combined with `useId()`. Hard-coded IDs cause duplicates when multiple form instances are rendered. Error `<p>` elements use stable IDs (`name-error`, `email-error`, `message-error`) that are unique within each form instance.

## 4.15 Toast with CSS Progress Animation

Use CSS `@keyframes` for the progress bar animation instead of `setInterval` for better performance. Multiple toasts stack vertically, each with configurable duration, auto-dismiss, and a close button.

```tsx
'use client';
import { useState, useCallback, useRef } from 'react';

export interface Toast {
  id: string;
  message: string;
  variant: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

let toastCounter = 0;

function ToastContainer({ toasts, onDismiss }: {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}) {
  return (
    <div
      aria-live="polite"
      aria-label="Notifications"
      className="fixed bottom-4 right-4 z-[var(--z-toast)] flex flex-col gap-2"
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: (id: string) => void }) {
  const variantStyles = {
    success: 'bg-green-600 dark:bg-green-700',
    error: 'bg-red-600 dark:bg-red-700',
    warning: 'bg-amber-500 dark:bg-amber-600',
    info: 'bg-blue-600 dark:bg-blue-700',
  };
  const duration = toast.duration || 5000;

  return (
    <div
      role="status"
      className={`relative overflow-hidden rounded-lg text-white shadow-lg animate-toast-in ${variantStyles[toast.variant]}`}
      style={{ minWidth: '300px' }}
    >
      <div className="flex items-center justify-between px-4 py-3">
        <p className="text-sm font-medium">{toast.message}</p>
        <button
          onClick={() => onDismiss(toast.id)}
          className="ml-3 text-white/80 hover:text-white"
          aria-label="Dismiss notification"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
      <div
        className="h-1 bg-white/30"
        style={{
          animation: `toast-progress ${duration}ms linear forwards`,
        }}
        onAnimationEnd={() => onDismiss(toast.id)}
      />
      <style>{`
        @keyframes toast-progress {
          from { width: 100%; }
          to { width: 0%; }
        }
        @keyframes toast-in {
          from { opacity: 0; transform: translateX(100%); }
          to { opacity: 1; transform: translateX(0); }
        }
        .animate-toast-in {
          animation: toast-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

// Hook for managing toast state — uses counter instead of Math.random()
function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const counterRef = useRef(0);

  const addToast = useCallback((message: string, variant: Toast['variant'] = 'info', duration?: number) => {
    const id = `toast-${++counterRef.current}`;
    setToasts(prev => [...prev, { id, message, variant, duration }]);
    return id;
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return { toasts, addToast, dismissToast };
}
```

> **Fix:** Replaced `Math.random().toString(36).slice(2)` with a module-level counter (`toastCounter`) and `useRef`-based counter. Math.random() produces non-deterministic values that violate SSR consistency and the skill's own anti-pattern #1.

## 4.16 Navigation Bar

```tsx
'use client';
import { useState, useCallback, useRef, useId } from 'react';

export interface NavItem {
  label: string;
  href: string;
  active?: boolean;
}

function Navbar({ brand, items, actions }: {
  brand: { label: string; href: string };
  items: NavItem[];
  actions?: React.ReactNode;
}) {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const menuId = useId();
  const mobileMenuRef = useRef<HTMLDivElement>(null);

  return (
    <nav aria-label="Main navigation" className="sticky top-0 z-[var(--z-sticky)] bg-white dark:bg-gray-900 border-b dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <a href={brand.href} className="text-lg font-bold text-gray-900 dark:text-white">
            {brand.label}
          </a>

          <div className="hidden md:flex md:items-center md:gap-1">
            {items.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  item.active
                    ? 'bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white'
                }`}
                aria-current={item.active ? 'page' : undefined}
              >
                {item.label}
              </a>
            ))}
          </div>

          <div className="hidden md:flex md:items-center md:gap-2">
            {actions}
          </div>

          <button
            className="md:hidden p-2 rounded-md text-gray-600 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary/40 dark:text-gray-300 dark:hover:bg-gray-800"
            onClick={() => setIsMobileOpen(prev => !prev)}
            aria-expanded={isMobileOpen}
            aria-controls={menuId}
            aria-label={isMobileOpen ? 'Close menu' : 'Open menu'}
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              {isMobileOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {isMobileOpen && (
        <div
          id={menuId}
          ref={mobileMenuRef}
          className="md:hidden border-t bg-white dark:bg-gray-900 dark:border-gray-700"
          role="region"
          aria-label="Mobile navigation"
        >
          <div className="px-4 py-3 space-y-1">
            {items.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className={`block px-3 py-2 rounded-md text-base font-medium transition-colors ${
                  item.active
                    ? 'bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white'
                }`}
                aria-current={item.active ? 'page' : undefined}
                onClick={() => setIsMobileOpen(false)}
              >
                {item.label}
              </a>
            ))}
          </div>
          {actions && <div className="px-4 py-3 border-t dark:border-gray-700">{actions}</div>}
        </div>
      )}
    </nav>
  );
}
```

## 4.17 Breadcrumb

```tsx
export interface BreadcrumbItem {
  label: string;
  href?: string;
}

function Breadcrumb({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex items-center gap-1 text-sm dark:text-gray-400" itemScope itemType="https://schema.org/BreadcrumbList">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <li
              key={index}
              className="flex items-center gap-1"
              itemProp="itemListElement"
              itemScope
              itemType="https://schema.org/ListItem"
            >
              {index > 0 && (
                <span aria-hidden="true" className="text-gray-400 dark:text-gray-600">/</span>
              )}
              {isLast || !item.href ? (
                <span
                  className="text-gray-500 dark:text-gray-400 font-medium"
                  aria-current="page"
                  itemProp="name"
                >
                  {item.label}
                </span>
              ) : (
                <a
                  href={item.href}
                  className="text-primary hover:underline dark:text-primary-light"
                  itemProp="item"
                >
                  <span itemProp="name">{item.label}</span>
                </a>
              )}
              <meta itemProp="position" content={String(index + 1)} />
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
```

## 4.18 Tooltip

```tsx
'use client';
import { useState, useRef, useId, useEffect } from 'react';

export interface TooltipProps {
  children: React.ReactElement;
  content: string;
  side?: 'top' | 'bottom' | 'left' | 'right';
}

function Tooltip({ children, content, side = 'top' }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState<{ top: number; left: number }>({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLElement>(null);
  const tooltipId = useId();
  const timeoutRef = useRef<NodeJS.Timeout>();

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const show = () => {
    timeoutRef.current = setTimeout(() => {
      if (triggerRef.current) {
        const rect = triggerRef.current.getBoundingClientRect();
        const positions = {
          top: { top: rect.top - 8, left: rect.left + rect.width / 2 },
          bottom: { top: rect.bottom + 8, left: rect.left + rect.width / 2 },
          left: { top: rect.top + rect.height / 2, left: rect.left - 8 },
          right: { top: rect.top + rect.height / 2, left: rect.right + 8 },
        };
        setPosition(positions[side]);
      }
      setIsVisible(true);
    }, 300);
  };

  const hide = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setIsVisible(false);
  };

  return (
    <>
      {isVisible && (
        <div
          id={tooltipId}
          role="tooltip"
          className="fixed z-[var(--z-tooltip)] px-2 py-1 text-xs font-medium text-white bg-gray-900 dark:bg-gray-700 rounded shadow-lg pointer-events-none animate-fade-in"
          style={{
            top: position.top,
            left: position.left,
            transform: side === 'top' ? 'translate(-50%, -100%)' :
                      side === 'bottom' ? 'translate(-50%, 0)' :
                      side === 'left' ? 'translate(-100%, -50%)' :
                      'translate(0, -50%)',
          }}
        >
          {content}
        </div>
      )}
      {typeof children.type === 'string' ? (
        <children.type
          {...children.props}
          ref={triggerRef}
          aria-describedby={isVisible ? tooltipId : undefined}
          onMouseEnter={show}
          onMouseLeave={hide}
          onFocus={show}
          onBlur={hide}
        />
      ) : (
        <span
          ref={triggerRef as React.RefObject<HTMLSpanElement>}
          aria-describedby={isVisible ? tooltipId : undefined}
          onMouseEnter={show}
          onMouseLeave={hide}
          onFocus={show}
          onBlur={hide}
        >
          {children}
        </span>
      )}
    </>
  );
}
```

> **Fix:** Added `useEffect` cleanup for `timeoutRef`. Without cleanup, if the Tooltip component unmounts while a timeout is pending, the callback will try to update state on an unmounted component, causing a React warning and potential memory leak.

## 4.19 Password Input

```tsx
'use client';
import { useState, useCallback, useId } from 'react';

export interface PasswordInputProps {
  value: string;
  onChange: (value: string) => void;
  label: string;
  error?: string;
  required?: boolean;
  id?: string;
}

function PasswordInput({ value, onChange, label, error, required = false, id }: PasswordInputProps) {
  const [showPassword, setShowPassword] = useState(false);
  const generatedId = useId();
  const inputId = id ?? generatedId;
  const errorId = `${inputId}-error`;
  const strengthId = `${inputId}-strength`;

  const getStrength = useCallback((pwd: string): { label: string; color: string; width: string } => {
    if (pwd.length === 0) return { label: '', color: '', width: '0%' };
    if (pwd.length < 6) return { label: 'Weak', color: 'bg-red-500', width: '25%' };
    if (pwd.length < 10) return { label: 'Fair', color: 'bg-amber-500', width: '50%' };
    if (/[A-Z]/.test(pwd) && /[0-9]/.test(pwd) && /[^A-Za-z0-9]/.test(pwd)) {
      return { label: 'Strong', color: 'bg-green-500', width: '100%' };
    }
    return { label: 'Good', color: 'bg-blue-500', width: '75%' };
  }, []);

  const strength = getStrength(value);

  return (
    <div>
      <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {label}
        {required && <span aria-hidden="true" className="text-red-500 ml-1">*</span>}
      </label>
      <div className="relative">
        <input
          id={inputId}
          type={showPassword ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required={required}
          aria-invalid={!!error}
          aria-describedby={`${error ? errorId : ''} ${value ? strengthId : ''}`.trim() || undefined}
          className="w-full rounded-lg border px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 dark:bg-gray-800 dark:text-gray-100 dark:border-gray-600"
        />
        <button
          type="button"
          onClick={() => setShowPassword(prev => !prev)}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          aria-label={showPassword ? 'Hide password' : 'Show password'}
        >
          {showPassword ? (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          )}
        </button>
      </div>
      {value && (
        <div className="mt-1 flex items-center gap-2" aria-live="polite" id={strengthId}>
          <div className="flex-1 h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all duration-300 ${strength.color}`} style={{ width: strength.width }} />
          </div>
          <span className="text-xs text-gray-500 dark:text-gray-400">{strength.label}</span>
        </div>
      )}
      {error && <p id={errorId} role="alert" className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
}
```

> **Fixes:** (1) Changed `const inputId = id || useId()` to always call useId unconditionally with `id ?? generatedId`. (2) Added `aria-live="polite"` and `id={strengthId}` to the strength indicator container so screen readers announce strength changes. (3) Updated `aria-describedby` to include the strength ID.

## 4.20 Radio Group

```tsx
'use client';
import { useState, useCallback, useId } from 'react';

export interface RadioOption {
  value: string;
  label: string;
  disabled?: boolean;
  description?: string;
}

export interface RadioGroupProps {
  options: RadioOption[];
  value?: string;
  onChange: (value: string) => void;
  label: string;
  error?: string;
}

function RadioGroup({ options, value, onChange, label, error }: RadioGroupProps) {
  const groupId = useId();
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const enabledOptions = options.filter(o => !o.disabled);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    const currentIdx = enabledOptions.findIndex(o => o.value === value);
    let nextIdx = currentIdx;

    switch (e.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        e.preventDefault();
        nextIdx = (currentIdx + 1) % enabledOptions.length;
        break;
      case 'ArrowUp':
      case 'ArrowLeft':
        e.preventDefault();
        nextIdx = (currentIdx - 1 + enabledOptions.length) % enabledOptions.length;
        break;
      default:
        return;
    }

    const next = enabledOptions[nextIdx];
    onChange(next.value);
    setFocusedIndex(nextIdx);
    document.getElementById(`${groupId}-${next.value}`)?.focus();
  }, [enabledOptions, value, onChange, groupId]);

  return (
    <fieldset>
      <legend className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</legend>
      <div
        aria-label={label}
        onKeyDown={handleKeyDown}
        className="mt-2 space-y-2"
      >
        {options.map((option) => {
          const isSelected = value === option.value;
          return (
            <label
              key={option.value}
              className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                isSelected ? 'border-primary bg-primary/5 dark:border-primary dark:bg-primary/10' : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
              } ${option.disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <input
                id={`${groupId}-${option.value}`}
                type="radio"
                name={groupId}
                value={option.value}
                checked={isSelected}
                onChange={() => !option.disabled && onChange(option.value)}
                disabled={option.disabled}
                className="mt-0.5 h-4 w-4 text-primary focus:ring-primary/40 accent-primary"
              />
              <div>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{option.label}</span>
                {option.description && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{option.description}</p>
                )}
              </div>
            </label>
          );
        })}
      </div>
      {error && <p role="alert" className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>}
    </fieldset>
  );
}
```

> **Fix:** Removed redundant `role="radiogroup"` from the inner `<div>`. The `<fieldset>` + `<legend>` already provides the semantic grouping and accessible name for the radio options. Adding `role="radiogroup"` alongside `<fieldset>` creates redundant ARIA that can confuse screen readers.

## 4.21 Data Table

```tsx
'use client';
import { useState, useMemo } from 'react';

export interface Column<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: T[keyof T], row: T) => React.ReactNode;
}

export interface DataTableProps<T extends Record<string, unknown>> {
  data: T[];
  columns: Column<T>[];
  caption?: string;
  onRowClick?: (row: T) => void;
  ref?: React.Ref<HTMLDivElement>;
}

function DataTable<T extends Record<string, unknown>>({
  data, columns, caption, onRowClick, ref
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<keyof T | null>(null);
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

  // Fixed: useMemo instead of useCallback + IIFE
  const sortedData = useMemo(() => {
    if (!sortKey) return data;
    return [...data].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (aVal == null || bVal == null) return 0;
      const cmp = String(aVal).localeCompare(String(bVal), undefined, { numeric: true });
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir]);

  const handleSort = (key: keyof T) => {
    if (sortKey === key) {
      setSortDir(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  return (
    <div ref={ref} className="overflow-x-auto rounded-lg border dark:border-gray-700">
      <table className="w-full text-sm">
        {caption && <caption className="sr-only">{caption}</caption>}
        <thead>
          <tr className="bg-gray-50 dark:bg-gray-800 border-b dark:border-gray-700">
            {columns.map((col) => (
              <th
                key={String(col.key)}
                scope="col"
                className="px-4 py-3 text-left font-medium text-gray-700 dark:text-gray-300"
              >
                {col.sortable ? (
                  <button
                    onClick={() => handleSort(col.key)}
                    className="flex items-center gap-1 hover:text-gray-900 dark:hover:text-white transition-colors"
                    aria-sort={sortKey === col.key ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'}
                  >
                    {col.label}
                    <span aria-hidden="true" className="text-xs">
                      {sortKey === col.key ? (sortDir === 'asc' ? '^' : 'v') : '^v'}
                    </span>
                  </button>
                ) : (
                  col.label
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map((row, i) => (
            <tr
              key={i}
              className={`border-b hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800 transition-colors ${
                onRowClick ? 'cursor-pointer' : ''
              }`}
              onClick={() => onRowClick?.(row)}
              style={{ contentVisibility: 'auto', containIntrinsicSize: 'auto 48px' }}
            >
              {columns.map((col) => (
                <td key={String(col.key)} className="px-4 py-3 dark:text-gray-300">
                  {col.render ? col.render(row[col.key], row) : String(row[col.key] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

> **Fix:** Replaced `useCallback(() => { ... }, deps)()` (useCallback + IIFE) with `useMemo(() => { ... }, deps)`. The previous pattern called a memoized callback on every render, defeating the purpose of memoization. `useMemo` correctly caches the computed sorted data.

## 4.22 Pagination

```tsx
'use client';
import { useCallback } from 'react';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  const getPageNumbers = useCallback(() => {
    const pages: (number | '...')[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (currentPage > 3) pages.push('...');
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);
      for (let i = start; i <= end; i++) pages.push(i);
      if (currentPage < totalPages - 2) pages.push('...');
      pages.push(totalPages);
    }
    return pages;
  }, [currentPage, totalPages]);

  return (
    <nav aria-label="Pagination" className="flex items-center gap-1">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
        className="px-3 py-2 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-800 dark:text-gray-300 transition-colors"
        aria-label="Previous page"
      >
        Previous
      </button>
      {getPageNumbers().map((page, i) =>
        page === '...' ? (
          <span key={`ellipsis-${i}`} className="px-2 text-gray-400 dark:text-gray-600" aria-hidden="true">...</span>
        ) : (
          <button
            key={page}
            onClick={() => onPageChange(page)}
            className={`px-3 py-2 rounded-md text-sm transition-colors ${
              currentPage === page
                ? 'bg-primary text-white font-medium'
                : 'hover:bg-gray-100 text-gray-700 dark:hover:bg-gray-800 dark:text-gray-300'
            }`}
            aria-label={`Page ${page}`}
            aria-current={currentPage === page ? 'page' : undefined}
          >
            {page}
          </button>
        )
      )}
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
        className="px-3 py-2 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-800 dark:text-gray-300 transition-colors"
        aria-label="Next page"
      >
        Next
      </button>
    </nav>
  );
}
```

## 4.23 Additional Component References

| Component | Key Features | Full Implementation |
|-----------|-------------|---------------------|
| Toast/Notification | aria-live, CSS progress animation, stacking, deterministic ID | 4.15 Toast |
| Navigation Bar | skip link, keyboard nav, mobile hamburger | 4.16 Navbar |
| Breadcrumb | aria-label, structured data, current page | 4.17 Breadcrumb |
| Tooltip | anchor positioning, delay show/hide, keyboard trigger, cleanup | 4.18 Tooltip |
| Password Input | visibility toggle, strength indicator, aria-live | 4.19 PasswordInput |
| Radio Group | arrow key nav, aria-checked, descriptions, no redundant ARIA | 4.20 RadioGroup |
| Data Table | sortable, scope/caption, content-visibility, useMemo | 4.21 DataTable |
| Pagination | aria-current, ellipsis, Previous/Next | 4.22 Pagination |
| Dropdown Menu | roving tabindex, type-ahead, Escape to close | 4.11 Select pattern |

---

# MODULE 5: MOTION PRESETS

## 5.1 CSS-First Presets (12)

These use only CSS transitions and animations. No JavaScript required.

### P-01: Fade In
```css
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

### P-02: Slide Up
```css
.animate-slide-up {
  animation: slideUp 0.3s ease-out;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### P-03: Scale In
```css
.animate-scale-in {
  animation: scaleIn 0.2s ease-out;
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```

### P-04: Slide Down (Dropdown)
```css
.animate-slide-down {
  animation: slideDown 0.2s ease-out;
  transform-origin: top;
}
@keyframes slideDown {
  from { opacity: 0; transform: scaleY(0.9) translateY(-4px); }
  to { opacity: 1; transform: scaleY(1) translateY(0); }
}
```

### P-05: Hover Lift
```css
.hover-lift {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}
@media (prefers-reduced-motion: reduce) {
  .hover-lift:hover { transform: none; }
}
```

### P-06: Focus Ring
```css
.focus-ring:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px oklch(0.55 0.20 260 / 0.4);
  border-radius: var(--radius-sm);
}
```

### P-07: Skeleton Shimmer
```css
.skeleton-shimmer {
  background: linear-gradient(90deg, #e5e7eb 25%, #f3f4f6 50%, #e5e7eb 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### P-08: Spinner
```css
.spinner {
  width: 24px; height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: oklch(0.55 0.20 260);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### P-09: Toast Slide In
```css
.animate-toast-in {
  animation: toastIn 0.3s ease-out;
}
@keyframes toastIn {
  from { opacity: 0; transform: translateX(100%); }
  to { opacity: 1; transform: translateX(0); }
}
```

### P-10: Toast Slide Out
```css
.animate-toast-out {
  animation: toastOut 0.2s ease-in forwards;
}
@keyframes toastOut {
  from { opacity: 1; transform: translateX(0); }
  to { opacity: 0; transform: translateX(100%); }
}
```

### P-11: Accordion Expand
```css
/* Uses CSS grid trick for height animation */
.accordion-content {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.3s ease-out;
}
.accordion-content.open {
  grid-template-rows: 1fr;
}
.accordion-content > div {
  overflow: hidden;
}
```

### P-12: Page Transition (View Transitions)
```css
/* See Part A Module 3.7 for full View Transitions API usage */
::view-transition-old(root) {
  animation: fadeOut 0.15s ease-out;
}
::view-transition-new(root) {
  animation: fadeIn 0.15s ease-in;
}
```

## 5.2 GSAP-Enhanced Presets (12)

These use GSAP for complex timeline animations. All presets are wrapped in the `useGSAP` hook pattern for automatic cleanup. Requires gsap and @gsap/react packages.

### G-01: Hero Sequence
```tsx
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';

function useHeroSequence(containerRef: React.RefObject<HTMLElement>) {
  useGSAP(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    const heroTl = gsap.timeline();
    heroTl.from('.hero-badge', { opacity: 0, y: -20, duration: 0.4 })
      .from('.hero-title', { opacity: 0, y: 40, duration: 0.6 }, '-=0.2')
      .from('.hero-subtitle', { opacity: 0, y: 20, duration: 0.4 }, '-=0.3')
      .from('.hero-cta', { opacity: 0, scale: 0.9, duration: 0.3, ease: 'back.out(1.5)' }, '-=0.1');
  }, { scope: containerRef });
}
```

### G-02: Scroll-Triggered Fade
```tsx
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

function useScrollFade(containerRef: React.RefObject<HTMLElement>) {
  useGSAP(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    gsap.utils.toArray('.fade-section').forEach((section) => {
      gsap.from(section, {
        opacity: 0,
        y: 50,
        duration: 0.8,
        scrollTrigger: {
          trigger: section as Element,
          start: 'top 85%',
          toggleActions: 'play none none reverse',
        },
      });
    });
  }, { scope: containerRef });
}
```

### G-03: Stagger Cards
```tsx
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

function useStaggerCards(containerRef: React.RefObject<HTMLElement>) {
  useGSAP(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    gsap.from('.card', {
      opacity: 0,
      y: 30,
      stagger: 0.1,
      duration: 0.5,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: '.card-grid',
        start: 'top 80%',
      },
    });
  }, { scope: containerRef });
}
```

### G-04: Magnetic Button
```tsx
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';

function useMagneticButton(ref: React.RefObject<HTMLElement>, strength = 0.3) {
  useGSAP(() => {
    const el = ref.current;
    if (!el) return;
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      gsap.to(el, { x: x * strength, y: y * strength, duration: 0.3, ease: 'power2.out' });
    };

    const handleMouseLeave = () => {
      gsap.to(el, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.3)' });
    };

    el.addEventListener('mousemove', handleMouseMove);
    el.addEventListener('mouseleave', handleMouseLeave);
    return () => {
      el.removeEventListener('mousemove', handleMouseMove);
      el.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, { scope: ref });
}
```

### G-05: Text Scramble
```tsx
import { useGSAP } from '@gsap/react';

function useTextScramble(
  elementRef: React.RefObject<HTMLElement>,
  finalText: string,
  duration = 1
) {
  useGSAP(() => {
    const el = elementRef.current;
    if (!el) return;
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      el.textContent = finalText;
      return;
    }

    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const length = finalText.length;
    let frame = 0;
    const totalFrames = Math.round(duration * 60);

    // Deterministic pseudo-random: replaces Math.random()
    const pseudoRandom = (index: number) => ((index * 9301 + 49297) % 233280) / 233280;

    const animate = () => {
      const progress = frame / totalFrames;
      const currentText = finalText
        .split('')
        .map((char, i) => {
          if (char === ' ') return ' ';
          if (i / length < progress) return finalText[i];
          // Deterministic character selection based on frame and position
          const charIndex = Math.floor(pseudoRandom(frame * length + i) * chars.length);
          return chars[charIndex];
        })
        .join('');
      el.textContent = currentText;
      frame++;
      if (frame <= totalFrames) requestAnimationFrame(animate);
      else el.textContent = finalText;
    };
    animate();
  }, { scope: elementRef, dependencies: [finalText, duration] });
}
```

> **Fix:** Replaced `Math.random()` with deterministic pseudo-random function `pseudoRandom(index)` using the same formula as the anti-pattern fix. This ensures consistent output across SSR and client renders.

### G-06: SplitText Reveal
```tsx
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

function useSplitTextReveal(selector: string, containerRef: React.RefObject<HTMLElement>, options = {}) {
  useGSAP(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    const elements = gsap.utils.toArray(selector);
    elements.forEach((el) => {
      const text = (el as HTMLElement).textContent || '';
      (el as HTMLElement).innerHTML = text
        .split('')
        .map((char) =>
          char === ' '
            ? ' '
            : `<span style="display:inline-block;opacity:0;transform:translateY(20px)">${char}</span>`
        )
        .join('');

      gsap.to((el as HTMLElement).querySelectorAll('span'), {
        opacity: 1,
        y: 0,
        stagger: 0.02,
        duration: 0.4,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: el as Element,
          start: 'top 85%',
          once: true,
        },
        ...options,
      });
    });
  }, { scope: containerRef });
}
```

### G-07: DrawSVG Stroke
```tsx
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { DrawSVGPlugin } from 'gsap/DrawSVGPlugin';
gsap.registerPlugin(DrawSVGPlugin);

function useDrawSVG(containerRef: React.RefObject<HTMLElement>) {
  useGSAP(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    gsap.from('.svg-path', {
      drawSVG: '0%',
      duration: 1.5,
      stagger: 0.2,
      ease: 'power2.inOut',
      scrollTrigger: {
        trigger: '.svg-container',
        start: 'top 80%',
        once: true,
      },
    });
  }, { scope: containerRef });
}
```

### G-08: MorphSVG Shape Transition
```tsx
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { MorphSVGPlugin } from 'gsap/MorphSVGPlugin';
gsap.registerPlugin(MorphSVGPlugin);

function useMorphSVG(containerRef: React.RefObject<HTMLElement>) {
  useGSAP(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    gsap.to('#circle', {
      morphSVG: '#square',
      duration: 0.8,
      ease: 'power2.inOut',
    });
  }, { scope: containerRef });
}
```

### G-09: MotionPath
```tsx
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { MotionPathPlugin } from 'gsap/MotionPathPlugin';
gsap.registerPlugin(MotionPathPlugin);

function useMotionPath(containerRef: React.RefObject<HTMLElement>) {
  useGSAP(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    gsap.to('.moving-element', {
      motionPath: {
        path: '#motion-path',
        align: '#motion-path',
        alignOrigin: [0.5, 0.5],
        autoRotate: true,
      },
      duration: 3,
      ease: 'power1.inOut',
      repeat: -1,
    });
  }, { scope: containerRef });
}
```

### G-10: Flip Layout Animation
```tsx
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { Flip } from 'gsap/Flip';
gsap.registerPlugin(Flip);

function useFlipLayout(containerRef: React.RefObject<HTMLElement>) {
  useGSAP(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;
    // Flip is triggered by DOM changes, call manually:
    // const state = Flip.getState('.flip-item', containerRef.current);
    // rearrangeItems();
    // Flip.from(state, { duration: 0.4, ease: 'power2.inOut', stagger: 0.02, absolute: true });
  }, { scope: containerRef });
}
```

### G-11: Lenis Smooth Scroll Integration
```tsx
import { useGSAP } from '@gsap/react';
import Lenis from 'lenis';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

function useLenisScroll() {
  useGSAP(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: 'vertical',
      smoothWheel: true,
    });

    lenis.on('scroll', ScrollTrigger.update);

    const rafCallback = (time: number) => {
      lenis.raf(time * 1000);
    };
    gsap.ticker.add(rafCallback);
    gsap.ticker.lagSmoothing(0);

    // Cleanup on unmount
    return () => {
      lenis.destroy();
      gsap.ticker.remove(rafCallback);
    };
  });
}
```

### G-12: Scroll-Triggered Parallax
```tsx
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

function useParallax(containerRef: React.RefObject<HTMLElement>) {
  useGSAP(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    gsap.utils.toArray('[data-speed]').forEach((el) => {
      const speed = parseFloat((el as HTMLElement).dataset.speed || '0.5');
      gsap.to(el, {
        yPercent: -100 * speed,
        ease: 'none',
        scrollTrigger: {
          trigger: el as Element,
          start: 'top bottom',
          end: 'bottom top',
          scrub: true,
        },
      });
    });
  }, { scope: containerRef });
}
```

## 5.3 Reduced Motion Handling

All motion presets must respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

```javascript
// JavaScript check — use in every GSAP animation
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (prefersReduced) {
  // Skip animation, show final state immediately
  return;
}
```

---

# MODULE 6: VALIDATION & AUDIT

## 6.1 Pre-Delivery Checklist

Before delivering ANY UI code, verify every item:

### Visual Quality
- [ ] No emojis used as icons (use SVG: Lucide, Heroicons, Simple Icons)
- [ ] All icons from consistent icon set
- [ ] Brand logos verified from official sources
- [ ] Hover states do not cause layout shift
- [ ] Images have explicit width/height (prevent CLS)
- [ ] Images optimized with framework-appropriate image component (next/image in Next.js, NuxtImage in Nuxt, native loading="lazy" otherwise)

### Interaction
- [ ] cursor-pointer on all clickable/hoverable elements
- [ ] Hover states provide clear visual feedback (color/shadow/border change)
- [ ] Transitions are smooth (150-300ms for UI feedback)
- [ ] Focus states visible with :focus-visible ring (3px offset, brand color)
- [ ] Active/pressed states distinct from hover
- [ ] Disabled states clearly communicated (opacity + cursor-not-allowed)

### Color & Contrast
- [ ] Body text contrast >= 4.5:1 (WCAG AA)
- [ ] Large text (18px+) contrast >= 3:1
- [ ] UI component contrast >= 3:1 against adjacent colors
- [ ] OKLCH tokens provided with hex fallbacks
- [ ] Color is not the only indicator (add icon/pattern/text)
- [ ] Light and dark mode both tested

### Layout
- [ ] Floating elements have proper spacing from edges
- [ ] No content hidden behind fixed navbars
- [ ] Responsive at: 375px, 640px, 768px, 1024px, 1280px, 1536px
- [ ] No horizontal scroll on mobile
- [ ] Content-first breakpoints (break when content strains, not at device widths)
- [ ] Body text max-width: 65-75ch

### Accessibility
- [ ] Skip link as first focusable element
- [ ] All images have descriptive alt text
- [ ] All form inputs have associated labels
- [ ] Color is not the only indicator of state
- [ ] prefers-reduced-motion respected (all animations)
- [ ] Keyboard navigation: Tab, Arrow keys, Home/End, Escape
- [ ] Focus trap in modals/dialogs
- [ ] ARIA roles and labels on interactive components
- [ ] Screen reader announcements for dynamic content (aria-live)
- [ ] Touch targets >= 44x44px on mobile

### Performance
- [ ] No Math.random() in SSR/hydration paths
- [ ] Barrel imports replaced with direct imports
- [ ] content-visibility: auto on long lists
- [ ] Images optimized (WebP, lazy loading, priority for above-fold)
- [ ] CSS organized in @layer base, components, utilities
- [ ] No layout-shifting animations (only transform/opacity)
- [ ] will-change added dynamically, removed after animation

### Security
- [ ] Content-Security-Policy headers configured
- [ ] Images optimized with framework-appropriate component or native lazy loading
- [ ] SEO metadata set via framework SEO API (Next.js Metadata API, Nuxt useHead, Astro head, Svelte svelte:head)
- [ ] Server Actions / API routes validated
- [ ] No sensitive data in client components

## 6.2 Anti-Pattern Confidence Checklist

Before shipping, verify you have NOT done any of these:

| # | Anti-Pattern | Why It's Wrong | Confidence Level |
|---|-------------|----------------|------------------|
| 1 | AI purple/pink gradients for non-AI products | Misleading brand association | BLOCK |
| 2 | Dark mode default for non-dev tools | Harms readability for general audience | HIGH |
| 3 | Neon/bright colors for healthcare/finance | Undermines trust | HIGH |
| 4 | Brutalism for B2B enterprise | Wrong tone for audience | MEDIUM |
| 5 | Complex animations for form-heavy apps | Distracts from task completion | MEDIUM |
| 6 | Full-screen video background on mobile | Performance + data cost | MEDIUM |
| 7 | Glassmorphism without fallback | Illegible on low-end devices | HIGH |
| 8 | Emoji as UI icons | Inconsistent rendering, accessibility fail | BLOCK |
| 9 | Hover-only navigation | Touch devices cannot access | HIGH |
| 10 | Auto-playing media | Accessibility violation, annoying | BLOCK |

## 6.3 Performance Audit

Run these checks using browser DevTools:

```
1. Lighthouse Score
   - Performance: > 90
   - Accessibility: > 90
   - Best Practices: > 90
   - SEO: > 90

2. Core Web Vitals
   - LCP: < 2.5s
   - INP: < 200ms (Interaction to Next Paint — replaces FID)
   - CLS: < 0.1

3. Bundle Size
   - First Load JS: < 100KB (Next.js)
   - Total CSS: < 50KB
   - No duplicate dependencies

4. Animation Performance
   - 60fps on desktop
   - 30fps minimum on mid-range Android
   - No layout thrashing during animations
```

> **Fix:** Replaced FID (First Input Delay) with INP (Interaction to Next Paint). FID was deprecated as a Core Web Vital in March 2024 and replaced by INP, which measures the latency of ALL interactions throughout the page lifecycle, not just the first one.

## 6.4 Accessibility Audit (WCAG 2.2)

```
Perceivable:
- [ ] 1.1.1 Non-text Content — All images have text alternatives
- [ ] 1.2.1 Audio-only/Video-only — Equivalent alternatives provided
- [ ] 1.2.2 Captions — Captions for audio/video content
- [ ] 1.3.1 Info and Relationships — Content adaptable to different presentations
- [ ] 1.3.2 Meaningful Sequence — Reading order is logical
- [ ] 1.3.5 Identify Input Purpose — Autocomplete attributes on form fields
- [ ] 1.4.1 Use of Color — Color is not the only visual indicator
- [ ] 1.4.3 Contrast (Minimum) — AA contrast ratios met
- [ ] 1.4.4 Resize Text — Text resizable to 200% without loss
- [ ] 1.4.10 Reflow — No horizontal scroll at 320px width
- [ ] 1.4.11 Non-text Contrast — UI components >= 3:1
- [ ] 1.4.12 Text Spacing — No loss of content when text spacing adjusted
- [ ] 1.4.13 Content on Hover/Focus — Dismissible, hoverable, persistent

Operable:
- [ ] 2.1.1 Keyboard — All functionality available from keyboard
- [ ] 2.1.2 No Keyboard Trap — Focus can move away from all components
- [ ] 2.2.1 Timing Adjustable — Enough time to read/use content
- [ ] 2.3.1 Three Flashes — No content that causes seizures (> 3/sec)
- [ ] 2.4.1 Bypass Blocks — Skip links provided
- [ ] 2.4.2 Page Titled — Descriptive page titles
- [ ] 2.4.3 Focus Order — Logical focus order
- [ ] 2.4.6 Headings and Labels — Descriptive headings
- [ ] 2.4.7 Focus Visible — Visible focus indicators
- [ ] 2.4.11 Focus Not Obscured (2.2) — Focus not hidden by other content
- [ ] 2.4.12 Focus Not Obscured (Minimum) (2.2) — Focus partially unobscured
- [ ] 2.4.13 Focus Appearance (2.2) — Focus indicator meets size requirements
- [ ] 2.5.1 Pointer Gestures — All multi-point gestures have single-pointer alternative
- [ ] 2.5.7 Dragging Movements (2.2) — Single-pointer alternative for drag actions
- [ ] 2.5.8 Target Size (Minimum) (2.2) — Touch targets >= 24x24px

Understandable:
- [ ] 3.1.1 Language of Page — Page language declared
- [ ] 3.2.1 On Focus — No context change on focus
- [ ] 3.2.2 On Input — No context change on input without warning
- [ ] 3.2.6 Consistent Help (2.2) — Help mechanism in consistent location
- [ ] 3.3.1 Error Identification — Errors clearly identified
- [ ] 3.3.2 Labels — All inputs have labels
- [ ] 3.3.3 Error Suggestion — Suggestions provided for errors
- [ ] 3.3.7 Redundant Entry (2.2) — Previously entered info auto-populated
- [ ] 3.3.8 Accessible Authentication (Minimum) (2.2) — No cognitive function tests for auth

Robust:
- [ ] 4.1.2 Name, Role, Value — All UI components have accessible names
- [ ] 4.1.3 Status Messages — Status messages communicated to assistive technologies
```

> **Fix:** Added 9 missing WCAG 2.2 criteria: 1.3.5 (Identify Input Purpose), 1.4.10 (Reflow), 1.4.11 (Non-text Contrast), 1.4.12 (Text Spacing), 1.4.13 (Content on Hover/Focus), 2.4.11 (Focus Not Obscured), 2.5.7 (Dragging Movements), 2.5.8 (Target Size Minimum), 3.2.6 (Consistent Help), 3.3.7 (Redundant Entry), 3.3.8 (Accessible Authentication Minimum).

---

# MODULE 8: CROSS-REFERENCE INTEGRATION

## 8.1 Design System Operating System

The five UI/UX skills form a composable "operating system" for design and implementation. Each skill is a module with a specific domain:

```
┌──────────────────────────────────────────────────────────┐
│                DESIGN SYSTEM OPERATING SYSTEM              │
│                                                            │
│  ┌──────────────────┐  ┌──────────────────────────────┐  │
│  │  UI/UX Pro Max   │  │  GSAP Animations              │  │
│  │  (THIS SKILL)    │  │  - Timeline choreography      │  │
│  │  - Design tokens │◄─┤  - ScrollTrigger              │  │
│  │  - Palettes      │  │  - SplitText, Flip, MorphSVG  │  │
│  │  - Typography    │  │  - MotionPath, DrawSVG        │  │
│  │  - Components    │  │  - useGSAP hook               │  │
│  │  - Industry rules│  │  - Lenis smooth scroll        │  │
│  └────────┬─────────┘  └──────────────────────────────┘  │
│           │                                                │
│  ┌────────┴─────────┐  ┌──────────────────────────────┐  │
│  │  Web Design       │  │  React Best Practices         │  │
│  │  Guidelines       │  │  - Waterfall elimination      │  │
│  │  - ARIA/focus     │◄─┤  - Bundle optimization        │  │
│  │  - Semantic HTML  │  │  - Server Components          │  │
│  │  - Forms/a11y     │  │  - Re-render optimization     │  │
│  │  - Keyboard nav   │  │  - Suspense boundaries        │  │
│  └───────────────────┘  └──────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Motion System Playbook (Cross-cutting governance)    │ │
│  │  - Library selection matrix                           │ │
│  │  - Performance budgets (60fps)                        │ │
│  │  - Combo safety (multi-library coexistence)           │ │
│  │  - Reduced motion enforcement                         │ │
│  │  - Core Web Vitals protection                         │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## 8.2 Cross-Reference Table: What Each Skill Provides

| Need | UI/UX Pro Max | GSAP Animations | React Best Practices | Web Design Guidelines | Motion System Playbook |
|------|---------------|-----------------|---------------------|----------------------|----------------------|
| Color palette | 48 OKLCH palettes | — | — | — | — |
| Font pairing | 36 verified pairings | — | — | — | — |
| Industry rules | 21 reasoning rules | — | — | — | — |
| Component code | 20+ React components | — | — | — | — |
| CSS primitives | Container queries, @layer, nesting | — | — | Semantic HTML, forms | — |
| Animation syntax | 24 presets (CSS + GSAP) | Full GSAP API reference | — | — | Library selection matrix |
| Scroll animations | Basic ScrollTrigger | Advanced ScrollTrigger, pin, scrub | — | — | Max 15-20 instances/page |
| Text animation | SplitText, scramble | Full SplitText, typewriter | — | — | Duration ceilings |
| SVG animation | DrawSVG, MorphSVG | Full DrawSVG/MorphSVG API | — | — | — |
| Layout animation | Flip basics | Full Flip API | — | — | Never mix libraries on same element |
| React perf | Basic memo/keys | — | 70 rules, 8 categories | — | Core Web Vitals audit |
| Bundle size | Barrel import warning | — | 6 bundle rules | — | Bundle size per library |
| Accessibility | WCAG 2.2 checklist, keyboard nav | — | — | Full ARIA, focus, keyboard | Reduced motion, motion toggle |
| AI UI patterns | 8 AI-specific components | — | — | — | — |
| View Transitions | API + Next.js integration | — | — | — | Duration guidance |
| Smooth scroll | Lenis integration | — | — | — | Performance rules |

## 8.3 Integration Workflows

### Workflow A: Full Marketing Site (Animation-Heavy)

```
1. UI/UX Pro Max Module 1 → Creative brief, style selection
2. UI/UX Pro Max Module 2 → Design tokens, OKLCH palettes
3. UI/UX Pro Max Module 7 → Font pairing, industry rules
4. GSAP Animations → Timeline choreography, ScrollTrigger setup
5. Motion System Playbook → Library selection (GSAP for scroll, CSS for hovers)
6. React Best Practices → Server Components for static sections, client for interactive
7. Web Design Guidelines → ARIA, keyboard nav audit
8. UI/UX Pro Max Module 6 → Pre-delivery validation
```

### Workflow B: AI Chat Product

```
1. UI/UX Pro Max Module 1 → Creative brief (AI platform)
2. UI/UX Pro Max Module 7 → AI-Native UI style, purple/blue palette
3. UI/UX Pro Max Module 4 → Thinking indicator, Chat composer, Uncertainty notice
4. React Best Practices → Streaming with Suspense, SWR for message dedup
5. Web Design Guidelines → aria-live for message announcements
6. Motion System Playbook → Typing animation (CSS or Motion One, not GSAP for this)
7. UI/UX Pro Max Module 6 → Accessibility audit (screen reader flow)
```

### Workflow C: Enterprise Dashboard

```
1. UI/UX Pro Max Module 1 → Creative brief (fintech/enterprise)
2. UI/UX Pro Max Module 7 → Data-Dense Dashboard style, banking palette
3. UI/UX Pro Max Module 3 → Container queries for responsive panels
4. React Best Practices → RSC for data fetching, memo for chart components
5. Web Design Guidelines → Form accessibility, ARIA for data tables
6. Motion System Playbook → CSS-only micro-interactions (no GSAP needed)
7. UI/UX Pro Max Module 6 → Performance audit (Core Web Vitals)
```

### Workflow D: Design System Migration (v3 → v4)

```
1. UI/UX Pro Max Module 2 → Audit existing tokens, plan OKLCH migration
2. UI/UX Pro Max Module 3 → Migrate CSS: nesting, @layer, @scope, @property
3. UI/UX Pro Max Module 9 → Theme system: add dark mode, color-scheme, unified elevation
4. React Best Practices → RSC adoption plan, bundle optimization
5. UI/UX Pro Max Module 4 → Component library: add dark: variants, ref props, type exports
6. UI/UX Pro Max Module 6 → Validation: run both WCAG 2.x and APCA contrast checks
```

### Workflow E: Accessibility Remediation Sprint

```
1. Web Design Guidelines → Full ARIA audit, keyboard nav assessment
2. UI/UX Pro Max Module 6 → WCAG 2.2 checklist (all 30+ criteria)
3. UI/UX Pro Max Module 4 → Fix component a11y: conditional hooks, contradictory ARIA, focus management
4. UI/UX Pro Max Module 2 → Contrast validation (both light and dark themes)
5. Motion System Playbook → Reduced motion audit, motion toggle implementation
6. UI/UX Pro Max Module 6 → Re-audit, verify INP < 200ms
```

## 8.4 Skill Activation Priority

When multiple skills could apply, use this priority order:

| Priority | Skill | Condition |
|----------|-------|-----------|
| 1 | UI/UX Pro Max | Always activate first for any UI/UX request (it routes to others) |
| 2 | React Best Practices | When writing React/Next.js component code |
| 3 | GSAP Animations | When implementing GSAP-specific animations |
| 4 | Web Design Guidelines | When auditing accessibility or semantic HTML |
| 5 | Motion System Playbook | When mixing animation libraries or debugging perf |

## 8.5 Conflict Resolution

When two skills give conflicting advice, resolve using this hierarchy:

| Conflict | Resolution |
|----------|------------|
| React 19 ref vs. forwardRef | Use React 19 ref prop directly (no forwardRef) |
| GSAP timeline vs. CSS animation | Use CSS for simple transitions, GSAP for complex sequences |
| WCAG 2.x ratio vs. APCA Lc | Pass BOTH thresholds during transition period |
| @layer utilities vs. !important in transitions | @layer wins for architecture; theme-transition !important is an explicit exception |
| Motion toggle vs. reduced-motion media query | Both must be respected — media query for users, toggle for manual control |

## 8.6 Bundled Assets Reference

This skill bundles data accessible via Python scripts:

```bash
# Design system generation
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system -p "Project Name"

# Domain-specific searches
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain>

# Stack-specific guidelines
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack <stack>

# Persistence
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project"
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project" --page "dashboard"
```

Available domains: product, style, color, landing, typography, chart, ux, icons, react, web

Available stacks: html-tailwind, react, nextjs, vue, nuxtjs, nuxt-ui, svelte, astro, swiftui, react-native, flutter, shadcn, jetpack-compose

Data files location: `skills/ui-ux-pro-max/data/`
- styles.csv (67 entries), colors.csv (96 palettes), typography.csv (57 pairings)
- products.csv, landing.csv, charts.csv, icons.csv
- ux-guidelines.csv, react-performance.csv, web-interface.csv
- ui-reasoning.csv (100 reasoning rules)
- stacks/*.csv (13 stack-specific guideline files)

---

# MODULE 10: ADVANCED PATTERNS

## 10.1 Error Boundary Component

Error boundaries catch rendering errors anywhere in their child component tree, display a fallback UI, and prevent the entire app from crashing. The `resetKey` prop allows parent components to trigger a reset by changing the key value.

```tsx
'use client';

import { Component, type ReactNode } from 'react';

export interface ErrorBoundaryProps {
  fallback?: ReactNode;
  children: ReactNode;
  resetKey?: string | number;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    // Reset error state when resetKey changes
    if (this.props.resetKey !== prevProps.resetKey && this.state.hasError) {
      this.setState({ hasError: false, error: null });
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
    // Send to error reporting service (Sentry, etc.)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div
          role="alert"
          className="flex flex-col items-center justify-center p-8 rounded-xl border border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20 text-center"
        >
          <svg className="w-12 h-12 text-red-400 dark:text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
          </svg>
          <h3 className="text-lg font-semibold text-red-800 dark:text-red-300 mb-2">Something went wrong</h3>
          <p className="text-sm text-red-600 dark:text-red-400 mb-4 max-w-md">
            This section encountered an error and could not be displayed. The rest of the page should work normally.
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="px-4 py-2 rounded-lg bg-red-100 text-red-800 hover:bg-red-200 dark:bg-red-900/40 dark:text-red-300 dark:hover:bg-red-900/60 transition-colors text-sm font-medium focus:outline-none focus:ring-2 focus:ring-red-400"
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage:
// <ErrorBoundary resetKey={someKey}>
//   <DataDependentComponent />
// </ErrorBoundary>
//
// With custom fallback:
// <ErrorBoundary fallback={<p>Failed to load content</p>} resetKey={version}>
//   <ChartComponent />
// </ErrorBoundary>
```

> **Fix:** Added `resetKey` prop that resets error state when the key value changes. This allows parent components to trigger a retry by updating the key, which is more idiomatic React than calling `setState` from outside the component.

## 10.2 Loading, Empty, and Error State Patterns

Every data-dependent component must handle three states beyond the happy path. These states are not edge cases — they are the first thing users see when network conditions are slow or data is unavailable.

### DataState Wrapper

```tsx
export interface DataStateProps<T> {
  data: T[] | null | undefined;
  isLoading: boolean;
  error: Error | null;
  children: (data: T[]) => React.ReactNode;
  emptyMessage?: string;
  onRetry?: () => void;
}

function DataState<T>({
  data, isLoading, error, children, emptyMessage = 'No data available', onRetry
}: DataStateProps<T>) {
  if (isLoading) {
    return (
      <div className="space-y-3 p-4" aria-busy="true" aria-label="Loading content">
        <Skeleton height="2rem" index={0} />
        <Skeleton height="1rem" width="80%" index={1} />
        <Skeleton height="1rem" width="60%" index={2} />
      </div>
    );
  }

  if (error) {
    return (
      <div role="alert" className="flex flex-col items-center p-8 text-center rounded-xl border border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
        <p className="text-red-700 dark:text-red-400 text-sm mb-3">{error.message || 'Failed to load data'}</p>
        <button
          onClick={onRetry}
          className="px-3 py-1.5 text-sm rounded-lg bg-red-100 text-red-800 hover:bg-red-200 dark:bg-red-900/40 dark:text-red-300 dark:hover:bg-red-900/60 transition-colors focus:outline-none focus:ring-2 focus:ring-red-400"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center p-8 text-center" aria-live="polite">
        <svg className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <p className="text-gray-500 dark:text-gray-400 text-sm">{emptyMessage}</p>
      </div>
    );
  }

  return <>{children(data)}</>;
}

// Usage:
// <DataState data={users} isLoading={isLoading} error={error} onRetry={refetch} emptyMessage="No users found">
//   {(users) => users.map(user => <UserCard key={user.id} user={user} />)}
// </DataState>
```

> **Fix:** Replaced `window.location.reload()` with an `onRetry` callback prop. Forcing a full page reload is a poor UX pattern — the parent component should control retry behavior (e.g., re-fetching data, resetting state) without losing client-side state.

## 10.3 Loading State Decision Tree

Choosing the wrong loading indicator creates a disjointed user experience. Use this decision tree to pick the right loading pattern for every situation.

### Decision Tree

```
What type of operation is this?
|
+-- Data loading (fetching content)
|   |
|   +-- Is the layout known in advance?
|   |   |
|   |   +-- YES --> Use Skeleton
|   |   |   Match the exact shape of the expected content.
|   |   |   Example: Article page, product card grid, profile page.
|   |   |
|   |   +-- NO --> Use Spinner
|   |       Show a centered spinner with a descriptive label.
|   |       Example: Search results, dynamic filters, AI-generated content.
|   |
|   +-- Is the load time likely > 3s?
|       |
|       +-- YES --> Use Skeleton + Progress Indicator
|       |   Combine skeleton placeholders with a progress bar for
|       |   long-running operations (file uploads, data exports).
|       |
|       +-- NO --> Skeleton alone is sufficient.
|
+-- User action (mutation)
|   |
|   +-- Is the outcome predictable?
|   |   |
|   |   +-- YES --> Use Optimistic UI
|   |   |   Immediately show the expected result, rollback on error.
|   |   |   Example: Like/unlike, toggle switch, checkbox, add to cart.
|   |   |
|   |   +-- NO --> Use Inline Spinner + Disable Button
|   |       Show a small spinner inside the button, disable interactions.
|   |       Example: Form submission, payment processing, file upload.
|   |
|   +-- Does the action change the page location?
|       |
|       +-- YES --> Use Skeleton for next page (view transition)
|       |
|       +-- NO --> Use inline feedback (spinner in button or toast)
|
+-- Error state
    |
    +-- Is retry likely to succeed?
    |   |
    |   +-- YES --> Show Error State with Retry button
    |   |   Include clear error message, retry button, and dismiss option.
    |   |
    |   +-- NO --> Show Error State with alternative actions
        Provide next steps, support contact, or fallback content.
```

### Implementation Examples

```tsx
// Optimistic UI with useOptimistic (React 19)
import { useOptimistic, useState } from 'react';

function LikeButton({ initialLiked, initialCount, onToggle }: {
  initialLiked: boolean;
  initialCount: number;
  onToggle: () => Promise<void>;
}) {
  const [isLiked, setIsLiked] = useState(initialLiked);
  const [count, setCount] = useState(initialCount);
  const [optimisticState, addOptimistic] = useOptimistic(
    { liked: isLiked, count },
    (state, newLiked: boolean) => ({
      liked: newLiked,
      count: newLiked ? state.count + 1 : state.count - 1,
    })
  );

  const handleToggle = async () => {
    const newLiked = !isLiked;
    addOptimistic(newLiked);
    try {
      await onToggle();
      setIsLiked(newLiked);
      setCount(prev => newLiked ? prev + 1 : prev - 1);
    } catch {
      // Optimistic state automatically reverts on error
    }
  };

  return (
    <button
      onClick={handleToggle}
      aria-pressed={optimisticState.liked}
      className="flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors"
    >
      <svg className={`w-5 h-5 ${optimisticState.liked ? 'text-red-500 fill-current' : 'text-gray-400'}`} viewBox="0 0 20 20" aria-hidden="true">
        <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
      </svg>
      <span className="text-sm">{optimisticState.count}</span>
    </button>
  );
}

// Error State with Retry
function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex flex-col items-center p-8 text-center rounded-xl border border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
      <svg className="w-10 h-10 text-red-400 dark:text-red-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
      </svg>
      <p className="text-red-700 dark:text-red-400 text-sm mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 text-sm rounded-lg bg-red-100 text-red-800 hover:bg-red-200 dark:bg-red-900/40 dark:text-red-300 dark:hover:bg-red-900/60 transition-colors focus:outline-none focus:ring-2 focus:ring-red-400"
        >
          Try again
        </button>
      )}
    </div>
  );
}
```

## 10.4 Container Query Component Patterns

Container queries enable components to adapt to their own layout context rather than the viewport. See Part A Module 3.1 for CSS container query syntax and Tailwind v4 integration.

### Responsive Card Grid

```css
.product-grid {
  container-type: inline-size;
  container-name: products;
}

@container products (min-width: 900px) {
  .product-grid-inner {
    grid-template-columns: repeat(3, 1fr);
  }
}

@container products (min-width: 500px) and (max-width: 899px) {
  .product-grid-inner {
    grid-template-columns: repeat(2, 1fr);
  }
}

@container products (max-width: 499px) {
  .product-grid-inner {
    grid-template-columns: 1fr;
  }
}
```

### Responsive Sidebar Layout

```css
.dashboard {
  container-type: inline-size;
  container-name: dashboard;
}

@container dashboard (min-width: 768px) {
  .dashboard-layout {
    display: grid;
    grid-template-columns: 240px 1fr;
  }
}

@container dashboard (max-width: 767px) {
  .dashboard-layout {
    display: grid;
    grid-template-columns: 1fr;
  }
  .sidebar {
    position: fixed;
    inset: 0;
    z-index: var(--z-modal);
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  .sidebar.open {
    transform: translateX(0);
  }
}
```

## 10.5 CSS Nesting Best Practices

See Part A Module 3.6 for the full CSS nesting best practices guide. Summary:

1. **Nest no deeper than 3 levels**
2. **Always use `&` for pseudo-classes and pseudo-elements**
3. **Nest `@media` and `@container` inside components** — but be aware of source-order override concerns
4. **Use `@scope` when you need hard boundaries**
5. **Avoid nesting for universal selectors**

## 10.6 IntersectionObserver with Strict Mode Safety

React Strict Mode in development double-invokes effects, which can cause IntersectionObserver to register twice. Use a ref-stored observer to prevent double registration and ensure clean disconnect.

> **Fix:** The `useScrollAnimation` hook now accepts individual threshold and rootMargin parameters instead of an `options` object, because spreading an options object into the IntersectionObserver constructor can cause subtle bugs when dependencies change.

```tsx
'use client';

import { useEffect, useRef, useState } from 'react';

export interface UseScrollAnimationReturn {
  isVisible: boolean;
  elementRef: React.RefCallback<HTMLElement>;
}

function useScrollAnimation(
  threshold = 0.1,
  rootMargin = '0px'
): UseScrollAnimationReturn {
  const [isVisible, setIsVisible] = useState(false);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const elementRef = useRef<HTMLElement | null>(null);

  const refCallback = useRef((node: HTMLElement | null) => {
    // Disconnect existing observer (handles Strict Mode double-mount)
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    elementRef.current = node;
    if (!node) return;

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      setIsVisible(true);
      return;
    }

    observerRef.current = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          // Once visible, stop observing (one-time trigger)
          observerRef.current?.unobserve(node);
        }
      },
      { threshold, rootMargin }
    );

    observerRef.current.observe(node);
  }).current;

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, []);

  return { isVisible, elementRef: refCallback };
}
```

> **Fixes:** (1) Changed from accepting `options?: IntersectionObserverInit` to accepting individual `threshold` and `rootMargin` parameters. Spreading an options object into the observer constructor is fragile when the values change between renders. (2) Used `refCallback` pattern instead of combining `useRef` + `useEffect` for more reliable DOM node tracking. (3) Added proper cleanup effect.
