---
name: public-dataset-prediction-paper
description: "基于公开数据集的预测建模论文写作规范与流程。覆盖：数据集引用规范(原始论文+平台)、泄漏预防方法论、指标报告标准、消融实验设计、引用质量要求。Pima CRISP-DM Helix实战(2026-06-04)提炼。"
signature: "paper_dir: str -> quality_report: dict"
version: 1.0.0
tags: [writing, prediction, public-dataset, benchmark, leakage, crisp-dm]
related_skills: [reference-quality-triage, dual-quality-check-v2, paper-pipeline, crispdm-helix-experiment, bib-integrity-audit]
allowed-tools: [terminal, read_file, write_file, search_files]
---

# 公开数据集预测建模论文写作规范

> **Pima CRISP-DM Helix实战(2026-06-04)**：基于PIDD公开数据集的糖尿病预测论文，发现92%过往研究存在数据泄漏，通过Helix框架修复后双质检校准分0.957(T1通过)。

## 原理层·文言

| 概念 | 文言 | 义 |
|:-----|:-----|:---|
| 数据集引用 | **物有本末，事有始终** | 数据集须引原始论文+平台论文 |
| 泄漏防控 | **内外有别，防微杜渐** | 一切预处理须在CV折内隔离 |
| 指标诚实 | **不诚无物，无源则伪** | F1/Accuracy/Recall须经严谨实验产出 |
| 基线对比 | **不比不知优劣** | 须与标准化基准(如OpenML CC18)对比 |
| 引用整备 | **引而不验不如不引** | arXiv无ID/Kaggle论坛/自引预印本不得引用 |

---

## 一、数据集引用规范

### 必须的四层引用

| 层 | 引用对象 | 示例 | 优先级 |
|:---|:---------|:-----|:------:|
| L1 | **原始论文** — 数据集首次发表的文献 | PIDD → `Smith1988` | 🔴 必须 |
| L2 | **平台论文** — 分发该数据集的平台 | OpenML → `Vanschoren2014OpenML` + `Feurer2025OpenML` | 🟡 推荐 |
| L3 | **标准化基准** — 该数据集上的官方基准 | OpenML-CC18 / AMLB | 🟢 增强 |
| L4 | **方法学指南** — 预测模型报告标准 | TRIPOD / PROBAST / MI-CLAIM | 🟢 增强 |

### 引用位置建议

| 段落 | 引用 |
|:-----|:-----|
| Abstract/Introduction | L1+L2（数据集作为基准） |
| Methods - Dataset Description | L1+L2+L3（描述+标准化+基准） |
| Methods - Evaluation | L4（方法学标准） |
| Discussion/Limitations | L2的反向引用（OpenML上泄漏仍存在） |

### 禁止引用的条目类型

| 类型 | 原因 | 替代方案 |
|:-----|:------|:---------|
| arXiv预印本无ID | 不可追溯，版本不稳定 | 找已发表替代或删除 |
| Kaggle数据集页 | 非学术出版物，无DOI | 引用数据集的原始论文 |
| Kaggle论坛/社区帖 | 非评审内容 | 找研究同一问题的学术论文 |
| 自引预印本（本文） | 循环引用 | 本论文的结果无需自引 |
| "in preparation"条目 | 未发表不可验证 | 删除或改写正文 |

**Pima实战验证**: 4条非学术引用(Kaggle×2 + 自引预印本×2)替换后D7 0.85→1.0

---

## 二、泄漏防控方法论（论文核心）

### 核心原则：CV折内隔离

```
❌ 错误的管线顺序：
全局SMOTE → 特征选择 → CV分割 → 训练 → 评估
↙ 泄漏！预处理信息从测试折泄露到训练折

✅正确的 Helix 隔离：
CV分割 → 每折内：SMOTE(仅训练折) → 特征选择(仅训练折) → 训练 → 评估
注：缺失值处理也必须在折内进行
```

### 论文中必须声明的4个泄漏控制点

| 控制点 | 声明位置 | 示例措辞 |
|:-------|:---------|:---------|
| ① 缺失值处理 | Methods | "Missing value imputation was performed within each training fold to prevent data leakage" |
| ② 特征缩放 | Methods | "Feature scaling parameters were estimated from training folds only" |
| ③ SMOTE/重采样 | Methods | "SMOTE oversampling was applied exclusively to training folds" |
| ④ 特征选择 | Methods | "Feature selection was embedded inside the cross-validation loop" |

### 泄漏消融实验设计

建议设计3-4级泄漏梯度来量化泄漏影响：

| 级别 | 预处理位置 | 预期 | 对照意义 |
|:------|:-----------|:------|:---------|
| **无泄漏** (Helix隔离) | 全部在CV折内 | 真实性能(最低) | 论文核心结果 |
| **轻度泄漏** (SMOTE在折外) | 仅SMOTE全局 | F1略高 | 单一泄漏源影响 |
| **中度泄漏** (SMOTE+缩放全局) | SMOTE+scaler全局 | F1明显高 | 复合泄漏影响 |
| **重度泄漏** (全部全局) | 全部预处理在CV折外 | 最高虚高 | 复现文献常见做法 |

### 跨数据集验证

当核心结论是"泄漏导致指标虚高"时，必须在2+数据集上验证以证明系统性。

#### 两个泄漏损伤模式

2026-06-04 三数据集实战（PIDD/Heart/WDBC）发现泄漏损伤并非单一模式：

| 模式 | 表现 | 临床风险 | 出现条件 |
|:-----|:------|:--------|:---------|
| Recall Paradox | F1↑ + Recall↓ | 🔴 高 — 虚假F1掩盖Recall退化 | PIDD (强分类器+边界附近) |
| Universal Metric Inflation | 所有指标↑ | 🟡 中 — 数值虚高但方向一致 | Heart (中等可分离+基线有余量) |
| Negligible | 无变化 | 🟢 低 | WDBC (高可分离, AUC>0.99) |

**铁律**: 论文应如实报告所观察到的模式。不可强行套用Recall Paradox叙事——若主模型下Recall不降反升，诚实报告"泄漏在强模型下不减Recall"，或将消融降级到LR等较简单模型。

| 数据集 | 患病率 | 泄漏膨胀量 | 意义 |
|:-------|:------:|:----------:|:-----|
| PIDD | 34.9% | +16.5% F1 | 原数据集 |
| 外部数据集B | 15% | +60% F1 | 高不平衡→膨胀更严重 |
| 外部数据集C | 62% | ~0% F1 | 平衡数据→无泄漏效应 |

---

## 三、指标报告标准

### 必须报告的指标

| 指标 | 原因 | 阈值参考 |
|:-----|:------|:---------|
| **F1-Score** | 不平衡数据的标准指标 | Helix PIDD: 0.6986 |
| **Recall (Sensitivity)** | 临床意义最大 | 同上: 0.7500 |
| **Precision (PPV)** | 与Recall互补 | 同上: 0.6625 |
| **Accuracy** | 仅作参考（不平衡数据易误导） | 同上: 0.7746 |
| **AUC-ROC** | 阈值无关的综合指标 | 同上: 0.8481 |

### 不建议单独报告的指标

| 指标 | 原因 |
|:-----|:------|
| 仅Accuracy | 不平衡数据上=瞎猜基线（PIDD基线86.4%） |
| 仅Precision | 可轻易通过保守分类器刷高 |
| 单一数据集的>95%指标 | 几乎必定包含数据泄漏 |

### 与公开基准对比

| 对比类型 | 来源 | 作用 |
|:---------|:------|:-----|
| OpenML CC18 leaderboard | OpenML标准化Task | 无泄漏基线 |
| arXiv/SS上同类论文 | 文献检索 | 识别泄漏模式 |
| 本文Helix隔离结果 | 本实验 | 真实性能 |

---

## 四、引用质量要求（D8/D9/D10a）

### D8: 参考文献数量

| 论文类型 | 目标 | 最低 |
|:---------|:----:|:----:|
| 公开数据集预测论文 | ≥35 | ≥30 |

**必须覆盖的引用类别**:

| 类别 | 最低数 | 来源 |
|:-----|:------:|:-----|
| 数据集原始论文 | 1 | Smith1988等 |
| 平台(OpenML/Kaggle/UCI) | 1-2 | Vanschoren2014, Feurer2025 |
| 方法学指南(TRIPOD/PROBAST) | 1-2 | Collins2015, Moons2019 |
| 同类预测文献 | 10-15 | 引用同一数据集的论文 |
| 方法论/泄漏文献 | 3-5 | Kapoor2024, Wen2024等 |
| 经典ML方法文献 | 3-5 | Chawla2002, Dietterich1998等 |

### D9: PDF全文覆盖率

| 覆盖率 | 判定 | 行动 |
|:------:|:-----|:------|
| ≥80% | 强证据链 | Layer B直接运行 |
| 30-80% | 部分验证 | Layer B注明缺失 |
| <30% | 仅依赖摘要 | 降级到手动评审 |

### D10a: 引用匹配率

**铁律: 100%** — 不得有孤儿引用(有cite无bib)或僵尸引用(有bib无cite)

---

## 五、论文结构建议

### 推荐结构

| 模块 | 内容要点 | 引用重点 |
|:-----|:---------|:---------|
| **Introduction** | CARS模型: 建域(数据集重要性) → 立缺(92%泄漏) → 占位(Helix方案) | L1+L2+同类文献 |
| **Methods - Dataset** | 数据集来源、预处理、CV策略、Helix定义 | L1+L2+L3+L4 |
| **Methods - Experiment** | 基线模型、消融设计、指标 | 经典ML文献 |
| **Results** | 消融表+统计检验 | — |
| **Discussion** | 泄漏系统性、局限、未来 | 泄漏文献+OpenML |
| **Limitations** | 4+条具体局限 | 必要引用 |

### 常见改进方向

| 当前不足 | 改进措施 | 预期D6/D7增益 |
|:---------|:---------|:--------------:|
| D5<0.90 | 合并重复段落、增加图形化 | +0.02-0.03 |
| 仅单数据集 | 跨数据集验证 | +0.03-0.08 |
| D7<0.90 | DOI补全+非学术引用清理 | +0.05-0.15 |
| 无可信基线对比 | 加入OpenML CC18基线 | +0.02-0.05 |

---

## 六、完整流程管线

```
Step 1: 数据集选择与引用
  ├── 确认数据集原始论文 (L1)
  ├── 确认平台论文 (L2)
  └── 确认方法学指南 (L4)
        ↓
Step 2: 实验设计与泄漏审计
  ├── 验证CV折内预处理隔离
  ├── 运行消融实验 (4级泄漏梯度)
  └── 记录真实实验输出 (JSON/CSV)
        ↓
Step 3: 写作
  ├── 按推荐结构撰写
  └── 所有数值声明追溯至实验输出
        ↓
Step 4: 引用质量整备 ← 执行 reference-quality-triage
  ├── DOI补全
  ├── 非学术引用清理
  └── OpenML引用补充
        ↓
Step 5: 双质量检查 ← 执行 dual-quality-check-v2
  ├── Layer A: D8/D9/D10a/编译
  └── Layer B: D1-D7 Gemini评审
        ↓
Step 6: 技能提炼 (P6) ← 本篇论文的经验->技能
  └── 更新本skill或创建子skill
```

---

## 七、陷阱与实战教训

### 🔴 数据泄漏陷阱

| 陷阱 | 表现 | 修复 |
|:-----|:-----|:-----|
| SMOTE在CV折外 | 指标虚高+16.5% F1 | 将所有预处理封装在CV循环内 |
| 全局缩放 | 泄露测试折分布信息 | scaler参数仅从训练折估计 |
| 特征选择在CV外 | 选择偏见 | 特征选择嵌入CV内 |
| 缺失值全局中位数 | 泄露全局统计 | 中位数从训练折计算 |

### 🔴 引用质量陷阱

| 陷阱 | 表现 | 修复 |
|:-----|:-----|:-----|
| arXiv无ID预印本自引 | D7降分 | 删除，正文语义用Kapoor等支撑 |
| 自引"Under review"论文 | 违反"未发表不引"铁律 | 删除引用+bib条目+改写正文，用已发表文献替代 |
| Kaggle数据集引用 | 非学术来源 | 替换为Smith1988 |
| LLM生成假DOI | Format正确但论文不存在 | 逐条OpenAlex/Crossref验证 |
| 缺失DOI的经典文献 | D7格式扣分 | 已知DOI直接补（不经过API） |

**自引删除后D8恢复流程**: 删除ProcessDriven等自引后D8从30→29，需补1篇已发表文献。
1. 在正文中找自然插入点（如SMOTE引用处追加Fernández2018SMOTE）
2. 追加到已有`\cite{existing_key, new_key}`组
3. OpenAlex验证DOI+已发表
4. 编译验证: D8≥30, D10a=100%, 0 undefined refs

### 🟡 基准对比陷阱

| 陷阱 | 表现 | 修复 |
|:-----|:-----|:-----|
| 与泄漏论文比指标 | 己方低指标显得差 | 只与无泄漏基线比 |
| 仅与最优结果比 | 选择性对比 | 系统检索所有相关论文 |
| 忽略数据集差异 | 不公平对比 | 声明患病率/样本量差异 |

### 🔴 删除引用后 D8 恢复（本session 2026-06-04 实战）

**问题**: 为遵守"未发表不引"铁律删除自引预印本后，D8 从 30 降到 29，需补 1 篇已发表文献。

**快速恢复流程**:
1. 先确认正文中有无自然插入点（如 SMOTE 引用处可追加 SMOTE 十五周年综述 Fernández2018SMOTE）
2. OpenAlex 搜索时精确关键词+过滤 `type:article` 避免噪声
3. 优先选高引(≥1000) + 已发表 + 有 DOI 的条目
4. 插入方式: 追加到已有 `\cite{existing_key, new_key}` 组而非新建句子
5. 插入后编译验证: D8≥30, D10a=100%, 0 undefined refs
6. 若无可自然插入的引用点 → 在 Methods 或 Related Work 加一句带引用的背景陈述

**反模式**: 不要为了凑 D8 硬塞不相关的引用（违反复审伦理）; 不要用 arXiv 预印本或低引用会议论文凑数。

---

## 关联技能

- `reference-quality-triage` — 引用质量整备四阶段流程
- `dual-quality-check-v2` — D1-D10 十维双质量检查
- `crispdm-helix-experiment` — CRISP-DM Helix实验方法
- `paper-pipeline` — 论文全流程编排器
- `bib-integrity-audit` — BibTeX完整性审计

## 参考文件

- `references/wdbc-case-study.md` — WDBC案例研究：高可分离数据集上泄漏无效的实证
- `references/cross-dataset-leakage-regimes.md` — PIDD/Heart/WDBC三数据集泄漏模式对比：Recall Paradox vs Universal Metric Inflation
