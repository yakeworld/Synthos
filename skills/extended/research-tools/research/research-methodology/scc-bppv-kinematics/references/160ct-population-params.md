# 160 Clinical CT Population Parameters (SCC 3D Logarithmic Spiral)

## Source
SCC Mathematical Morphology paper (submitted to Journal of Vestibular Research).
Table 1 (tab:ct_params) in the published manuscript.

## Data
- 80 subjects (160 ears), clinical temporal bone CT
- Voxel size: 0.49mm isotropic
- 3D UNet segmentation (Dice > 0.9), topology-preserving thinning for centerlines
- 475 successful fits out of 480 possible (99% success rate)

## Spiral Growth Rate |b| by Canal

| Canal | n | Mean | Median | SD | Range |
|:------|:-:|:----:|:------:|:--:|:-----:|
| AC (Superior) | 160 | 0.096 | 0.109 | 0.039 | [0.0002, 0.147] |
| PC (Posterior) | 156 | 0.032 | 0.017 | 0.039 | [0.0002, 0.158] |
| LC (Lateral) | 159 | 0.048 | 0.033 | 0.043 | [0.0003, 0.155] |
| **All** | **475** | **0.059** | **0.047** | **0.049** | **[0.0002, 0.158]** |

## Left-Right Symmetry (Cohen's d)

| Canal | d | Interpretation |
|:------|:-:|:--------------|
| AC | -0.250 | Small effect (left higher) |
| PC | 0.217 | Small effect (right higher) |
| LC | -0.071 | Negligible |

## Notes
- PC had 4 fewer fits (156 vs 160) due to incomplete segmentation in atypical anatomy
- Micro-CT reference specimens' |b| values fall within CT population distribution
- All parameters (a, A, ω, φ) available at specimen level; population means only available for |b|
- Raw per-subject CSV not saved independently — values embedded in paper Table 1 and analysis scripts
