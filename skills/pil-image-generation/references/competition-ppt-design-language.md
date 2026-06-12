# Synthos Competition PPT Design Language

> Discovered: 2026-05-25
> Source: `Synthos_Full_Demo.pptx` (WPS backup)

## Visual Identity

| Token | Value | Notes |
|-------|-------|-------|
| Background | `#0F172A` (slate-900) | Very dark blue, solid fill |
| Card surface | `#1E293B` (slate-800) | Rounded rectangles with 1.5pt `#334155` border |
| **Accent** | **`#3B82F6` (blue-500)** | ⚠️ Not cyan/teal! Used for vertical accent bars (4.5pt wide, left-aligned) |
| Text primary | `#F8FAFC` (slate-50) | Bold Arial |
| Text secondary | `#06B6D4` (cyan-500) | Used for subtitle only |
| Text muted | `#94A3B8` (slate-400) | Body/description text |
| Font | Arial (system) | No custom fonts needed |
| Slide size | 13.33 x 7.5 inches (1280 x 720 px) | Standard 16:9 |

## Slide Structure Template

### Cover Slide (Slide 1)
- Background: `#0F172A` solid fill
- Accent: Left-aligned vertical `#3B82F6` bar (4.5pt wide, ~60% slide height)
- Title: "SYNTHOS" — Bold 54pt, `#F8FAFC`, Arial, centered
- Subtitle: "自主进化学术科研平台" — 22pt, `#06B6D4`, centered
- Tagline: Two-line centered text — 22pt, `#94A3B8`, line break between sentences

### Content Slide (Slides 2-9)
- Layout: Left accent bar + card grid
- Card: Rounded rectangle (`rx=6pt`), `#1E293B` fill, `#334155` 1.5pt border
- Card Header: Left accent bar (`#3B82F6`) + title text
- Content: White text on dark card, with alternating colors for emphasis
- Connecting arrows: Right-pointing auto shapes between steps

### End Slide (Slide 10)
- Similar to cover but simpler
- Centered "SYNTHOS" title
- Tagline + "感谢您的观看！"

## Color Assignments by Component

| Element | Fill | Text | Notes |
|---------|------|------|-------|
| Feature card | `#1E293B` | `#F8FAFC` (title), `#94A3B8` (body) | Rounded corners |
| Metrics number | transparent | `#3B82F6` | Large, bold |
| Metrics label | transparent | `#94A3B8` | Smaller, below number |
| Innovation card | `#1E293B` | `#F8FAFC` | Numbered 1-5 |
| Accent bars | `#3B82F6` | — | Thin vertical rectangles |

## Key Design Principles Observed

1. **Dark slate palette** (not black/navy, not cyan) — `#0F172A` base
2. **Blue accent (#3B82F6) as the single visual anchor** — used sparingly for vertical bars and metric numbers
3. **Clean card-based layout** — each slide section is a rounded rectangle card
4. **Minimal decoration** — no gradients, no glow effects, no grid patterns
5. **Left-aligned accent bars** — thin blue line on the left of cards
6. **System fonts** — Arial, no Google Fonts dependency

## Design vs PIL-Generated Cover

When generating a Synthos cover for the competition:

**If matching existing PPT style**: Use `#0F172A` background, `#3B82F6` accent blue (NOT `#00BCD4` cyan), Arial font, minimal decoration.

**If creating a standalone cover**: The user's current preference is cyan/teal (`#00BCD4`) with Linear-inspired dark theme — this is for a different visual identity (more modern, tech-forward) than the existing PPT. Match the context: use PPT-style for presentation materials, cyan style for standalone covers/marketing.
