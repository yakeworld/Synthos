# 僵尸引用清理实战：3d-eyeball-iris-segmentation (2026-05-31)

## 场景
- **论文**: 3d-eyeball-iris-segmentation (3D Eyeball Model-Constrained Iris Segmentation)
- **引用模式**: 模式A — `.bib` 文件 (references.bib), `\bibliography{reference4}`
- **初始**: 55个bib条目, 28个被引用, 27个僵尸 → D10a ≈ 51%
- **最终**: 37个bib条目, 37个被引用 → D10a = 100%

## 决策框架

### Keep (新增 \cite{}, 9个)

| BibKey | 类别 | 插入位置 | 理由 |
|:-------|:-----|:---------|:-----|
| `garbin2019openeds` | 数据集原始论文 | Dataset Description段 | 论文使用OpenEDS数据集，必须引原始论文 |
| `palmero2020openeds2020` | 数据集挑战 | Dataset Description段 | OpenEDS 2020挑战论文 |
| `CASIA2019` | 数据集 | Iris Annotation Datasets段 | CASIA是标准基准数据集 |
| `proencca2005ubiris` | 数据集 | Iris Annotation Datasets段 | UBIRIS v1经典数据集 |
| `proencca2009ubiris` | 数据集 | Iris Annotation Datasets段 | UBIRIS v2经典数据集 |
| `daugman2001statistical` | 奠基文献 | Introduction 3处 | Daugman是虹膜识别奠基人 |
| `bowyer2008image` | 综述 | Iris Annotation Datasets段 | 虹膜生物特征综述 |
| `chen2017deeplab` | 方法 | Deep Learning段 | DeepLab分割架构 |
| `feng2022iris` | 方法 | Deep Learning段 | Iris R-CNN最新方法 |

### Delete (删除bib条目, 18个)

| BibKey | 删除理由 |
|:-------|:---------|
| `guestrin2006general` | 视线估计理论≠虹膜分割 |
| `huo2021heterogeneous` | 异质虹膜分割，不在scope |
| `kansal2019eyenet` | 通用，不增加信息 |
| `kim1999vision` | 过于陈旧 |
| `kuang2022towards` | 通用，不增加信息 |
| `lee2008fake` | 假体检测，不在scope |
| `lee20123d` | 3D视线追踪，不在此论文讨论范围 |
| `lu2016estimating` | 合成虹膜外观拟合，不直接相关 |
| `newman2000real` | 过于陈旧 |
| `nguyen2017long` | 远距离虹膜识别，不在scope |
| `nguyen2020constrained` | 虽然相关但未被any context支撑 |
| `tsukada2011illumination` | 光照子主题，不在scope |
| `tsukada2012automatic` | 自动虹膜，无具体上下文支撑 |
| `wang2019cross` | 交叉谱虹膜，不在scope |
| `wang2022light` | 轻量网络，未被讨论 |
| `bature2024iris` | 较新但非核心方法 |
| `dierkes2018novel` | ETRA会议论文，通用 |
| `dierkes2019fast` | ETRA会议论文，通用 |

## 执行流程

### Phase 1: 在正文中添加 \cite{}（先添加后删除，防止误伤）
```python
# 1. Daugman 2001 — 在Introduction 3处追加
\citep{daugman2009iris} → \citep{daugman2001statistical,daugman2009iris}

# 2. Dataset段追加多数据集引用
"Standard databases such as CASIA, UBIRIS, and OpenEDS"
→ "Standard databases such as CASIA~\citep{CASIA2019}, 
   UBIRIS~\citep{proencca2005ubiris,proencca2009ubiris}, 
   and OpenEDS~\citep{garbin2019openeds,palmero2020openeds2020,omelina2021survey},
   complemented by comprehensive surveys~\citep{bowyer2008image}."

# 3. Deep Learning段追加方法论文
\citep{nguyen2024deep} → \citep{chen2017deeplab,nguyen2024deep}
# 新增句子: "Feng et al. \citep{feng2022iris} proposed Iris R-CNN..."

# 4. Dataset Description段追加数据集原始论文
\citep{Sarker2021} → \citep{garbin2019openeds,Sarker2021}
"OpenEDS dataset" → "OpenEDS dataset\citep{palmero2020openeds2020}"
```

### Phase 2: 从.bib文件中删除僵尸条目
```python
zombies_to_delete = [
    'bature2024iris', 'dierkes2018novel', 'dierkes2019fast',
    'guestrin2006general', 'huo2021heterogeneous', 'kansal2019eyenet',
    'kim1999vision', 'kuang2022towards', 'lee2008fake', 'lee20123d',
    'lu2016estimating', 'newman2000real', 'nguyen2017long',
    'nguyen2020constrained', 'tsukada2011illumination', 'tsukada2012automatic',
    'wang2019cross', 'wang2022light'
]

# 用Python逐条目删除：找到 @article{key, 到 } 的块
# 注意：条目结束用 } 判断，但不能碰到嵌套括号（极少见）
```

### Phase 3: 修复 bib 文件路径（如适用）
```bash
# 当 \bibliography{reference4} 但实际文件在 06-references/references.bib
ln -sf 06-references/references.bib reference4.bib
```

### Phase 4: 编译验证
```bash
pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex
# 验证: 0 undefined errors, 32 pages, D10a=37/37=100%
```

## 关键教训

1. **先加cite后删bib**: 顺序很重要。先在正文中确认哪些条目值得保留（加\cite{}），再删除未激活的僵尸。反之会丢失需要保留的条目。
2. **数据集论文是最常见的"该keep僵尸"**: 在_mtodo迁移的论文中，CASIA、UBIRIS、OpenEDS等基准数据集的原始论文经常出现在bib中但未被引用。
3. **"9+18=37"启发式**: 对于55条目/28引用的初始状态，约1/3的僵尸该keep（加cite），约2/3该delete。可作为未来清理的参考比例。
4. **符号链接修复路径**: 迁移论文常有 `\bibliography{}` 路径与实际文件不匹配的问题。符号链接是最低侵入的修复方案。
5. **编译验证必须走完整链**: pdflatex → bibtex → pdflatex × 2，中间步骤不能省略。
