# Next.js Best Practices

---
name: next-best-practices
description: Next.js best practices - file conventions, RSC boundaries, data patterns, async APIs, metadata, error handling, route handlers, image/font optimization, bundling
---

# Next.js Best Practices

Apply these rules when writing or reviewing Next.js code.

## File Conventions
- Project structure and special files
- Route segments (dynamic, catch-all, groups)
- Parallel and intercepting routes
- Middleware rename in v16 (middleware -> proxy)

## RSC Boundaries
- Detect invalid React Server Component patterns
- Async client component detection (invalid)
- Non-serializable props detection
- Server Action exceptions

## Async Patterns
- Async `params` and `searchParams`
- Async `cookies()` and `headers()`
- Migration codemod

## Runtime Selection
- Default to Node.js runtime
- When Edge runtime is appropriate

## Directives
- `'use client'`, `'use server'` (React)
- `'use cache'` (Next.js)

## Functions
- Navigation hooks: `useRouter`, `usePathname`, `useSearchParams`, `useParams`
- Server functions: `cookies`, `headers`, `draftMode`, `after`
- Generate functions: `generateStaticParams`, `generateMetadata`

## Error Handling
- `error.tsx`, `global-error.tsx`, `not-found.tsx`
- `redirect`, `permanentRedirect`, `notFound`
- `forbidden`, `unauthorized` (auth errors)

## Data Patterns
- Server Components vs Server Actions vs Route Handlers
- Avoiding data waterfalls (`Promise.all`, Suspense, preload)
- Client component data fetching

## Image Optimization
- Always use `next/image` over `<img>`
- Remote images configuration
- Responsive `sizes` attribute
- Priority loading for LCP

## Font Optimization
- `next/font` setup
- Google Fonts, local fonts
- Tailwind CSS integration

## Bundling
- Server-incompatible packages
- CSS imports (not link tags)
- Bundle analysis
