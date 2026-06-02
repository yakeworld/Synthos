# uCT Data Landscape

## uCT数据有3个版本，路径不同用途不同

### 1. 裁剪版 ✅ (推荐使用)
路径: `UNet_Seg/Dataset/uCT/labels/{L,R}/`
每耳一个 nii.gz (269×269×269, ~0.05mm spacing)
62个文件 (31 L + 31 R) — 包括:
  - ALPHA-ZETA (希腊字母, 8个单耳标本)
  - F01-F15 (15个双侧标本, 30耳)
  - T01-T08 (8个双侧标本, 16耳)
  - EPSILON, ETA, GAMMA, THETA 仅L侧
  - ALPHA, BETA, DELTA, ZETA 仅R侧

### 2. 未裁剪版 ❌ (全颞骨,太大)
路径: `UNet_Seg/Dataset/Original uCT/labels/`
54个 nii.gz (792×792×370, 232M体素)
骨架化会耗尽内存, 不可直接处理。
需要先用nnUNet裁剪或提取ROI。

### 3. 原始ZIP版 (备用)
路径: `inner_ear_data/Human_Bony_Labyrinth/{F01-F14,T01-T08}.zip`
22个zip文件 (每标本含CT+uCT+DESC)
解压后可读, 但裁剪版更方便(已在不失真的前提下裁剪到最小包围盒)。

### 对应关系
- F01-F14 ≈ 裁剪版中的 F01-F14
- T01-T08 ≈ 裁剪版中的 T01-T08
- 希腊字母标本在zips中不存在(只有裁剪版有)
- F15存在于裁剪版但不在zips中

### 2026-05-29 发现
第一次跑时先找了 Human_Bony_Labyrinth/zip, 以为只有22标本。
用户指出 Dataset/Original uCT/labels/ 有54个文件。
进一步发现 Original 版太大跑不动, 最终用 Dataset/uCT/labels/ 裁剪版(62耳)。
教训: 优先查 Dataset/ 下各目录, 而非第三方数据目录。
