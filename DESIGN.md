# UI/UX Design Specification: Foresight Studio

This document defines the canonical UX/UI design language, visual parameters, brand voice, and interaction states for the **Foresight Studio Collaborative SaaS Workspace**. 

All frontend implementations (React web app, Replit embeds, and visual canvas elements) must conform strictly to these patterns to eliminate "AI slop" and maintain a high-end, cohesive, studio-grade aesthetic.

---

## 1. Brand Identity & Creative Voice

*   **Design Concept:** "An Academic Notebook Crossed with a Modern Research Workspace."
*   **Tone of Voice:** Rigorous, collaborative, supportive, and accessible. It uses clear, jargon-free labels while maintaining methodological depth.
*   **Atmosphere:** Light, calm, spatial, and intellectually structured.
*   **Visual Direction (The Anti-Slop Pact):**
    *   **NO** purple-to-blue generic neon gradients.
    *   **NO** overused rounded-card-inside-rounded-card nesting.
    *   **NO** default framework styling or un-adjusted gaps.
    *   **YES** to tactile borders, crisp high-contrast text, generous breathing room, and micro-animations that represent connections.

---

## 2. Color System & Contrast (OKLCH Standards)

We leverage the modern **OKLCH** color space for perceptual uniformity, high-contrast compliance, and accessible dark-mode variants.

```css
:root {
  /* Brand Neutrals - Tactile, light warm paper background */
  --color-bg-base: oklch(0.99 0.003 40.0);       /* Extremely soft cream-white */
  --color-bg-surface: oklch(0.97 0.005 40.0);    /* Soft card / panel background */
  --color-border: oklch(0.88 0.005 40.0);        /* Fine, crisp tactile borders */
  
  /* High Contrast Typography */
  --color-text-primary: oklch(0.15 0.008 40.0);  /* Deep charcoal-brown */
  --color-text-secondary: oklch(0.45 0.008 40.0);/* Soft, legible grey */
  --color-text-muted: oklch(0.62 0.008 40.0);    /* Supporting details / timestamps */
  
  /* Strategic Category Colors (Muted, high-contrast tags) */
  --color-social: oklch(0.55 0.14 20.0);         /* Terra cotta */
  --color-technological: oklch(0.50 0.13 250.0);  /* Deep slate blue */
  --color-economic: oklch(0.48 0.11 140.0);      /* Sage green */
  --color-environmental: oklch(0.60 0.16 75.0);  /* Warm clay-yellow */
  --color-political: oklch(0.40 0.15 310.0);     /* Soft grape berry */
  --color-legal: oklch(0.42 0.10 190.0);         /* Teal */
  
  /* Status Signals */
  --color-glow-base: oklch(0.65 0.18 150.0);     /* Strategic convergence glow */
}
```

---

## 3. Typography & Measurement Layout

### Typography
*   **Primary System Font:** Standard system serif/sans combinations that evoke academic notebooks and premium workspaces.
    *   *Headers & Displays:* `Georgia`, `Baskerville`, or system serifs for editorial authority.
    *   *Interface & Metadata:* `system-ui`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `sans-serif` for clean readability.
*   **Scale Hierarchy:**
    *   `h1` (Display): `2.25rem` / line-height `1.2` (Tracked slightly tight).
    *   `h2` (Section): `1.5rem` / line-height `1.3`.
    *   `h3` (Card Header): `1.15rem` / line-height `1.4`.
    *   `body` (Paragraphs): `1rem` / line-height `1.6` (Max measure of `65ch` for reading comfort).
    *   `caption` (Labels): `0.8rem` / line-height `1.5` (Uppercase, slight letter-spacing for premium feel).

### Spacing & Grid (The 8px Baseline)
*   All layouts, margins, padding, and gaps are multiples of an 8px grid (`0.5rem`, `1rem`, `1.5rem`, `2rem`, `3rem`).
*   **Standard Spacing Rules:**
    *   Page Margins: `2.5rem` (Tablet), `4rem` (Desktop).
    *   Section Gap: `3rem` (To prevent structural compression).
    *   Card Padding: `1.5rem` internal padding.

---

## 4. Interaction Quality & Component States

To guarantee a highly finished, production-grade interactive experience across student data-entry and facilitator portals:

### 4.1 Form Fields (The Futures-Wheel Step Wizard)
*   **Default State:** Soft background, crisp border:
    `background: var(--color-bg-surface); border: 1px solid var(--color-border); padding: 0.75rem 1rem;`
*   **Focus State (Deliberate & Accessible):** Use a clean, non-offset focus ring utilizing our Technological slate-blue:
    `border-color: var(--color-technological); box-shadow: 0 0 0 3px oklch(0.50 0.13 250.0 / 0.15); outline: none;`
*   **Disabled State (Roster Locked):**
    `opacity: 0.6; cursor: not-allowed; background: oklch(0.92 0.003 40.0); color: var(--color-text-secondary);`
*   **Error State:** Clear, non-destructive error banners with concrete tips:
    `border-color: var(--color-social); background: oklch(0.55 0.14 20.0 / 0.05);`

### 4.2 Interactive Polar Radar Canvas
*   **Progressive Disclosure:** Clicking an active visual dot on the polar canvas triggers an **Obsidian-style detail drawer** that glides in from the right.
*   **Visual Glow:** Elements with higher convergence scores possess a subtle, soft drop-shadow radial glow:
    `filter: drop-shadow(0 0 8px var(--color-glow-base));`
*   **Hover Motif:** Hovering over a signal node highlights its connecting relational edges (`edges` table connections) with fine 1px dashed lines, while muting unrelated nodes.

---

## 5. Responsive Adapts & Accessibility (A11Y)

*   **Keyboard Navigation:** All cards, drawers, and form controls must be navigable via Tab keys. Focus states must remain visible and crisp.
*   **Screen Reader Landmarks:** Define explicit landmarks (`<main>`, `<nav>`, `<aside>`, `<section>`, `aria-describedby`) for complex panels.
*   **Responsive Composing:** Tablet and mobile layouts should reorganize content into vertical scrolls rather than shrinking elements, maintaining large touch targets (minimum `44px x 44px` for buttons).
