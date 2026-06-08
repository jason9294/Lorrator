---
name: Lorrator
colors:
  surface: '#fbf9f5'
  surface-dim: '#dbdad6'
  surface-bright: '#fbf9f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3ef'
  surface-container: '#efeeea'
  surface-container-high: '#eae8e4'
  surface-container-highest: '#e4e2de'
  on-surface: '#1b1c1a'
  on-surface-variant: '#444748'
  inverse-surface: '#30312e'
  inverse-on-surface: '#f2f0ed'
  outline: '#747878'
  outline-variant: '#c4c7c7'
  surface-tint: '#5f5e5e'
  primary: '#171818'
  on-primary: '#ffffff'
  primary-container: '#2c2c2c'
  on-primary-container: '#949393'
  inverse-primary: '#c8c6c5'
  secondary: '#725b2f'
  on-secondary: '#ffffff'
  secondary-container: '#ffdea7'
  on-secondary-container: '#796135'
  tertiary: '#1a1526'
  on-tertiary: '#ffffff'
  tertiary-container: '#2f293c'
  on-tertiary-container: '#9890a7'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e4e2e1'
  primary-fixed-dim: '#c8c6c5'
  on-primary-fixed: '#1b1c1c'
  on-primary-fixed-variant: '#474747'
  secondary-fixed: '#ffdea7'
  secondary-fixed-dim: '#e1c28e'
  on-secondary-fixed: '#271900'
  on-secondary-fixed-variant: '#58431a'
  tertiary-fixed: '#e8def8'
  tertiary-fixed-dim: '#ccc2db'
  on-tertiary-fixed: '#1e192b'
  on-tertiary-fixed-variant: '#4a4458'
  background: '#fbf9f5'
  on-background: '#1b1c1a'
  surface-variant: '#e4e2de'
typography:
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 40px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Playfair Display
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.05em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.4'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1280px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 20px
  stack-xs: 4px
  stack-sm: 12px
  stack-md: 24px
  stack-lg: 48px
---

## Brand & Style

This design system embodies the persona of a **Modern Scholar of the Occult**. It moves away from traditional "gaming" aesthetics—characterized by heavy textures and distressed edges—in favor of a **Minimalist-Archival** approach. The goal is to make the user feel like an investigator organizing a high-stakes dossier on a digital interface that retains the tactile soul of a physical desk.

The brand personality is **Intellectual, Enigmatic, and Precise**. It balances the clean, functional efficiency of tools like Notion or Linear with the haunting, historical weight of a Lovecraftian mystery. The emotional response should be one of "calm intensity"—a professional environment where dangerous knowledge is systematically cataloged.

The visual style is a hybrid of **Minimalism** and **Tactile Archival**. It uses expansive whitespace (the paper), hairline borders (the ink), and purposeful monospaced typography (the typewriter) to create a sense of organized chaos.

## Colors

The palette is rooted in the materials of an investigator’s workspace.

- **Paper (Neutral):** `#FDFBF7` serves as the primary canvas. It is a warm off-white that reduces eye strain and mimics high-quality, acid-free archival paper.
- **Ink (Primary):** `#2C2C2C` is a deep charcoal used for all primary text and structural lines. It provides a stark, authoritative contrast against the paper.
- **Brass (Secondary):** `#A68B5B` acts as the primary highlight color. It represents the hardware of the era—brass clips, gold-leaf lettering, and aged compasses. Use this for interactive elements and key status indicators.
- **The Void (Tertiary):** `#4A4458` is a desaturated, deep purple used sparingly for "occult" accents, metadata, or hovering states over esoteric data points.

The system defaults to a **light mode** to maintain the "white paper" archival feel, though secondary surfaces may use the tertiary color to indicate "Forbidden Knowledge" sections.

## Typography

The typography strategy employs a three-font system to delineate information hierarchy:

1.  **Playfair Display (Serif):** Used for headlines and chapter markers. It evokes a sense of history, literary tradition, and elegance.
2.  **Inter (Sans-serif):** The workhorse for all body text and UI labels. It ensures maximum readability for long-form case files and investigator notes.
3.  **JetBrains Mono (Monospaced):** Used for technical data, coordinates, timestamps, and "encoded" information. It mimics the output of a manual typewriter or a mid-century cataloging system.

**Formatting Note:** Headlines should use "Title Case" for a formal look. Monospaced labels should often be in "ALL CAPS" with slight tracking to enhance the archival appearance.

## Layout & Spacing

This design system utilizes a **Fixed-Fluid Hybrid Grid**. Content is centered within a maximum width of 1280px to maintain the readability of a dossier, while the background "Paper" spans the full viewport.

- **Columns:** A 12-column grid for desktop, collapsing to 4 columns for mobile.
- **Margins:** Generous outer margins (64px) are used on desktop to create a "framed document" effect.
- **Rhythm:** An 8px base unit governs all padding and margins. Vertical rhythm is strictly enforced to ensure that rows of data align perfectly, similar to a ruled ledger.
- **Breakpoints:**
  - Desktop: 1024px+
  - Tablet: 768px - 1023px (Margins reduce to 32px)
  - Mobile: < 767px (Margins reduce to 20px)

## Elevation & Depth

In this design system, depth is conveyed through **Tonal Layering and Low-Contrast Outlines** rather than heavy shadows.

- **Surface Tiers:**
  - **Base:** The primary paper background (#FDFBF7).
  - **Mid:** Slightly darker tones or subtle paper-grain textures for sidebars and navigation panels.
  - **Top:** Pure white cards or panels with a 1px border in `#2C2C2C` at 10% opacity.
- **Outlines:** Instead of shadows, use 1px solid borders. For active elements, the border color shifts from a faint ink grey to the secondary Brass color.
- **Subtle Depth:** Where shadows are necessary (e.g., floating dossiers or context menus), use "Ambient Shadows"—diffused, low-opacity (#2C2C2C at 5%) with a zero-offset to mimic a sheet of paper laying flat on a desk.
- **Interactions:** Hover states should feel like a "highlight" rather than a "lift." Use a subtle background fill of `#A68B5B` at 5-10% opacity.

## Shapes

The shape language is **Structured and Precise**.

- **Corner Radius:** A universal 4px (Soft) radius is applied to cards, buttons, and input fields. This prevents the UI from feeling sharp and aggressive while avoiding the "playful" nature of fully rounded elements.
- **File Tabs:** Navigation elements use the "Folder Tab" shape—a rectangle with the top two corners rounded and the bottom corners sharp, mimicking the index tabs in a filing cabinet.
- **Dividers:** Horizontal and vertical lines must be 1px thick. Use dashed lines for "secondary" separations, suggesting a perforated edge.

## Components

### Buttons

Buttons are rectangular with a 4px radius.

- **Primary:** Solid `#2C2C2C` with `#FDFBF7` text. High contrast, authoritative.
- **Secondary:** Outlined with a 1px `#A68B5B` border and brass-colored text.
- **Ghost:** Monospaced text with a 1px dashed underline that becomes solid on hover.

### Dossier Cards

Used for investigator profiles or location summaries. They feature a 1px border, a generous 24px internal padding, and a "Stamp" in the top-right corner using the Tertiary "Void" color for status indicators (e.g., "Insane", "Missing").

### File Folder Tabs

Navigation is styled as horizontal tabs at the top of a container. Active tabs have a solid `#FDFBF7` background that "merges" into the container below, while inactive tabs have a slight grey tint.

### Typewriter Tables

Data tables should use `label-sm` (Monospaced) for all content. Borders are only used for horizontal rows to maintain a "ledger" look. Align numerical data to the right for a financial/accounting feel.

### Input Fields

Inputs are styled as "Form Blanks." They feature no background fill, only a bottom border of 1px. When focused, the border becomes the Secondary Brass color and a small Monospaced label floats above.

### Minimalist Icons

Icons must be ultra-thin (1px stroke), using geometric shapes. Avoid filled icons; stick to "line-art" style to maintain the ink-on-paper aesthetic.
