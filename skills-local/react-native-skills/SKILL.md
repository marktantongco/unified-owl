# React Native Skills

---
name: vercel-react-native-skills
description: React Native and Expo best practices for building performant mobile apps. Use when building React Native components, optimizing list performance, implementing animations, or working with native modules.
metadata:
  author: vercel
  version: "1.0.0"
---

# React Native Skills

Comprehensive best practices for React Native and Expo applications. Contains rules across multiple categories covering performance, animations, UI patterns, and platform-specific optimizations.

## When to Apply

Reference these guidelines when:
- Building React Native or Expo apps
- Optimizing list and scroll performance
- Implementing animations with Reanimated
- Working with images and media
- Configuring native modules or fonts
- Structuring monorepo projects with native dependencies

## Rule Categories by Priority

| Priority | Category         | Impact   | Prefix               |
| -------- | ---------------- | -------- | -------------------- |
| 1        | List Performance | CRITICAL | `list-performance-`  |
| 2        | Animation        | HIGH     | `animation-`         |
| 3        | Navigation       | HIGH     | `navigation-`        |
| 4        | UI Patterns      | HIGH     | `ui-`                |
| 5        | State Management | MEDIUM   | `react-state-`       |
| 6        | Rendering        | MEDIUM   | `rendering-`         |
| 7        | Monorepo         | MEDIUM   | `monorepo-`          |
| 8        | Configuration    | LOW      | `fonts-`, `imports-` |

## Quick Reference

### 1. List Performance (CRITICAL)
- Use FlashList for large lists
- Memoize list item components
- Stabilize callback references
- Avoid inline style objects

### 2. Animation (HIGH)
- Animate only transform and opacity
- Use useDerivedValue for computed animations
- Use Gesture.Tap instead of Pressable

### 3. Navigation (HIGH)
- Use native stack and native tabs over JS navigators

### 4. UI Patterns (HIGH)
- Use expo-image for all images
- Use Pressable over TouchableOpacity
- Handle safe areas in ScrollViews
- Use native context menus and modals

### 5. State Management (MEDIUM)
- Minimize state subscriptions
- Use dispatcher pattern for callbacks
- Show fallback on first render

### 6. Rendering (MEDIUM)
- Wrap text in Text components
- Avoid falsy && for conditional rendering

### 7. Monorepo (MEDIUM)
- Keep native dependencies in app package
- Use single dependency versions across packages

### 8. Configuration (LOW)
- Use config plugins for custom fonts
- Organize design system imports
