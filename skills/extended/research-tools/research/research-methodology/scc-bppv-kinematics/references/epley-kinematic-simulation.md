# Epley Maneuver Kinematic Simulation

## Purpose
Simulate otoconia displacement during standardized repositioning maneuvers as a function of individual SCC morphological variation.

## Method

### Simplified Model
- Gravity-driven otoconia movement within SCC (constant gravity vector)
- No fluid dynamics, no cupula mechanics, no otoconia size/shape
- Tangential component of gravity along SCC centerline drives displacement
- Integration over maneuver positions gives total travel distance

### Maneuver Definition (Right Ear Epley)

| Position | Rotation | Description |
|:---------|:---------|:------------|
| P0 | Identity | Anatomical (upright, facing forward) |
| P1 | Yaw +45° about Z | Head turned 45° right |
| P2 | P1 + Pitch -105° about Y | Lie back, head 30° below horizontal |
| P3 | P2 + Yaw -90° about Z | Turn head 90° to left |
| P4 | P3 + Roll -90° about X | Roll onto left side |

All rotations in world coordinate frame (LPS: +X right, +Y anterior, +Z superior).
Gravity vector: g_world = [0, 0, -1]

### Rotation Sequence Code (Python)
```python
yaw_45 = rotation_matrix_z(math.pi/4)
R_pitch = rotation_matrix_y(-105*math.pi/180)
P2 = R_pitch @ yaw_45
yaw_m90 = rotation_matrix_z(-math.pi/2)
P3 = yaw_m90 @ P2
roll_m90 = rotation_matrix_x(-math.pi/2)
P4 = roll_m90 @ P3
maneuver = [I, yaw_45, P2, P3, P4]
```

## Population Results (160 CT scans, Monte Carlo n=10,000)

### Mean Otoconia Travel Distance

| Canal | Mean | SD | P5 | P95 | CV |
|:------|:---:|:--:|:--:|:---:|:--:|
| AC | 2.88mm | 1.07mm | 0.61mm | 4.46mm | 37% |
| PC | 0.56mm | 0.40mm | 0.04mm | 1.31mm | 72% |
| LC | 0.82mm | 0.54mm | 0.03mm | 2.01mm | 66% |

### Clinical Significance

| Canal | Inter-individual range | × Lumen diameter | Interpretation |
|:------|:---------------------:|:----------------:|:--------------|
| AC | 4.45mm | 11.1× | Most variable |
| PC | 2.11mm | 5.3× | Epley target, moderate |
| LC | 2.37mm | 5.9× | Supine roll target |

### Key Finding
- PC b-value (spiral tightness) correlates with travel distance
- Low b-value patients: Epley barely moves otoconia (~0.04mm)
- High b-value patients: Epley moves otoconia significantly (~1.3mm)
- Explains why some patients need multiple repositioning attempts

## Limitations
1. **No fluid dynamics**: Neglects endolymph viscosity, cupula stiffness, particle settling
2. **No otoconia properties**: Size (0.1-1mm), shape, density not modeled
3. **Constant gravity**: Doesn't model head movement dynamics (acceleration)
4. **Single maneuver**: Only Epley, not Semont/BBQ/barbecue
5. **Simplified SCC model**: No ampulla, no utricle connection modeling
6. **Normal distribution assumption**: b values sampled as truncated normal; actual distribution is right-skewed

## Future Improvements
- Couple with 3D finite element fluid dynamics
- Add particle size distribution
- Validate against patient outcome data (retrospective CT + BPPV outcome)
- Extend to Semont and Barbecue maneuvers
- Add ampullary geometry for cupula deflection estimation
