# PIL Color Format Gotchas

## RGBA CSS Strings FAIL

PIL's `ImageDraw` does NOT accept CSS `rgba(R,G,B,A)` strings:

```python
# WRONG — ValueError: unknown color specifier
draw.line([(0,0), (100,100)], fill='rgba(0,188,212,0.04)', width=1)
```

## Correct Approaches

### Opaque Colors (RGB mode image)

```python
# Pure opaque — use (R, G, B) tuples
draw.line([(0,0), (100,100)], fill=(0, 188, 212), width=1)
```

### Semi-Transparent (RGBA mode image)

```python
# For transparency, create image in 'RGBA' mode
img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.line([(0,0), (100,100)], fill=(0, 188, 212, 80), width=1)  # 80/255 alpha
```

### Solid Background with Opaque Overlay

```python
# Standard for competition covers — all opaque is fine
img = Image.new('RGB', (1920, 1080), (10, 22, 40))
draw = ImageDraw.Draw(img)
draw.line([(0,0), (100,100)], fill=(255, 255, 255), width=2)  # white line
```

## Color Palette Convention

For professional/tech covers:

| Role | RGB | Use |
|------|-----|-----|
| Background dark | (10, 22, 40) | Base fill |
| Background mid | (26, 58, 92) | Radial gradient center |
| Primary accent | (0, 188, 212) | Key highlights, titles |
| Secondary accent | (156, 39, 176) | Secondary elements |
| Warm accent | (255, 152, 0) | CTA elements |
| Text primary | (255, 255, 255) | Main text |
| Text secondary | (170, 170, 170) | Subtitles, labels |
| Grid subtle | (0, 188, 212) at low alpha | Background grid lines |

## Common Mistakes

1. Mixing `rgba()` string format with PIL → always use tuples
2. Creating RGB image but trying to use 4-tuple colors → switch to RGBA mode
3. Forgetting that `fill` and `outline` parameters both expect the same format
4. Using hex strings like `#00BCD4` in draw methods that expect tuples → actually PIL DOES accept hex strings for fill but NOT for line width/color specifications in all contexts