# 01-manuscript 符号链接陷阱 — 2026-06-18 3D Eyeball 实战

## 问题描述

v3 tex 文件编译报错 `File 'Figure_1' not found`、`File 'graphical_abstract' not found`。
但 `ls 05-figures/Figure_1.jpg` 确认文件存在。

## 根因

符号链接创建时使用了错误的相对路径深度。

**正确目录结构**：
```
media/yakeworld/sda2/Synthos/outputs/papers/
└── 3d-eyeball-iris-segmentation/       ← 论文根目录
    ├── 01-manuscript/                  ← 01-manuscript 是论文根目录的子目录
    │   ├── revision20241118v3.tex
    │   └── (图片符号链接应在此)
    ├── 05-figures/                     ← 05-figures 是论文根目录的子目录（与01-manuscript同级）
    │   ├── Figure_1.jpg
    │   ├── Figure_2.jpg
    │   ├── Figure_3.jpg
    │   └── graphical_abstract.pdf
    └── 06-references/                  ← 06-references 是论文根目录的子目录（与01-manuscript同级）
        ├── references.bib
        └── reference4.txt
```

**正确路径（从 01-manuscript/ 出发）**：
```bash
cd 01-manuscript/
ln -sf ../05-figures/Figure_1.jpg Figure_1.jpg
ln -sf ../05-figures/Figure_2.jpg Figure_2.jpg
ln -sf ../05-figures/Figure_3.jpg Figure_3.jpg
ln -sf ../05-figures/graphical_abstract.pdf graphical_abstract.pdf
ln -sf ../06-references/references.bib references.bib
ln -sf ../06-references/references.bib reference4
```

**错误路径（之前使用的）**：
```bash
ln -sf ../../05-figures/Figure_1.jpg Figure_1.jpg   # ❌ ../../ 指向 papers/ 目录
```

`../../` 从 `01-manuscript/` 会跳到 `papers/`（不是 `3d-eyeball-iris-segmentation/`），因为：
- `01-manuscript/..` = `3d-eyeball-iris-segmentation/`
- `01-manuscript/../../` = `outputs/papers/`

而 `outputs/papers/` 下没有 `05-figures/`。

## 修复步骤

1. 检查现有符号链接：`ls -la Figure_*.jpg graphical_abstract*`
2. 读取实际链接目标：`readlink Figure_1.jpg`
3. 验证目标存在：`ls -la ../05-figures/Figure_1.jpg`
4. 删除错误的符号链接：`rm -f Figure_1.jpg`
5. 创建正确的符号链接：`ln -sf ../05-figures/Figure_1.jpg Figure_1.jpg`
6. 验证：`ls -la Figure_1.jpg` 应显示 `-> ../05-figures/Figure_1.jpg`
7. 重新编译：`rm -f *.aux *.log *.bbl && pdflatex paper.tex`

## 通用规则

**规则：从 01-manuscript/ 到 05-figures/ 或 06-references/ 永远使用 `../`**

无论论文在 `outputs/papers/` 下的什么深度，01-manuscript 和 05-figures 永远在同一层级下（论文根目录的子目录）。

因此：
- `../05-figures/` — 永远正确
- `../06-references/` — 永远正确
- `../../05-figures/` — 永远错误（会跳一层到 papers/）

## 验证清单

修复后编译应满足：
- [ ] `grep -c "Error" paper.log` → 0
- [ ] `grep -c "undefined" paper.log` → 0
- [ ] `ls *.bbl` → 文件存在且 >0 字节
- [ ] PDF 包含所有图片（检查页面数和文件大小）
