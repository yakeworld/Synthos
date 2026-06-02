# Nature-Approved Color Palettes

## 6-Color Blind-Safe Palette (Print + Screen)

From Nature's official Final Artwork Guidelines. Safe for color-blind readers
and CMYK printing.

| Name | Hex | RGB | CMYK | Use |
|------|-----|-----|------|-----|
| Blue | `#0072B2` | (0,114,178) | (100,36,0,30) | Primary/hero method |
| Orange | `#E69F00` | (230,159,0) | (0,31,100,10) | Secondary method |
| Green | `#009E73` | (0,158,115) | (100,0,27,38) | Positive/improvement |
| Pink | `#CC79A7` | (204,121,167) | (0,41,18,20) | Highlight/accent |
| Brown | `#D55E00` | (213,94,0) | (0,56,100,16) | Baseline/reference |
| Gray | `#999999` | (153,153,153) | (0,0,0,40) | Neutral/background |

## 9-Color Extended Palette (for complex figures)

| Name | Hex |
|------|-----|
| Blue | `#0072B2` |
| Orange | `#E69F00` |
| Green | `#009E73` |
| Pink | `#CC79A7` |
| Brown | `#D55E00` |
| Gray | `#999999` |
| Sky Blue | `#56B4E9` |
| Yellow | `#F0E442` |
| Purple | `#8830B0` |

## NMI Pastel Family (Nature Machine Intelligence style)

| Name | Hex | Use |
|------|-----|-----|
| Blue main | `#0F4D92` | Hero method |
| Blue secondary | `#3775BA` | Second method |
| Green light | `#DDF3DE` | Positive gradient 1 |
| Green mid | `#AADCA9` | Positive gradient 2 |
| Green | `#8BCF8B` | Positive gradient 3 |
| Red light | `#F6CFCB` | Baseline gradient 1 |
| Red mid | `#E9A6A1` | Baseline gradient 2 |
| Red strong | `#B64342` | Baseline |
| Teal | `#42949E` | Accent |
| Violet | `#9A4D8E` | Accent |
| Gold | `#FFD700` | Callout |
| Neutral mid | `#767676` | Background text |
| Neutral dark | `#4D4D4D` | Axis labels |
| Neutral black | `#272727` | Primary text |

## TikZ Color Definitions

```latex
% ===== Nature 6-color palette =====
\definecolor{nat_blue}{HTML}{0072B2}
\definecolor{nat_orange}{HTML}{E69F00}
\definecolor{nat_green}{HTML}{009E73}
\definecolor{nat_pink}{HTML}{CC79A7}
\definecolor{nat_brown}{HTML}{D55E00}
\definecolor{nat_gray}{HTML}{999999}

% ===== NMI Pastel =====
\definecolor{nmi_blue}{HTML}{0F4D92}
\definecolor{nmi_blu2}{HTML}{3775BA}
\definecolor{nmi_teal}{HTML}{42949E}
\definecolor{nmi_viol}{HTML}{9A4D8E}
\definecolor{nmi_gold}{HTML}{FFD700}
\definecolor{nmi_reds}{HTML}{B64342}
\definecolor{nmi_neut}{HTML}{767676}
```

## Color Rules

1. **One family per figure** — pick Nature 6-color OR NMI pastel, not both
2. **Light fill + dark text** — `fill=COLOR!10, text=COLOR!90!black` for maximum contrast
3. **Max 6 distinct colors** — color-blind readers can distinguish up to 6-8, not more
4. **Consistent semantics** — blue=proposed method everywhere, gray=background everywhere
5. **Avoid saturated fills** — use `!8` to `!15` opacity for fill, never 100%
6. **Spine/line colors** — use `black!40` for layer boundaries, `black!25` for subtle boxes
