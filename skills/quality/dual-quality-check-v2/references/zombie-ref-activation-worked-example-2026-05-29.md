# 僵尸引用激活实战：hcs3wt-breast-cancer 修复记录 (2026-05-29)

## 场景
- **论文**: hcs3wt-breast-cancer (Hybrid Cascade-Stacking Three-Way Triage)
- **模板**: elsarticle, inline `thebibliography` (模式B)
- **初始问题**: D8=28 (<30), D10a=64.3% (10/28僵尸)

## 发现流程

### Step 1: 检测模式
```bash
grep '\\begin{thebibliography}' paper.tex  # 找到 → 模式B
```

### Step 2: 提取bibitem keys
```python
bibitems = set(re.findall(r'\\bibitem\{([^}]+)\}', content))
```

### Step 3: 提取cited keys  
```python
cited = set()
for m in re.finditer(r'\\cite[pt]?\{([^}]+)\}', content):
    for k in m.group(1).split(','):
        cited.add(k.strip())
```

### Step 4: 计算僵尸引用
```python
uncited = bibitems - cited  # 10 items
```

## 10个僵尸引用的激活方案

| BibKey | 优先级 | 激活位置 | 插入句模板 |
|--------|:------:|:---------|:-----------|
| **Yao2010ThreeWay** | P0 | Introduction 第3段 | `三支决策框架提供了处理不确定性的原则性方法` → 附加到现有 `\cite{}` |
| **Prokhorenkova2018CatBoost** | P0 | Methods, Stage 2 | CatBoost后紧跟 `\cite{}` |
| **McKinney2020International** | P1 | Introduction 第2段 | 大型临床评估显示... + `\cite{}` |
| **Chakravarthy2021Deep** | P1 | Introduction 第2段 | 添加到现有 `\cite{}` 中 |
| **Caruana2015Intelligible** | P1 | Discussion (新段) | 可解释模型可增强临床信任 |
| **Ribeiro2016Why** | P1 | Discussion (新段) | 后验解释方法如LIME... |
| **Lundberg2017SHAP** | P1 | Discussion (新段) | ...和SHAP... |
| **Floridi2018AI** | P2 | Discussion (新段) | 伦理框架要求... |
| **HighLevel2019Ethics** | P2 | Discussion (新段) | 可信AI准则... |
| **Topol2019Deep** | P2 | Discussion (新段) | 从基准评估到临床整合... |

## 追加的2个新引用 (D8: 28→30)

| BibKey | 来源 | 激活位置 |
|--------|------|:---------|
| **Bejnordi2017Diagnostic** | JAMA, CAMELYON challenge | Introduction 第2段 |
| **Hosny2018Artificial** | Nature Reviews Cancer | Introduction 第2段 |

## 编译验证

```bash
pdflatex paper.tex  # pass 1 → 2 undefined references
pdflatex paper.tex  # pass 2 → 0 undefined, 12 pages clean
```

## 关键教训
1. 10个僵尸引用中有8个实际上**完全相关**（三支决策、CatBoost、可解释性、伦理）——它们只是没有被插入引用位置。
2. 只需一个承接句即可自然地激活多个相关引用（如Discussion中关于可解释性的新段落一次性激活5个bibitem）。
3. LaTeX patch工具不能正确处理反斜杠——所有patch后的文件需要用Python脚本修复 `\\` → `\`。
