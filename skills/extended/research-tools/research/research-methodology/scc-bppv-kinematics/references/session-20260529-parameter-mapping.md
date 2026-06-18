# Session 2026-05-29: Bony→Membranous SCC Parameter Mapping

## Data Inventory

| Specimen | Modality | AC | PC | LC |
|:---------|:---------|:---|:---|:---|
| sp1_microct | micro-CT | bony+memb (44/106pts) | bony+memb (33/146pts) | bony+memb (19/95pts) |
| sp2_mrn | 7T MRI | bony+memb (39/81pts) | bony+memb (32/88pts) | bony+memb (23/78pts) |
| sp3_ict | ICT | bony+MEM1+MEM2(merged=90pts) | bony+MEM1+MEM2(merged=88pts) | bony+MEM (16/84pts) |

## All Fitted Log-Spiral Parameters

| Key | Type | a(mm) | b | A(mm) | ω | φ(°) | Arc(mm) | RMSE |
|:----|:-----|:-----:|:-:|:-----:|:-:|:----:|:-------:|:----:|
| sp1_microct_AC | bony | 3.64 | 0.096 | 0.278 | 2.45 | 35.5 | 13.58 | 0.133 |
| sp1_microct_AC | memb | 4.28 | -0.093 | 0.353 | 2.37 | 245.6 | 16.28 | 0.166 |
| sp1_microct_PC | bony | 3.13 | -0.019 | 0.261 | 2.25 | 281.8 | 16.18 | 0.271 |
| sp1_microct_PC | memb | 3.84 | -0.067 | 0.316 | 2.34 | 75.0 | 19.46 | 0.170 |
| sp1_microct_LC | bony | 2.89 | 0.005 | 0.208 | 2.49 | 265.2 | 12.65 | 0.174 |
| sp1_microct_LC | memb | 3.17 | 0.055 | 0.166 | 2.67 | 342.3 | 12.27 | 0.112 |
| sp2_mrn_AC | bony | 3.15 | -0.097 | 0.190 | 2.25 | 335.7 | 12.68 | 0.108 |
| sp2_mrn_AC | memb | 3.40 | -0.109 | -0.133 | 2.28 | 168.0 | 13.97 | 0.122 |
| sp2_mrn_PC | bony | 2.74 | 0.015 | 0.074 | 2.46 | 80.8 | 13.64 | 0.148 |
| sp2_mrn_PC | memb | 3.19 | -0.013 | 0.078 | 2.52 | 141.6 | 15.66 | 0.130 |
| sp2_mrn_LC | bony | 2.34 | -0.0001 | 0.121 | 2.29 | 288.0 | 9.96 | 0.159 |
| sp2_mrn_LC | memb | 2.79 | -0.109 | 0.143 | 2.46 | 6.4 | 12.51 | 0.167 |
| sp3_ict_AC | bony | 3.92 | 0.242 | 0.222 | 2.65 | 71.4 | 12.67 | 0.101 |
| sp3_ict_AC | memb* | 4.45 | 0.193 | -0.310 | 2.53 | 289.9 | 15.50 | 0.156 |
| sp3_ict_PC | bony | 3.62 | 0.122 | 0.133 | 2.48 | 92.8 | 13.68 | 0.101 |
| sp3_ict_PC | memb* | 3.62 | 0.012 | 0.201 | 2.25 | 147.4 | 15.15 | 0.142 |
| sp3_ict_LC | bony | 2.27 | 0.032 | 0.084 | 2.53 | 147.2 | 9.78 | 0.173 |
| sp3_ict_LC | memb | 2.85 | -0.022 | 0.108 | 2.56 | 106.1 | 13.58 | 0.203 |

*memb = MEM1+MEM2 merged

## Plane Angle Summary (after MEM1+MEM2 merge)

| Canal | n | Mean | SD | Median | Range |
|:------|:-:|:----:|:--:|:------:|:-----:|
| AC | 3 | 2.02° | 1.15° | 2.46° | [0.44, 3.15] |
| PC | 3 | 1.81° | 0.26° | 1.64° | [1.61, 2.17] |
| LC | 3 | 2.43° | 0.28° | 2.44° | [2.08, 2.76] |
| **All** | **9** | **2.08°** | **0.75°** | **2.17°** | **[0.44, 3.15]** |

- 89% within 3°
- 100% within 5°

## Parameter Mapping: Linear Models

| Param | r | p | Slope | Intercept | Id-MAE | Lin-MAE |
|:------|:-:|:-:|:-----:|:---------:|:------:|:-------:|
| a | 0.928 | 0.0003 | 0.948 | 0.592 | 0.433 | 0.170 |
| b | 0.756 | 0.0186 | 0.749 | -0.050 | 0.072 | 0.046 |
| arc | 0.825 | 0.0061 | 0.929 | 3.075 | 2.259 | 0.929 |
| A_s | 0.154 | 0.693 | — | — | 0.127 | 0.150 |
| ω | 0.520 | 0.151 | — | — | 0.110 | 0.092 |

## Centerline Mapping (Displacement Field): CV Results

| Test | AC RMSE | PC RMSE | LC RMSE |
|:-----|:-------:|:-------:|:-------:|
| Leave-out sp1 | 0.788 | 0.769 | 2.146 |
| Leave-out sp2 | 0.761 | 0.514 | 1.193 |
| Leave-out sp3 | 0.848 | 0.727 | 1.447 |
| **Mean** | **0.799** | **0.670** | **1.595** |

## H1 Monte Carlo Simulation (160CT population)

| Canal | Mean Travel | P5 | P95 | Range | ×Lumen |
|:------|:----------:|:--:|:---:|:-----:|:------:|
| AC | 2.88mm | 0.61 | 4.46 | 3.85mm | 11.1× |
| PC | 0.56mm | 0.04 | 1.31 | 1.27mm | 5.3× |
| LC | 0.82mm | 0.03 | 2.01 | 1.98mm | 5.9× |
