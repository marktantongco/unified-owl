# Deployment Manager

## Context

Use this skill to deploy projects, configure CI/CD, manage environment variables, monitor deployment health, or execute rollbacks. Covers GitHub Pages, Vercel, and Netlify.

**Trigger phrases:** "deploy to Vercel/Netlify/GitHub Pages," "configure CI/CD," "rollback deployment," "monitor uptime," "environment variables."

---

## Instructions

### Step 1: Pre-Deployment Checklist

1. **Build locally:** `npm run build` — no errors, reasonable bundle size.
2. **Test:** `npm run test -- --coverage` + `npm run lint` — all pass.
3. **Environment:** create `.env.example` (document vars, no secrets), verify `.gitignore` includes `.env*`.
4. **Git:** all changes committed, correct branch (`main`), no untracked files.

### Step 2: Platform Deployment

#### GitHub Pages
5. Static sites only. Add `.github/workflows/deploy.yml` with `actions/deploy-pages`.
6. Set output directory (`dist`/`build`). Settings -> Pages -> Source: GitHub Actions.
7. For SPAs: add `404.html` redirecting to `index.html`. Set `base` in build config.

#### Vercel
8. Connect repo or `npx vercel`. Auto-detects framework; override build/output commands if needed.
9. Set env vars in Project Settings -> Environment Variables (Production/Preview/Dev).
10. **Custom domain:** add in Settings -> Domains. DNS: CNAME to `cname.vercel-dns.com` or A record `76.76.21.21`. SSL auto-provisioned.

#### Netlify
11. `npm i -g netlify-cli && netlify init`. Set build command and publish directory.
12. **Redirects** in `netlify.toml`: `[[redirects]] from="/*" to="/index.html" status=200`.
13. Set env vars in Site Settings -> Environment.

### Step 3: SSL & CDN

14. All platforms auto-provision SSL (Let's Encrypt). Verify HTTPS is active.
15. **Cache headers** for hashed assets: `Cache-Control: public, max-age=31536000, immutable`.
16. **Lighthouse audit:** target Performance > 90, Accessibility > 90. Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1.

### Step 4: Monitoring

17. **Uptime:** UptimeRobot (free, 1-5 min checks) or BetterUptime.
18. **Errors:** Sentry (free tier). Add `Sentry.init({ dsn })` in app entry.
19. **Alerts:** email on > 5 errors/hour, Slack on > 10 errors/hour.
20. **Performance:** Vercel Speed Insights or Netlify Analytics. Track load times, API latency, bundle size trends.

### Step 5: Update & Rollback

21. **Update flow:** Pull -> Install -> Test -> Build -> Push to main -> CI runs -> Verify -> Smoke test -> Monitor 15 min.
22. **Rollback by platform:**
    - Vercel: Dashboard -> Deployments -> "..." -> Promote to Production (30s)
    - Netlify: Dashboard -> Deploys -> Rollback previous
    - GitHub Pages: `git revert <hash>` -> push -> Actions redeploys
23. **Smoke test:** homepage loads, nav works, key flows function, no console errors, assets load, APIs respond.

---

## Constraints

- NEVER deploy locally to production for team projects. Always use CI/CD.
- NEVER commit secrets. Use platform UI or encrypted secrets.
- ALWAYS test on preview before promoting to production.
- ALWAYS have a rollback plan before deploying.
- NEVER skip the post-deploy smoke test.
- Environment variables MUST be documented in `.env.example`.
- SSL MUST be active on production.
- Deploy logs MUST be checked for warnings even on successful builds.

---

## Examples

### Example 1: React SPA -> Vercel

```
Project: React + TypeScript + Vite portfolio
1. npm run build -> dist/
2. Push to GitHub main -> Vercel auto-deploys
3. Env vars: VITE_API_URL, VITE_CONTACT_EMAIL
4. Domain: portfolio.jane.dev -> CNAME cname.vercel-dns.com
5. SSL auto, Lighthouse 96/98/100
6. Sentry for errors, UptimeRobot 5-min pings
Rollback: Vercel dashboard -> Promote previous deploy
```

### Example 2: Docs Site -> GitHub Pages

```
Project: Astro + Tailwind documentation
1. .github/workflows/deploy.yml -> actions/deploy-pages
2. Push main -> Actions builds and deploys
3. Domain: docs.project.com -> CNAME github.io
4. Enable Enforce HTTPS toggle
5. 404.html for SPA routing fallback
6. UptimeRobot 1-min checks -> Slack alerts
7. Weekly Lighthouse via cron GitHub Action
Rollback: git revert <hash> -> push -> Actions redeploys
```
