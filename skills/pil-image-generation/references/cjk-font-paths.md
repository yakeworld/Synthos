# System CJK Font Paths

## Ubuntu/Debian (Noto CJK)

```
/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc
/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc
/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc
/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc

/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc
```

## Font Name for ImageFont.truetype()

```python
# Direct path (most reliable):
ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", size)

# Named (may vary by system):
ImageFont.truetype("Noto Sans CJK SC", size)   # Simplified Chinese
ImageFont.truetype("Noto Sans CJK TC", size)   # Traditional Chinese
ImageFont.truetype("Noto Sans CJK JP", size)   # Japanese
ImageFont.truetype("Noto Sans CJK KR", size)   # Korean
```

## Fallback Strategy

```python
def get_font(size, bold=False):
    for path in [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    try:
        return ImageFont.truetype("Noto Sans CJK SC", size)
    except:
        return ImageFont.load_default()  # Always have a fallback
```

## Other Distributions

| Distro | Font Package | Path |
|--------|-------------|------|
| RHEL/CentOS | google-noto-sans-cjk-fonts | `/usr/share/fonts/google-noto-sans-cjk/` |
| Fedora | google-noto-cjk-fonts | `/usr/share/fonts/google-noto-cjk/` |
| Arch | ttf-noto-cjk | `/usr/share/fonts/NotoSansCJK/` |
| Alpine | notofonts-cjk-ttf | `/usr/share/fonts/noto-cjk/` |

## Verify Available Fonts

```bash
fc-list :lang=zh family
```

## Notes

- `.ttc` files contain multiple fonts; PIL handles them automatically
- Size in pixels, not points. For high-res images (3000px+), use larger sizes (72-100 for titles)
- Bold variant: `NotoSansCJK-Bold.ttc`
- If bold is needed, load the Bold variant instead of relying on PIL's internal bold rendering