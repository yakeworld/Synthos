# 图尔敏论证模型分析器

> 理论来源：Toulmin (1958) "The Uses of Argument"

## 图尔敏模型定义

Toulmin 论证模型是论证分析的黄金标准。每个完整的学术主张包含 6 个要素：

```
┌─────────────────────────────────────────────────────┐
│                    Claim (主张)                       │
│            "本研究证明了 X 能改善 Y"                  │
└────────────────┬────────────────────────────────────┘
                 │ supports
                 ▼
┌─────────────────────────────────────────────────────┐
│                Warrant (推理规则)                      │
│   "既往文献表明 X 通过机制 M 影响 Y"                   │
└──────┬──────────────────────────────────────────────┘
       │ justified by
       ▼
┌─────────────────────────────────────────────────────┐
│                Data (数据/证据)                       │
│   "实验组 Y 提升 23%, p<0.01, n=120"                 │
└──────┬──────────────────────────────────────────────┘
       │ grounded in
       ▼
┌─────────────────────────────────────────────────────┐
│                Backing (支撑)                          │
│   "机制 M 已在 3 项独立研究中验证 (Ref A, B, C)"       │
└──────┬──────────────────────────────────────────────┘
       │ qualified by
       ▼
┌─────────────────────────────────────────────────────┐
│              Qualifier (限定词)                        │
│   "在特定条件下" / "很可能" / "统计学上显著"            │
└──────┬──────────────────────────────────────────────┘
       │ except when
       ▼
┌─────────────────────────────────────────────────────┐
│              Reservation (例外)                        │
│   "不适用于共病患者群体" / "长期效果未知"               │
└─────────────────────────────────────────────────────┘
```

## 自动化分析规则

### 要素检测规则

| 要素 | 必须包含 | 检测模式 |
|------|----------|----------|
| **Claim** | 明确的主张陈述 (非隐含) | "we demonstrate", "our results show", "X increases" |
| **Data** | 具体数据/证据支撑 | 数字、统计值 (p, n, CI, r, t, F)、引用文献 |
| **Warrant** | 推理规则 (为什么 Data→Claim) | "because", "since", "this suggests", "by mechanism" |
| **Backing** | 支撑推理规则的依据 | 引用、前序实验、理论基础 |
| **Qualifier** | 条件/强度限定 | "likely", "possibly", "in this context", "under" |
| **Reservation** | 适用范围/例外 | "except", "limitation", "not applicable to" |

### 合格标准

```
必须同时满足:
1. Claim 必须出现 (不能隐含)              → 否则 FAIL
2. Data 必须出现且包含至少 1 个具体数值      → 否则 FAIL  
3. Warrant 必须建立 Data→Claim 的逻辑链     → 否则 WARNING
4. Qualifier 必须出现                       → 否则 WARNING
5. 完整链路 Data→Warrant→Claim 不能断裂     → 否则 FAIL

不合格判定:
- 仅 Claim 无 Data:     "空中楼阁" → 直接 FAIL
- 仅 Data 无 Warrant:   "数据罗列" → WARNING (有数据不会推理)
- 无 Qualifier:         "过度概括" → WARNING
- 无 Reservation:       "绝对化"   → WARNING
```

### 质量评分

```
completeness (完整度) = (要素齐全数 / 6) × 100

validity (有效性) = 
  Data→Warrant→Claim 链完整 ? 0.4 : 0.0 +
  Data 包含数值统计 ? 0.2 : 0.0 +
  Warrant 有理论支撑 (Backing) ? 0.2 : 0.0 +
  Qualifier 合理 ? 0.1 : 0.0 +
  Reservation 明确 ? 0.1 : 0.0
```

## 与 CARS Model 的关系

```
CARS Move1 (Establish Territory) → 提供 Backing 的来源
CARS Move2 (Establish Niche)     → Claim 的定位
CARS Move3 (Occupy Niche)        → Claim + Data 的组合

CARS 解决"论文结构如何写"
Toulmin 解决"每个论点是否成立"
```

## 传递规则

```json
{"source_type": "toulmin_analysis", "source_ref": "section_id",
 "claim": "...", "data": "...", "warrant": "...",
 "backing": "...", "qualifier": "...", "reservation": "...",
 "completeness": 0.83, "validity": 0.70}
```

## 理论来源

- Toulmin, S. E. (1958). *The Uses of Argument*. Cambridge University Press.
- Perelman, C. & Olbrechts-Tyteca, L. (1958). *The New Rhetoric*.
- Hitchcock, D. (2013). *The Language of Argumentation*.
