# MRI中心线提取验证（2026-05-29）

## 数据源

| 子集 | 路径 | 格式 | 体素数/例 | 弧长范围 | 推荐度 |
|------|------|------|:--------:|:--------:|:------:|
| **semical_lab_smooth** | `step2/evaluate/zhoumi/semical_lab_smooth/` | nii.gz | ~14K-15K | 4-13mm | ⭐ 首选 |
| semical_lab | `step2/evaluate/zhoumi/semical_lab/` | nii.gz | ~7.5K | 3-7mm | ⚠ 偏短 |
| eye_lab | `step2/evaluate/zhoumi/eye_lab/` | nii.gz | ~140K | 5-16mm | ❌ 混入前庭 |
| GLDcheck | `GLDcheck/MR*/LabelMapVolume_1.nrrd` | NRRD | ~15K | 需解析 | ⚠ NRRD需转换 |

## 15例试跑结果（semical_lab_smooth, v5管线, rejection_ratio=0.40）

| case | AC_mm | PC_mm | LC_mm | AC/PC分离 | 备注 |
|------|:-----:|:-----:|:-----:|:---------:|:----:|
| MR_065678 | 5.11 | 7.08 | 5.39 | ❌ 0.17mm | AC/PC合并 |
| MR_066107 | 6.86 | 3.91 | 8.72 | ❌ 0.82mm | AC/PC合并 |
| MR_066112 | 8.60 | 5.43 | 7.84 | ✅ 4.2mm | |
| MR_066575 | 10.73 | 5.92 | 5.12 | ✅ 2.6mm | |
| MR_066599 | 8.98 | 4.23 | 8.53 | ✅ 2.1mm | |
| MR_066605 | 12.00 | 7.53 | 2.64 | ✅ 2.9mm | LC偏短 |
| MR_066830 | 6.13 | 5.46 | 8.34 | ✅ 3.8mm | |
| MR_066876 | 7.97 | 6.86 | 7.97 | ✅ 3.1mm | |
| MR_066925 | 11.99 | 11.99 | 9.27 | ❌ 0.0mm | AC/PC合并 |
| MR_067729 | 8.97 | 9.19 | 2.39 | ✅ 1.5mm | LC偏短 |
| MR_067960 | 8.22 | 7.81 | 12.91 | ✅ 2.3mm | |
| MR_068294 | 12.90 | 8.70 | 7.75 | ✅ 3.9mm | |
| MR_068369 | 6.91 | 7.30 | 9.87 | ✅ 1.8mm | |
| MR_069381 | 7.48 | 9.02 | 2.92 | ✅ 2.2mm | LC偏短 |
| MR_069460 | 4.46 | 6.63 | 7.19 | ✅ 2.5mm | |

**成功率**: 15/15 (100%)
**AC/PC合并率**: 3/15 (20%) — 与其他模态一致
**LC偏短(<3mm)**: 3/15 (20%) — MRI分辨率限制

## 简化批量命令

```bash
# 单例测试
python3 -c "
import nibabel as nib
from clean_centerline import extract_centerlines
nii = nib.load('semical_lab_smooth/MR_XXXXXX_lab.nii.gz')
r = extract_centerlines(nii.get_fdata(), nii.header.get_zooms()[:3])
print(r.arc_lengths)
"

# 批量统计
for f in semical_lab_smooth/*.nii.gz; do
  python3 -c "import nibabel as nib, sys; from clean_centerline import extract_centerlines; nii=nib.load('$f'); r=extract_centerlines(nii.get_fdata(), nii.header.get_zooms()[:3]); print('$(basename $f)', r.arc_lengths)"
done
```
