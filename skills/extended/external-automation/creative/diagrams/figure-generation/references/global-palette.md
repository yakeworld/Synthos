# Global Color Palette — Unified Entry Point

> All figure-generation skills must use colors defined here.
> No ad-hoc colors allowed. This file is the single source of truth.

## Nature Academic Palette (default)

```python
PALETTE = {
    # Primary color (proposed method)
    'blue_main':      '#0F4D92',  # Blue — main method
    'blue_secondary': '#3775BA',  # Blue — secondary method
    
    # Positive color (improvement/correct)
    'green_1': '#AADCA9',  # Light green — secondary positive
    'green_2': '#DDF3DE',  # Very light green — background/highlight
    'green_3': '#8BCF8B',  # Standard green — positive/correct
    
    # Baseline color (control/baseline)
    'red_1':   '#F6CFCB',  # Light red — baseline background
    'red_2':   '#E9A6A1',  # Medium red — baseline light
    'red_strong': '#B64342',  # Dark red — baseline/risk/error
    
    # Neutral colors
    'neutral_light': '#CFCECE',  # Light gray — background/reference
    'neutral_mid':   '#767676',  # Medium gray — auxiliary text
    'neutral_dark':  '#4D4D4D',  # Dark gray — secondary text
    'neutral_black': '#272727',  # Near black — primary text
    
    # Accent colors
    'gold':  '#FFD700',  # Gold — highlight
    'teal':  '#42949E',  # Teal — auxiliary accent
    'violet': '#9A4D8E',  # Violet — core contribution
    'magenta': '#EA84DD',  # Magenta — special annotation
}

DEFAULT_COLORS = ['#0F4D92', '#8BCF8B', '#B64342', '#42949E', '#9A4D8E', '#CFCECE']
```

## Nature NMI Soft Palette (paper/conference variant)

```python
PALETTE_NMI_PASTEL = {
    # Baseline family (cool, dark -> light)
    'baseline_dark':  '#484878',  # Dark blue-gray — strongest baseline
    'baseline_mid':   '#7884B4',  # Medium blue-gray
    'baseline_soft':  '#B4C0E4',  # Light blue-gray — weak baseline
    
    # Our method family (warm, small -> large contribution)
    'ours_tiny':  '#E4E4F0',
    'ours_base':  '#E4CCD8',
    'ours_large': '#F0C0CC',
    
    # Directional annotations
    'delta_up':   '#2E9E44',  # Green — improvement
    'delta_down': '#E53935',  # Red — degradation
}
```

## Dark Tech Palette (pil-image-generation only)

```python
PALETTE_DARK_TECH = {
    'bg':        '#0B1120',
    'card':      '#1E293B',
    'cyan':      '#00BCD4',
    'green':     '#34D399',
    'orange':    '#F59E0B',
    'red':       '#FF6B6B',
    'text':      '#F1F5F9',
    'gray':      '#94A3B8',
    'blue':      '#3B82F6',
}
```

## Semantic Rules (MUST obey)

| Color Semantics | Usage | Example |
|:----------------|:------|:--------|
| Blue | Proposed method | Our method = #0F4D92 |
| Green | Positive/change | delta_up = #2E9E44 |
| Red | Baseline/risk/error | Baseline = #B64342 |
| Gray | Reference/background/random | Random baseline = #999999 |
| Teal | Auxiliary accent | Annotation = #42949E |
| Violet | Core contribution | Core protocol = #9A4D8E |

## Color-blind Safety Rules

1. With >=3 colors, MUST check color-blind accessibility (see qa-architecture-diagram.py `check_color_blind_safe()`)
2. Red-green pair MUST NOT be the sole encoding — combine with line_style + marker
3. Grayscale readability: brightness difference >=0.15
4. No loss of distinguishability in color-blind simulation

## Font Constants

```python
FONT_FAMILY = ['Arial', 'DejaVu Sans', 'Liberation Sans']
FONT_SIZES = {
    'title':      9,
    'panel_label': 10,
    'axis_label':  8,
    'legend':      7,
    'tick':        7,
    'annotation':  6,
    'footer':      6,
}
```
