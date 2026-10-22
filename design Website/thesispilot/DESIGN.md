---
name: ThesisPilot
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#3f4850'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#707881'
  outline-variant: '#bfc7d2'
  surface-tint: '#006398'
  primary: '#006194'
  on-primary: '#ffffff'
  primary-container: '#007bb9'
  on-primary-container: '#fdfcff'
  inverse-primary: '#93ccff'
  secondary: '#006c49'
  on-secondary: '#ffffff'
  secondary-container: '#6cf8bb'
  on-secondary-container: '#00714d'
  tertiary: '#825100'
  on-tertiary: '#ffffff'
  tertiary-container: '#a36700'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#cce5ff'
  primary-fixed-dim: '#93ccff'
  on-primary-fixed: '#001d31'
  on-primary-fixed-variant: '#004b73'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.03em
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.005em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.02em
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-sm: 1rem
  margin: 2rem
  margin-sm: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The brand personality is encouraging, structured, and profoundly calm. Academic writing and post-graduate thesis preparation are fraught with imposter syndrome, decision paralysis, and cognitive overload. This design system strips away academic pedantry and cold institutional austerity, replacing them with a focused, supportive workspace inspired by the precision of Linear, the modular clarity of Notion, and the approachable organization of Airtable.

### Aesthetic Movement & Philosophy
The aesthetic aligns with **Clean Functional Minimalism with Warm Tactility**. It balances structural utility with humane comfort:
- **Calm, High-Clarity Workspace:** Soft, paper-tinted neutral surfaces eliminate eye strain over multi-hour synthesis sessions.
- **Supportive Mentorship Cues:** Visual affordances prioritize guidance over raw performance metrics, turning overwhelming milestones into digestible micro-actions.
- **De-escalated Complexity:** Interfaces avoid dense, high-friction toolbars. Features unfold contextually using subtle borders, gentle elevations, and clear typographic hierarchy.

## Colors

The palette is engineered for prolonged research focus, intentional pacing, and positive reinforcement. The color system uses warm whites, cool slate undertones, and purposeful semantic accents.

### Color Tokens & Roles
- **Canvas & Surface Base:**
  - `surface-canvas` (`#F8FAFC`): The ambient workspace foundation.
  - `surface-card` (`#FFFFFF`): Elevated content workspaces, cards, and active document sheets.
  - `surface-subtle` (`#F1F5F9`): Inactive panels, sidebars, table headers, and structural backgrounds.
- **Primary Accent (`#0284C7` - Clear Horizon Sky):** Directs the user’s cognitive focus. Applied to active draft states, primary execution buttons, progress milestones, and directional prompts.
- **Secondary Accent (`#10B981` - Sage Green):** Celebrates completion, accepted peer feedback, verified citations, and finished thesis sections. Never harsh or neon.
- **Tertiary Accent (`#F59E0B` - Warm Amber):** Reserved for coach annotations, contextual tips, methodology warnings, and nudge states. It feels like a reassuring highlighter margin note.
- **Neutral Stack (`#0F172A` to `#E2E8F0`):**
  - Text Primary: `#0F172A` (Deep Slate for effortless reading contrast).
  - Text Secondary: `#475569` (Subtle contextual labels and metadata).
  - Text Muted: `#94A3B8` (Placeholders and disabled markers).
  - Border Subdued: `#E2E8F0` (Card outlines, split dividers, and table borders).

## Typography

Typography prioritizes legibility and scannability during prolonged reading and writing sessions. `Plus Jakarta Sans` provides an approachable, geometric warmth for headers, body content, and document text, while `Inter` provides neutral, condensed structure for metadata, status tags, table cell data, and controls.

### Typographic Hierarchy
- **Editorial Headings:** Use tighter tracking (`-0.02em` to `-0.03em`) to anchor long section overviews, literature chapter breakdowns, and thesis drafts.
- **Reading Comfort:** `body-lg` and `body-md` maintain a generous `1.6` line-height ratio, preventing vertical fatigue when reviewing abstract summaries or methodology documentation.
- **Markdown Distinction:** Inline notes, quotes, and research citations employ distinct structural spacing: left-indented 3px amber borders for coach hints, and muted monospace treatments (`code-sm`) for citations and DOI IDs.

## Layout & Spacing

The layout follows a fluid-hybrid grid system built on an 8pt architectural rhythm, with a strict 4pt sub-grid for dense UI controls.

### Form Factors & Adaptation
- **Desktop (1024px and above):** 12-column layout with 24px (`1.5rem`) gutters and 32px (`2rem`) page margins. Utilizes a collapsible three-pane spatial model:
  1. *Navigation/Outline Rail:* 240px fixed width.
  2. *Active Drafting Sheet:* Max width 768px centered, replicating optimal reading line lengths (60–75 characters per line).
  3. *Coach & Context Drawer:* 320px contextual inspector for citation checks and AI prompts.
- **Tablet (768px – 1023px):** 8-column layout with 16px (`1rem`) gutters. Sidebars fold into an overlay sheet; the writing canvas retains priority.
- **Mobile (Below 768px):** 4-column layout with 16px (`1rem`) canvas margins. Panels stack vertically, switching secondary tools to bottom action sheets to preserve drafting surface area.

## Elevation & Depth

This system avoids aggressive, dark drop shadows. Visual depth is established primarily through **tonal surface layering**, complemented by soft **low-contrast outlines** and diffuse **ambient tinting**.

### Hierarchy of Depth
- **Level 0 (Canvas Base):** Plain `#F8FAFC`. Completely flat; houses structural navigation and inactive workspace panels.
- **Level 1 (Cards & Canvases):** Pure `#FFFFFF` surface resting on the canvas, bounded by a crisp 1px border (`#E2E8F0`). Shadow: `0px 1px 3px rgba(15, 23, 42, 0.04), 0px 1px 2px rgba(15, 23, 42, 0.02)`.
- **Level 2 (Dropdowns, Coach Callouts, & Popovers):** Elevated contextual elements. Crisp 1px border (`#CBD5E1`). Shadow: `0px 8px 16px -4px rgba(15, 23, 42, 0.06), 0px 2px 4px -1px rgba(15, 23, 42, 0.03)`.
- **Level 3 (Modals & Deep Focus Overlays):** Used for thesis defense simulations, file importers, and global search. Backed by a soft backdrop blur (`rgba(15, 23, 42, 0.25)` with `backdrop-filter: blur(4px)`). Shadow: `0px 20px 25px -5px rgba(15, 23, 42, 0.08), 0px 8px 10px -6px rgba(15, 23, 42, 0.04)`.

## Shapes

The design system uses a deliberate, rounded geometry that softens academic software's typical clinical stiffness without losing professional organization.

### Corner Radius Implementation
- **Standard Controls (Inputs, Buttons, Toolbars):** Set to 8px (`rounded-md`) for sharp, responsive interactions.
- **Cards, Panels, and Workspaces:** Set to 16px (`rounded-xl` / `1rem`), creating approachable, distinct module boundaries reminiscent of clean modern cards.
- **Pill Containers (Badges, Status Chips, Micro Avatars):** Fully rounded (9999px) to contrast against structured rectangular grids and instantly communicate metadata or progress.

## Components

### Buttons & Interactive Triggers
- **Primary Action (Sky Blue):** Background `#0284C7`, text `#FFFFFF`, radius 8px, height 40px (desktop) or 36px (compact). Hover transitions to `#0369A1` with an ambient primary-tinted glow (`0 2px 8px rgba(2, 132, 199, 0.2)`).
- **Secondary / Ghost:** Transparent background with 1px border `#E2E8F0`, text `#475569`. Hover shifts background to `#F1F5F9` and text to `#0F172A`.
- **Coach Action (Amber Nudge):** Soft background `#FEF3C7`, text `#92400E`, 1px border `#FDE68A`. Used specifically for contextual recommendations, prompt suggestions, and structural improvements.

### Badges & Plain-Language Status Chips
- Height 24px, pill-shaped (`rounded-full`), padding 2px 10px. Typography uses `label-sm`.
- **In Draft / Unstarted:** `#F1F5F9` background, `#475569` text, `#CBD5E1` border.
- **In Review / Progress:** `#E0F2FE` background, `#0369A1` text, `#BAE6FD` border.
- **Needs Attention / Coach Note:** `#FEF3C7` background, `#B45309` text, `#FDE68A` border.
- **Ready / Approved:** `#DCFCE7` background, `#15803D` text, `#BBF7D0` border.

### Input Fields & Search Bars
- Background `#FFFFFF`, 1px border `#CBD5E1`, radius 8px, height 40px, font `body-md`.
- **Focus State:** 1px border `#0284C7`, combined with an accessible 3px outer ring `#0284C7` at 15% opacity (`box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15)`).
- **Embedded Research Search:** Linear-inspired shortcut indicators on the trailing edge (e.g., `⌘K`) rendered in muted monospace badge styling.

### Cards & Content Modules
- Background `#FFFFFF`, 1px solid `#E2E8F0`, radius 16px (`rounded-xl`), inner padding 20px–24px.
- Hoverable workspace cards scale depth smoothly to Level 2 with a 1px border shift to `#CBD5E1`.

### Form Controls (Checkboxes & Radios)
- Size 18px by 18px. Radius 4px for checkboxes, full circle for radios.
- Unchecked: 1.5px border `#94A3B8`, background `#FFFFFF`.
- Checked: Background `#0284C7` (or `#10B981` in thesis milestone checklists), white centered check icon.

### Specialized Academic Modules
- **Coach Guidance Callout:** A contextual card with a subtle left accent edge (3px solid `#F59E0B`), warm ivory background `#FFFBEB`, and soft amber text hints explaining *why* a methodology section needs further citations.
- **Literature Progress Row:** Airtable-like condensed horizontal rows displaying paper title, publication year, assigned thesis chapter, and editable dropdown status badges with instant keyboard navigation.