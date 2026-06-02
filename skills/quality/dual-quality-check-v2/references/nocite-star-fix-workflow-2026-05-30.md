# `\nocite{*}` Fix Workflow — scale-space-canny 实战 2026-05-30

## 场景

论文 `scale-space-canny` (7页, LaTeX) 使用 `\nocite{*}` 强制将所有 40 条 `.bib` 条目包含进参考文献。实际在正文中手动 `\cite{}` 的仅 14 条，26 条从未在正文中被提及。

## 检测

```python
tex = open('article.tex').read()
import re
if '\\nocite{*}' in tex:
    print('DETECTED: nocite{*} in use')
    manual = set()
    for m in re.finditer(r'\\cite[pt]?\{([^}]+)\}', tex):
        for k in m.group(1).split(','):
            manual.add(k.strip())
    print(f'Manual cites: {len(manual)}')
    # Need to read bib separately to get total
```

## 分类策略

仅通过 `\nocite{*}` 纳入的 26 条分为三类：

### Px-REMOVE (11条) — 完全不相关，删除

| bibkey | 实际主题 | 理由 |
|--------|---------|------|
| `komodakis2008image` | 图像补全 (image completion) | 非边缘检测 |
| `ren2012labelme` | RGB-D 场景标注 | 非边缘检测 |
| `galasso2013unified` | 视频分割基准 | 非边缘检测 |
| `deng2009imagenet` | ImageNet 分类 | 太通用 |
| `he2016deep` | ResNet | 分割/分类通用架构 |
| `simonyan2015very` | VGGNet | 分割/分类通用架构 |
| `ronneberger2015u` | U-Net 分割 | 非边缘检测 |
| `badrinarayanan2017segnet` | SegNet 分割 | 非边缘检测 |
| `long2015fully` | FCN 分割 | 非边缘检测 |
| `weiss1999segmentation` | NCut 分割 | 非边缘检测 |
| `mairal2014online` | 稀疏建模 | 非边缘检测 |

### P1-KEEP (15条) — 相关，需插入手动 `\cite{}`

| bibkey | 推荐插入位置 | 上下文理由 |
|--------|-------------|-----------|
| `perona1990scale` | Introduction (L51) | 各向异性扩散，尺度空间奠基文献 |
| `meer1992edge` | Methods (L120) | 基于置信度的边缘检测 |
| `narendra1981comparison` | Introduction (L49) | 边缘检测器比较研究 |
| `ziou1998comprehensive` | Introduction (L51) | 边缘检测技术综述 |
| `marr1982vision` | Introduction (L49) | Marr 视觉计算经典著作 |
| `lindeberg1994scalebook` | Introduction (L53) | 尺度空间理论专著 |
| `puig2001multi` | Discussion (L229) | 基于Canny的多尺度边缘检测 |
| `sharif2019optimized` | Discussion (L229) | 优化的尺度空间滤波器 |
| `korada2022scale` | Discussion (L229) | 尺度空间曲率自适应边缘检测 |
| `roth2009fields` | Discussion (L223) | 图像先验模型 (Fields of Experts) |
| `dollar2006supervised` | Discussion (L238) | 边缘的监督学习 |
| `martin2001database` | Discussion (L238) | BSDS 数据库 |
| `he2020bidirectional` | Discussion (L242) | 双向级联边缘检测 |
| `wang2020deep` | Discussion (L242) | 深度学习边缘检测综述 |
| `acuna2019devil` | Discussion (L242) | 噪声标注下学习语义边界 |

### 新增条目 (1条) — OpenAlex 验证

| bibkey | 详情 | DOI |
|--------|------|-----|
| `ding2001canny` | Ding & Goshtasby, "On the Canny Edge Detector", Pattern Recognition 2001, 673引 | 10.1016/S0031-3203(00)00023-6 |

## 执行步骤

### Step 1: 删除 11 条不相关 bib 条目

```python
import re
with open('references.bib') as f: content = f.read()
remove_keys = ['komodakis2008image', 'ren2012labelme', 'galasso2013unified', 
               'deng2009imagenet', 'he2016deep', 'simonyan2015very', 
               'ronneberger2015u', 'badrinarayanan2017segnet', 'long2015fully',
               'weiss1999segmentation', 'mairal2014online']
for key in remove_keys:
    content = re.sub(r'@\w+\{' + re.escape(key) + r'.*?\n\}', '', content, 
                     flags=re.DOTALL)
with open('references.bib', 'w') as f: f.write(content)
```

### Step 2: 插入 16 条手动 `\cite{}`

使用 Python `str.replace()` 在自然上下文插入：

| 插入点 | 原始文本片段 | 新增引用 |
|--------|-------------|---------|
| L49 | `\cite{canny1986computational,marr1980theory}` | +`marr1982vision` |
| L49 | `good localization, and minimal response.` | +`~\\cite{narendra1981comparison}.` |
| L51 | `\cite{deriche1987using,haralick1984digital}` | +`,perona1990scale` |
| L51 | `generalizes across diverse imaging conditions` | +`~\\cite{ziou1998comprehensive,ding2001canny}` |
| L53 | `\cite{lindeberg1994scale,lindeberg1998feature}` | +`,lindeberg1994scalebook` |
| L120 | `\cite{lindeberg1998feature}` | +`,meer1992edge` |
| L223 | `...changes with viewing resolution.` | +`~\\cite{roth2009fields}.` |
| L229 | `\cite{lindeberg2013scale}` | +`,puig2001multi,korada2022scale,sharif2019optimized` |
| L238 | `\cite{arbelaez2011contour}` | +`,martin2001database` |
| L238 | `\cite{dollar2015fast,xie2017hed,liu2017rcf}` | +`,dollar2006supervised` |
| L242 | 深度学习方法段落 | +`~\\cite{he2020bidirectional,wang2020deep,acuna2019devil}` |

### Step 3: 删除 `\nocite{*}` 行

```python
tex = tex.replace(
    '% Include all references in the bibliography for comprehensive coverage\n\\nocite{*}',
    '% All references are now manually cited in the text'
)
```

### Step 4: 编译验证

```bash
cd paper-dir/
rm -f article.aux article.bbl article.blg
pdflatex -interaction=nonstopmode article.tex
bibtex article
pdflatex -interaction=nonstopmode article.tex
pdflatex -interaction=nonstopmode article.tex
# Verify: grep 'undefined' article.log | grep -v 'may have changed'
```

## 结果

| 指标 | 修复前 | 修复后 |
|:-----|:------:|:------:|
| Bib 条目 | 40 | 30 |
| 手动 `\cite{}` | 14 (35%) | 30 (100%) |
| `\nocite{*}` | 使用中 | 已删除 |
| 编译页数 | 7p, 275KB | 7p, 276KB |
| 编译错误 | 0 | 0 |
| undefined citations | 0 | 0 |
| D10a | 100% (虚高) | 100% (真实) |

## 鉴别原则

`\nocite{*}` 不总是错误的——当论文引用大量概念性背景文献（教科书、综述）且不便每次出现都加 `\cite{}` 时，少量使用可接受。问题在于**引用列表中大部分条目从未被正文提及**。

快速判定：`手动 \cite{} 条目数 < bib 条目数的 50% → 必须修复`。

## 后续轮次可继续

- 补充 refs-md/ 参考 PDF（D9 提升）
- BSDS500 基准评估（D3 提升）
- 生成稳定性图/边缘图作为图片（D5 提升）
