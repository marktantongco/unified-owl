# gumroad-pipeline - Digital product monetization funnel

## Context
Use this skill when you need to design, launch, or optimize a digital product sales funnel on Gumroad (or similar platforms like Lemon Squeezy, Payhip). It covers the full monetization pipeline: product packaging, pricing strategy, landing page copy, email sequences, and conversion optimization. This skill fills the monetization gap between content-strategy (which plans content) and social-media-manager (which distributes it) — neither handles the revenue conversion step.

## Instructions
1. **Product Definition**: Identify the digital product type (ebook, course, template, tool, community access). Define the core value proposition and target buyer persona.
2. **Pricing Strategy**: Determine pricing using value-based analysis. Consider: tiered pricing (free teaser + paid full), pay-what-you-want floor, bundle discounts, and cohort-based launch pricing. Never price below $5 for digital products (undermines perceived value).
3. **Landing Page**: Generate Gumroad product page copy following the PAS framework (Problem, Agitate, Solve). Include: headline, subheadline, 3-5 benefit bullets, social proof placeholder, FAQ, and CTA. Keep total copy under 500 words.
4. **Email Sequence**: Design a 5-email launch sequence: (1) Announcement with early-bird pricing, (2) Social proof and testimonials, (3) Objection handling, (4) Urgency — deadline reminder, (5) Last call with bonus. Each email under 200 words.
5. **Conversion Tracking**: Define key metrics: visit-to-purchase rate, email open rate, refund rate. Set up tracking via Gumroad analytics or UTM parameters. Flag any conversion rate below 2% as needing optimization.
6. **Post-Purchase Flow**: Generate a thank-you email, upsell sequence for complementary products, and a review request template. Include a "share with a friend" discount code generator.

## Constraints
- Never recommend pricing below $5 for standalone digital products.
- Landing page copy must be under 500 words — Gumroad pages that scroll lose conversion.
- Email sequences must not exceed 5 emails in the launch window — fatigue kills open rates.
- Always include a free tier or sample — zero-friction entry converts 3-5x better than paid-only.
- Do not generate fake testimonials or social proof — use placeholder format: "[Add real testimonial from beta user]".

## Error Handling
All errors are typed and surfaced. Never swallow failures silently.

| Error Type | Code | When | Action |
|-----------|------|------|--------|
| NoProductError | GP-001 | No product type or value proposition defined | Halt and prompt: "What are you selling and to whom?" |
| PricingBelowFloorError | GP-002 | Price set below $5 for standalone product | Reject price, explain value perception risk, suggest minimum |
| CopyLengthError | GP-003 | Landing page copy exceeds 500 words | Flag section that's too long, suggest cuts |
| EmailSequenceOverflowError | GP-004 | More than 5 emails in launch window | Trim to 5, flag which emails to cut based on lowest expected ROI |
| LowConversionWarning | GP-005 | Conversion rate tracking shows below 2% | Generate A/B test suggestions: headline, price point, CTA |
| MissingSocialProofError | GP-006 | No testimonials or proof sections defined | Insert placeholder with format for real testimonial collection |

## Examples
1. Product: "50 ChatGPT Prompts for SaaS Founders" ebook at $19.
   - Pricing: Single tier at $19, with 3 free sample prompts as teaser.
   - Landing page: PAS framework, 380 words, 4 benefit bullets, 2 FAQ items.
   - Email sequence: 5 emails over 7 days, early-bird $14 for first 48 hours.
   - Metrics target: 3% visit-to-purchase, 45% email open rate, under 5% refund rate.

2. Error scenario: User sets price at $2 for an ebook.
   → Raises `PricingBelowFloorError(GP-002)` — "Price $2 is below the $5 floor. Digital products priced under $5 signal low value. Recommended: $9-$19 for ebooks. Want me to recalculate with value-based pricing?"
