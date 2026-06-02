# Competition Cover Generation with Pillow

> Quick reference for generating 1920x1080 competition covers using Python Pillow.

## Standard Layout

```
+--------------------------------------+
  (corner)              (corner)
     [ACQ]--[EXT]
       \   /           7-atom pipeline
      [ROU]            ACQ->EXT->...
       /   \
     [HYP]--[VER]

           Synthos
     自主进化认知操作系统
   A Self-Evolving ...

   53   0.98   18   80+
  进化  质量   吸收  技能
----------------------------------------
  AI for Medicine . 医学研究支持智能体
+--------------------------------------+
```

## Fonts (System CJK Paths)

| Font | Path | Best for |
|------|------|----------|
| Noto Sans CJK Bold | /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc | Titles >=30pt, mixed CJK+English |
| Noto Sans CJK Regular | /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc | Body text >=30pt |
| DroidSansFallbackFull | /usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf | CJK-only text under 32pt |

Pitfall: Noto TTC at <32pt produces faint anti-aliased glyphs. TTF (Droid) at <32pt renders English as extremely thin strokes. For mixed text under 32pt, use Noto Bold TTC and double-draw.

## Bold Text via Double-Draw

draw.text((x, y), "text", fill=(255,255,255), font=font)
draw.text((x+1, y), "text", fill=(255,255,255), font=font)

This increases bright pixels by ~34% without visible blur.

## Key Pitfalls

1. Blend creates new image - After Image.blend(), re-create ImageDraw.Draw referencing the new image.
2. No rgba CSS strings - Use (R, G, B) tuples or (R, G, B, A) for RGBA mode.
3. Pre-compute coordinates - Compute all hexagon positions in a first loop, draw in a second loop to avoid IndexError.
4. Metrics must match current system - Update hardcoded numbers (evolution_count, quality_score, absorption_count, skill_count) before generating. Check evolution-state.json for current values.
5. No personal info - No names, schools, or identifiable info in the cover image.
