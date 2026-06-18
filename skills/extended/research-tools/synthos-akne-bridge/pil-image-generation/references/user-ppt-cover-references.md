# User's Existing Beautiful PPT Covers (Design References)

The user has several professionally designed competition PPTs in `~/下载/` (Downloads folder). All have full-image covers as slide 1. These represent the user's preferred design language.

## PPT Cover Inventory

| File | Slides | Cover Size | Notes |
|------|--------|------------|-------|
| `~/下载/4D_Edge_AI_Eye_Intelligence.pptx` | 12 | 1920×1080 full-image | 4D eye tracking AI |
| `~/下载/Spatial_Neural_Interface.pptx` | 15 | 1920×1080 full-image | Spatial neural interface |
| `~/下载/VOR_Digital_Twin_Decoding.pptx` | 14 | 1920×1080 full-image | VOR decoding |
| `~/下载/4D_VOR_Digital_Twin.pptx` | 15 | 1920×1080 full-image | 4D VOR twin |
| `~/下载/VOR_Digital_Twin.pptx` | 15 | 1920×1080 full-image | VOR digital twin |
| `~/下载/Precision_4D_Neuro-Vestibular_AI.pptx` | 15 | 1920×1080 full-image | Neuro-vestibular AI |
| `~/下载/AI_Vestibular_Digital_Twin.pptx` | 15 | 1920×1080 full-image | AI vestibular twin |

## How to Reference

Before generating any new cover for a competition/PPT:

1. Extract cover images from these PPTs for visual reference:
   ```python
   from pptx import Presentation
   prs = Presentation("~/下载/Spatial_Neural_Interface.pptx")
   slide = prs.slides[0]
   for shape in slide.shapes:
       if hasattr(shape, 'image'):
           img = shape.image
           with open('/tmp/reference_cover.png', 'wb') as f:
               f.write(img.blob)
           print(f"Reference cover: {img.content_type}, {len(img.blob)} bytes")
   ```

2. Analyze the visual style: color palette, layout density, typography, use of gradients/shapes

3. Match the aesthetic when generating the new cover (either HTML+Chromium or PIL)

## Design Style Notes (from these PPTs)

- All use full-image slide covers (no text-overlays on slide)
- Dark navy backgrounds with cyan/teal accents
- Futuristic/tech aesthetic with network/grid motifs
- Minimal text — title + subtitle only
- High contrast, clean typography
- 16:9 aspect ratio (1920×1080 or 17.78"×10")

## Usage

- `~/下载/*.pptx` — original PPT files (full presentations)
- Extract cover images via python-pptx (installed system-wide)
- Use as visual benchmark: "does my cover look as good as the user's existing PPT covers?"
