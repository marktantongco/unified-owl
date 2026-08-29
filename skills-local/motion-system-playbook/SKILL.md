# motion-system-playbook

## context
Use this skill whenever you add, review, or optimize any animation—web or mobile. It ensures every motion is purposeful, performant at 60fps, accessible to all users, and safe when multiple animations coexist. This is the "how to not break things" layer. It delegates actual syntax to domain-specific skills (GSAP, framer-motion, three-r3f, lottie, motion-one, remotion, css-native, reanimated) but governs rules, sequencing, library selection, and safeguards. It also ensures animations never regress Core Web Vitals and always pass a reduced-motion audit.

---

## PART 0 — LIBRARY SELECTION MATRIX

Choose the right tool for the job. Wrong choice = unnecessary complexity and performance debt.

| Library | Best Frontend Pairing | Web/Mobile | Bundle Size | Thread Model | Ideal For |
|---------|----------------------|------------|-------------|--------------|-----------|
| **CSS Animations / WAAPI** | Any (vanilla, React, Vue, Svelte) | Web + Mobile Web | 0 KB | Compositor thread | Simple state transitions, hover effects, scroll-driven without JS |
| **GSAP** | Any (framework-agnostic) | Web | ~50 KB | JS thread + GPU composite | Complex timelines, scroll-triggered sequences, SVG, high-precision |
| **Framer Motion (Motion)** | React, Next.js | Web + Mobile Web | ~60 KB | JS + GPU composite | Component mount/unmount, layout animations, gestures, "delight" |
| **Motion One** | Any (WAAPI-based, 3.8 KB) | Web + Mobile Web | ~3.8 KB | Compositor thread | Micro-interactions, lightweight replacements, low-budget perf |
| **React Spring** | React | Web + Mobile Web | ~20 KB | JS thread (physics) | Physics-based interactions, gestures, fluid transitions |
| **Three.js / R3F** | React / R3F | Web | ~130 KB (3D) | WebGL/WebGPU | 3D scenes, product configurators, immersive, particles |
| **Lottie (dotLottie)** | Any (ThorVG WASM) | Web + Mobile (iOS, Android, RN) | Varies (80% smaller as .lottie) | GPU + WASM | Designer handoff, After Effects exports, splash/onboarding |
| **Rive** | React Native, Flutter, Web | Web + Mobile | Small (runtimes) | Native GPU | Interactive state machines, character animation, real-time |
| **React Native Reanimated** | React Native | Mobile (iOS, Android) | ~150 KB | UI thread (native, not JS) | Gesture-driven, 60fps native, complex mobile interactions |
| **Remotion** | React (programmatic video) | Web (render to MP4) | ~30 KB | React reconciler | Video generation from React components, data-driven videos |
| **Anime.js** | Any | Web | ~18 KB | JS thread | SVG, CSS, DOM sequencing, creative demos |

**Decision flow:**
1. Is it a simple hover/fade/toggle? → **CSS** first. Always.
2. Is it React component enter/exit/layout change? → **Framer Motion**.
3. Is it a complex timeline with precise sequencing? → **GSAP**.
4. Is it 3D or immersive? → **Three.js / R3F**.
5. Is it a designer-handoff animation (After Effects)? → **dotLottie**.
6. Is it React Native with gestures? → **Reanimated**.
7. Is it interactive state-machine animation? → **Rive**.
8. Is it programmatic video rendering? → **Remotion**.
9. Is it a small (under 4KB budget) micro-interaction? → **Motion One**.
10. Is it physics-based (springs, decay, gestures)? → **React Spring** or Framer Motion's `spring` type.

---

## PART 1 — UNIVERSAL RULES (All Libraries)

### 1.1 Performance: Animate Only These Properties
**Always GPU-safe:**
- `transform` (translate, scale, rotate, skew) — use `x`, `y` in Framer Motion/GSAP
- `opacity`

**Never animate these (trigger layout → 50% frame drops):**
- `width`, `height`
- `top`, `left`, `right`, `bottom`, `margin`, `padding`
- `border-width`, `font-size`

**Why:** Browsers render in pipeline: Style → Layout → Paint → Composite. `transform` and `opacity` skip Layout and Paint entirely, staying on the compositor thread. Everything else forces costly recalculation.

**Golden rule:** If you're animating anything other than `transform` or `opacity`, justify it in a comment. It's wrong 90% of the time.

### 1.2 Duration Ceilings
| Animation Type | Max Duration | Rationale |
|---------------|-------------|-----------|
| Micro-interactions (hover, focus) | 100–200ms | Feedback must feel instant |
| Standard show/hide | 200–300ms | Users perceive >300ms as sluggish |
| Page transitions | 300–400ms | Long enough to notice, short enough to not wait |
| Decorative/ambient | Up to 1000ms | Only if non-functional |

### 1.3 will-change: The Knife That Cuts Both Ways
- **Add dynamically** before animation starts: `element.style.willChange = 'transform'`
- **Remove immediately** after animation ends (listen to `transitionend` / `animationend` or GSAP's `onComplete`): `element.style.willChange = 'auto'`
- **Never** apply statically in CSS — creates "compositor layer explosion," tanks mobile GPU memory, causes OOM and 20fps jank on mid-range Android.
- **Only** set on the element being animated, not on parent containers.
- Fallback: if animation is shorter than 16ms (iOS Safari may not fire `animationend`), use `setTimeout(() => el.style.willChange = 'auto', duration + 100)`.

### 1.4 Backdrop-Blur Limits
- Max 3–5 simultaneous blur effects on mobile.
- Max blur value: 12px.
- Respect `prefers-reduced-transparency` media query.

---

## PART 2 — ACCESSIBILITY (Universal)

### 2.1 Reduced Motion
Every animation must be wrapped:
```js
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (prefersReduced) {
  // skip animation or replace with instant state change
}
```

- Framer Motion: use useReducedMotion() hook.
- GSAP: check before creating timelines.
- CSS: @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; } }

### 2.2 Site-Wide Motion Toggle
Provide a visible toggle that persists to localStorage. On toggle:
- Kill all running GSAP timelines (ScrollTrigger.getAll().forEach(st => st.kill())).
- Disable Framer Motion's AnimatePresence animations.
- Refresh scroll positions to avoid broken states.
- Call ScrollTrigger.refresh() after toggle.

### 2.3 Motion Boundaries
- Never animate elements that overlap with interactive controls during animation.
- Ensure pointer-events: none on animating elements during entrance to prevent misclicks.
- Restore pointer-events: auto on animationend.

---

## PART 3 — LIBRARY-SPECIFIC RULES

### 3.1 CSS Animations (Native)
Best for: Simple hover states, fade-ins, scroll-driven animations.

Rules:
- Use @keyframes + animation for declarations. CSS scroll-driven: view-timeline and scroll-timeline run on compositor thread, zero JS overhead.
- Prefer transition over animation for two-state changes.
- Always test animation-fill-mode: forwards to prevent snap-back on completion.
- Avoid animation-delay with negative values — causes initial flash.

When NOT to use CSS:
- When you need to pause/resume/seek (CSS has no API for frame control).
- When animation is gesture-driven (needs JS event handling).
- When you need to sequence multiple elements with dynamic stagger.

### 3.2 GSAP (GreenSock)
Best for: Complex timelines, scroll-triggered sequences, SVG animation, framework-agnostic precision.

Rules:
- Use GSAP's built-in ticker — never setTimeout for animation frames.
- ScrollTrigger: always call .refresh() after route change, DOM insertion, or motion toggle.
- Kill timelines on unmount: return () => { tl.kill(); ScrollTrigger.getAll().forEach(st => st.refresh()); }
- Cap ScrollTrigger instances: Max 15–20 per page. Above that, batch into fewer timelines.
- Animate only x, y, scale, rotate, opacity — never left, top, width, height in GSAP tweens.

GSAP specific gotchas:
- from tweens can cause flash of unstyled content. Use fromTo instead.
- stagger combined with ScrollTrigger — verify each element's trigger position.
- ScrollTrigger.matchMedia() must be used for responsive breakpoints.

### 3.3 Framer Motion (Motion)
Best for: React apps — mount/unmount, layout animations, page transitions.

Rules:
- Always use viewport={{ once: true }} on scroll-triggered whileInView animations.
- Use layout prop sparingly — it recalculates FLIP transforms on every re-render.
- Prefer variants for coordinated children (staggerChildren, delayChildren).
- useReducedMotion() hook must wrap all animated components.
- AnimatePresence requires unique key on every child.
- Hover/tap micro-interactions: use whileHover/whileTap with type: "spring".
- Avoid animating large component trees — split into small isolated motion.div wrappers.
- Limit concurrent animations: max 2–3 elements animating at once on mobile.

### 3.4 Motion One
Best for: Lightweight micro-interactions, tiny bundle budgets, framework-agnostic.

Rules:
- Built on Web Animations API (WAAPI) — runs on compositor thread by default.
- 3.8 KB bundle — use when Framer Motion's 60 KB is unacceptable.
- Composable: chain animations via promises.
- Limitation: No layout animation equivalent. No AnimatePresence.

### 3.5 React Spring
Best for: Physics-based UI interactions, gestures, continuous spring animations.

Rules:
- Use useSpring for continuous physics-driven values, useTransition for mount/unmount effects.
- Spring config: { tension: 170, friction: 26 } is the standard "natural" feel.
- Physics animations can overshoot — ensure bounds on numeric values.

### 3.6 Three.js + React Three Fiber (R3F)
Best for: 3D immersive experiences, product configurators, portfolios, particles.

R3F Performance Rules:
- Enable on-demand rendering: Canvas frameloop="demand".
- Use Detailed (LOD) for complex models.
- Share material instances via useMemo.
- Use instancedMesh for repeated objects.
- KTX2 compressed textures: 2x-4x smaller GPU memory footprint.
- Migrate from WebGL to WebGPU renderer for 2026+ targets.

3D Animation Safety:
- 3D scenes must pause rendering when tab is hidden.
- Always test on low-end mobile — target 30fps on mid-range Android for 3D.

### 3.7 Lottie (dotLottie)
Best for: Designer-created animations, splash screens, loading states, icons.

Rules:
- Always optimize before shipping: Convert to .lottie format (80% reduction).
- Rendering: Use ThorVG WASM runtime — identical engine across platforms.
- File size: Lottie JSON files over 100 KB unoptimized must be optimized.
- Interactivity: Use dotLottie State Machines for interactive states.

### 3.8 Rive
Best for: Interactive character animation, real-time state machines, cross-platform runtime.

Rules:
- Use for stateful, interactive animations (not passive playback — Lottie is better for that).
- State Machines are the killer feature.
- Limitation: Smaller community, fewer pre-made assets.

### 3.9 React Native Reanimated
Best for: React Native apps with gesture-driven interactions.

Rules:
- Runs animations on UI thread (native), not JS thread.
- Use useSharedValue and useAnimatedStyle for 60fps animations.
- Pair with react-native-gesture-handler for gesture-driven interactions.
- Worklets execute on UI thread — never call console.log inside worklets.

### 3.10 Remotion
Best for: Programmatic video rendering from React components.

Rules:
- Always drive animations by useCurrentFrame() — never CSS transitions.
- Use interpolate() for readable animation math.
- Render via renderMedia() with inputProps for data-driven batch rendering.
- Perf: Render at 30fps for social media content.

---

## PART 4 — COMBO PATTERNS (Multi-Library Safety)

### 4.1 GSAP + Framer Motion in Same Page
- GSAP handles scroll-driven animations (ScrollTrigger).
- Framer Motion handles component mount/unmount (AnimatePresence).
- Never animate the same DOM element with both libraries.
- Use a boundary: GSAP animates .gsap-section, Framer Motion animates .react-section.

### 4.2 Three.js + Scroll (R3F + GSAP ScrollTrigger)
- R3F Canvas is a black box to DOM scroll. Sync via useFrame reading GSAP's scroll progress.
- Don't use ScrollTrigger on R3F elements — feed GSAP values into R3F's useFrame.
- On page exit: pause useFrame loop, kill GSAP timeline, dispose Three.js geometry/texture.

### 4.3 Lottie + Any JS Animation Library
- Lottie runs its own render loop. Don't nest inside GSAP/Framer Motion animations.
- Control Lottie playback via library's imperative API (.play(), .stop()).
- If Lottie must appear inside a page transition: pause Lottie during transition, resume after.

### 4.4 CSS Scroll-Driven + Framer Motion
- CSS view-timeline/scroll-timeline and Framer Motion's whileInView can overlap. Choose ONE per element.
- CSS scroll-driven is more performant (compositor thread). Use for simple animations.
- Use Framer Motion when you need variants, stagger, or exit animations.

### 4.5 Global Animation Coordinator
When multiple components animate independently on one page:
1. Create a simple AnimationCoordinator (event-based)
2. Page entrance: Stagger top-to-bottom. Max 3 concurrent animations.
3. Page exit: Reverse order, half duration, kill all after 500ms.

---

## PART 5 — TESTING & QA

After implementing any animation, run this audit:

1. **Reduced Motion Test**: Toggle prefers-reduced-motion: reduce. Site must be fully functional. Zero exceptions.
2. **CPU Throttle Test**: Chrome DevTools → Performance → 6x CPU slowdown. No frame drops below 30fps.
3. **Paint Flashing**: Chrome DevTools → Rendering → Paint Flashing. No unnecessary paints outside animated elements.
4. **Mobile Device Test**: Real mid-range Android device. If simple animations drop below 30fps, reduce complexity.
5. **Memory Leak Test**: Mount/unmount component 20 times. Heap snapshot before/after — no retained animation objects.
6. **Core Web Vitals**: Animation must not regress LCP or CLS. All animated elements need explicit width/height.

---

## constraints
- Never animate without a purpose. Decorative animations must be removable in reduced-motion mode.
- Never animate width, height, top, left, right, bottom, margin, or padding. Ever.
- Always kill timelines on component unmount.
- Always respect prefers-reduced-motion. No exceptions. Non-negotiable.
- No animation may block user interaction. Max duration 300ms for UI feedback, 400ms for page transitions.
- Never mix two animation libraries on the same DOM element.
- will-change must be added dynamically and removed after animation. Never static CSS.
- Backdrop-blur limited to 3–5 elements and <=12px blur.
- Scroll-driven animations: max 15–20 ScrollTrigger instances per page.
- R3F: always test on low-end mobile; 30fps acceptable for 3D.
- Lottie files over 100 KB must be optimized before production.
- Never animate more than 2–3 elements simultaneously on mobile.

## examples
1. **React e-commerce product page**: Framer Motion for product list mount/unmount (staggerChildren 0.1s, whileInView with once: true), CSS for hover effects on cards (transition: transform 0.2s ease), Lottie for add-to-cart success animation (optimized .lottie, 40 KB), GSAP for scroll-triggered hero parallax. Each library operates on its own DOM boundary.
2. **React Native onboarding**: Reanimated for gesture-driven swipe between screens (UI thread, 60fps), dotLottie for splash animation (ThorVG runtime, 80% smaller than JSON), LayoutAnimation for accordion expand in FAQ. Zero jank because animations don't share DOM elements or threads.
3. **3D portfolio with scroll**: R3F for 3D scene (Canvas frameloop="demand"), GSAP for scroll progress fed into R3F's useFrame, Framer Motion for UI overlay enter/exit. GSAP kills and R3F geometry disposes on route exit.
