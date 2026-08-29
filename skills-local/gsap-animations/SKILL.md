---
name: gsap-animations
description: GSAP (GreenSock Animation Platform) skill for creating professional web animations. Covers all GSAP plugins including ScrollTrigger, Flip, Draggable, MotionPath, SplitText, DrawSVG, MorphSVG, ScrollSmoother, Observer, and TextPlugin. Use when the user needs web animations, scroll effects, interactive UI animations, SVG animations, or timeline-based motion design.
author: xerxes-on
version: "1.0.0"
tags:
  - animation
  - gsap
  - scroll
  - svg
  - motion
  - frontend
---

# GSAP Animations Skill

When this skill is invoked, you MUST ask the user clarifying questions before writing any animation code. Use the AskUserQuestion tool to gather requirements.

## Required Questions (ALWAYS ASK)

Before implementing ANY animation, ask the user:

1. **What elements to animate?** - CSS selectors, component names, or element descriptions
2. **What type of animation?** - Choose from the categories below
3. **When should it trigger?** - On load, scroll, hover, click, or custom event
4. **Any specific timing preferences?** - Duration, delay, easing style

### Animation Categories to Present

When asking about animation type, present these options:

**Basic Animations:**
- Fade (in/out/cross-fade)
- Slide (up/down/left/right)
- Scale (grow/shrink/pulse)
- Rotate (spin/flip/wobble)
- Combined (fade + slide, scale + rotate, etc.)

**Advanced Animations:**
- Stagger (animate list items sequentially)
- Timeline (choreographed multi-step sequence)
- Morph (transform between shapes)
- Path (move along SVG path)
- Parallax (depth-based scroll effects)

**Scroll-Based:**
- Scroll-triggered (animate when element enters view)
- Scrub (animation linked to scroll position)
- Pin (freeze element while scrolling)
- Parallax layers (different speeds)
- Smooth scroll (momentum-based scrolling)

**Interactive:**
- Hover effects
- Click/tap animations
- Drag interactions
- Gesture responses

**Text Animations:**
- Typewriter effect
- Character-by-character reveal
- Word-by-word animation
- Line-by-line stagger
- Text morphing

**SVG Animations:**
- Draw stroke (line drawing effect)
- Morph shapes
- Path animation
- Fill transitions

---

## Installation

### CDN (All Plugins)
```html
<!-- Core -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>

<!-- Free Plugins -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/Draggable.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/MotionPathPlugin.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/TextPlugin.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/Observer.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollToPlugin.min.js"></script>
```

### NPM
```bash
npm install gsap
```

```javascript
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);
```

---

## Core Methods

### gsap.to() - Animate TO destination values
```javascript
gsap.to(".box", {
  x: 100, y: 50, rotation: 360, scale: 1.5,
  opacity: 0.5, duration: 1, ease: "power2.out"
});
```

### gsap.from() - Animate FROM starting values
```javascript
gsap.from(".box", { opacity: 0, y: -50, duration: 1 });
```

### gsap.fromTo() - Define both start and end
```javascript
gsap.fromTo(".box",
  { opacity: 0, x: -100 },
  { opacity: 1, x: 0, duration: 1 }
);
```

### gsap.set() - Instantly set properties (no animation)
```javascript
gsap.set(".box", { x: 100, opacity: 0.5 });
```

---

## All Animatable Properties

### Transform Properties
| Property | Description | Example |
|----------|-------------|---------|
| `x` | Horizontal position (px) | `x: 100` |
| `y` | Vertical position (px) | `y: -50` |
| `xPercent` | Horizontal position (%) | `xPercent: 50` |
| `yPercent` | Vertical position (%) | `yPercent: -100` |
| `rotation` | Rotation (degrees) | `rotation: 360` |
| `rotationX` | 3D X rotation | `rotationX: 45` |
| `rotationY` | 3D Y rotation | `rotationY: 180` |
| `scale` | Uniform scale | `scale: 1.5` |
| `scaleX` | Horizontal scale | `scaleX: 2` |
| `scaleY` | Vertical scale | `scaleY: 0.5` |
| `skewX` | Horizontal skew (degrees) | `skewX: 20` |
| `skewY` | Vertical skew (degrees) | `skewY: 10` |
| `transformOrigin` | Transform pivot point | `transformOrigin: "center center"` |
| `transformPerspective` | 3D perspective | `transformPerspective: 500` |

### Special Properties
| Property | Description | Example |
|----------|-------------|---------|
| `duration` | Animation length (seconds) | `duration: 1` |
| `delay` | Wait before starting | `delay: 0.5` |
| `ease` | Easing function | `ease: "power2.out"` |
| `stagger` | Offset for multiple targets | `stagger: 0.1` |
| `repeat` | Iterations (-1 = infinite) | `repeat: 2` |
| `yoyo` | Reverse on repeat | `yoyo: true` |
| `paused` | Start paused | `paused: true` |

---

## All Easing Functions

Format: `ease: "name.direction"`

### Easing Names
| Name | Description |
|------|-------------|
| `none` | Linear, no easing |
| `power1` | Subtle acceleration |
| `power2` | Moderate acceleration (DEFAULT) |
| `power3` | Strong acceleration |
| `power4` | Very strong acceleration |
| `back` | Overshoots then settles |
| `bounce` | Bounces like a ball |
| `circ` | Circular motion feel |
| `elastic` | Springy, elastic motion |
| `expo` | Exponential acceleration |
| `sine` | Sinusoidal, very smooth |
| `steps(n)` | Steps (n = number of steps) |

### Directions: `.in`, `.out`, `.inOut`

---

## Timelines

### Basic Timeline
```javascript
const tl = gsap.timeline();
tl.to(".box1", { x: 100, duration: 1 })
  .to(".box2", { y: 100, duration: 0.5 })
  .to(".box3", { rotation: 360, duration: 1 });
```

### Position Parameters
| Position | Description |
|----------|-------------|
| (none) | After previous animation ends |
| `"<"` | At start of previous animation |
| `">"` | At end of previous animation |
| `"+=0.5"` | 0.5s after timeline ends |
| `"-=0.5"` | 0.5s before timeline ends |
| `2` | At exactly 2 seconds |

### Timeline Controls
```javascript
tl.play(); tl.pause(); tl.resume(); tl.reverse();
tl.restart(); tl.seek(1.5); tl.progress(0.5);
tl.timeScale(2); tl.kill();
```

---

## ScrollTrigger Plugin

### Full Configuration
```javascript
gsap.to(".box", {
  x: 500,
  scrollTrigger: {
    trigger: ".box",
    start: "top 80%",
    end: "bottom 20%",
    scrub: true,
    pin: true,
    markers: true, // DEBUG only - remove in production
    toggleActions: "play pause resume reset",
    toggleClass: "active",
    snap: 1 / (sections.length - 1),
    onEnter: () => {},
    onLeave: () => {},
    onUpdate: (self) => {},
  }
});
```

### With Timeline
```javascript
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".container",
    start: "top top",
    end: "+=1000",
    scrub: 1,
    pin: true
  }
});
tl.to(".box1", { x: 100 })
  .to(".box2", { y: 100 }, "<")
  .to(".box3", { rotation: 360 });
```

---

## Draggable Plugin
```javascript
Draggable.create(".box", {
  type: "x,y",
  bounds: "#container",
  inertia: true,
  snap: { x: (v) => Math.round(v/50)*50 },
  onDragEnd: function() {}
});
```

---

## MotionPath Plugin
```javascript
gsap.to(".element", {
  duration: 5,
  motionPath: {
    path: "#svgPath",
    align: "#svgPath",
    autoRotate: true,
  },
  ease: "power1.inOut"
});
```

---

## Flip Plugin (Club)
```javascript
const state = Flip.getState(".boxes");
// Make DOM changes...
Flip.from(state, { duration: 0.5, ease: "power1.inOut", stagger: 0.1 });
```

---

## Framework Integration

### React with useGSAP
```javascript
import { useGSAP } from "@gsap/react";

function Component() {
  const container = useRef();
  useGSAP(() => {
    gsap.to(".box", { x: 100 });
  }, { scope: container });
  return <div ref={container}><div className="box" /></div>;
}
```

### gsap.context() for cleanup
```javascript
useEffect(() => {
  const ctx = gsap.context(() => {
    gsap.to(".box", { x: 100 });
  }, containerRef);
  return () => ctx.revert();
}, []);
```

---

## Common Animation Patterns

### Page Load Sequence
```javascript
const tl = gsap.timeline();
tl.from(".logo", { opacity: 0, y: -50, duration: 0.5 })
  .from(".nav-item", { opacity: 0, y: -20, stagger: 0.1 }, "-=0.2")
  .from(".hero-title", { opacity: 0, x: -100, duration: 0.8 }, "-=0.3")
  .from(".cta-button", { opacity: 0, scale: 0.5, ease: "back.out" }, "-=0.2");
```

### Scroll-Triggered Sections
```javascript
gsap.utils.toArray(".section").forEach((section) => {
  gsap.from(section.querySelectorAll(".fade-in"), {
    opacity: 0, y: 50, stagger: 0.1, duration: 0.8,
    scrollTrigger: { trigger: section, start: "top 80%",
      toggleActions: "play none none reverse" }
  });
});
```

### Infinite Marquee
```javascript
gsap.to(content, {
  x: -contentWidth, duration: 20, ease: "none", repeat: -1,
  modifiers: { x: gsap.utils.unitize(x => parseFloat(x) % contentWidth) }
});
```

---

## Best Practices

1. **Use transforms** - `x`, `y`, `scale`, `rotation` instead of `left`, `top`, `width`, `height`
2. **Use `autoAlpha`** - Combines `opacity` with `visibility` for better performance
3. **Register plugins** - Always `gsap.registerPlugin()` before using
4. **Use `gsap.context()`** - Essential for React/Vue cleanup
5. **Remove markers** - Always remove `markers: true` in production
6. **Use `overwrite: "auto"`** - Prevents conflicting tweens
7. **Batch with stagger** - Use `stagger` instead of loops
8. **Use `will-change`** - Add `will-change: transform` to heavily animated elements
9. **Test reduced motion** - Respect `prefers-reduced-motion`
10. **Use `invalidateOnRefresh`** - For responsive ScrollTriggers
