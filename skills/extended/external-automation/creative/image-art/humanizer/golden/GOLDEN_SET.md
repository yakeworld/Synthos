# GOLDEN_SET.md — humanizer

> 对应原则：P0（证据可溯性：每条模式替换可定位）+ P1（原子可复现性）
> golden_set_origin: self_defined

## 设计依据

本技能（IO_CONTRACT: `text: str, target_tone: str -> humanized_text: str`）识别并消除 29 种 AI 写作模式（5 大类：内容/语言语法/风格/沟通/填充），同时注入人类写作个性（观点、节奏变化、矛盾感、第一人称），并支持声音校准。金标准是自设的，用于验证：

1. **模式识别完整性**（HUMA-003/005）：29 项模式逐类扫描，识别出的模式必须定位到具体子串（P0：凡数必源——每个断言可回指输入）
2. **语义保真**（P3 保真原则 / HUMA-007）：替换保持语义等价，核心事实（数字、实体、立场）不丢失
3. **有魂**（P2 / HUMA-001/002）：不只是机械删词——注入观点与节奏变化（句子长短交替）
4. **声音匹配**（P4 / HUMA-004）：提供样本时匹配样本声音；无样本时回退默认自然声音并声明
5. **输出格式**（R3）：改写草稿 + 剩余 AI 特征说明 + 最终版本
6. **错误路径**（RULES-3 异常约束）：空输入 → 带上下文的错误

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 正常路径 | 1 | 高密度 AI 模式文本（覆盖全部 5 大类 ≥1 项）+ 无样本 |
| 正常路径（声音校准） | 1 | 提供写作样本 → 匹配样本句长/用词 |
| 错误路径 | 1 | 空文本 → 报错不生成 |
| 模式大类覆盖 | 5/5 | 内容、语言语法、风格、沟通、填充 各 ≥1 |
| 语义保真 | 全部 | 关键事实保留列表 |

## 测试用例 (cases/)

### case_001: 正常路径 — 高密度 AI 模式博客段（无样本）
- **输入**: 一段含 ≥5 类 AI 模式的英文文本（delve / serves as / Additionally / In order to / em dash / "the future looks bright" / "Industry experts say"），`target_tone: "casual"`，无声音样本
- **期望**:
  - `detected_patterns` ≥6 项，且覆盖 5 大类中的 ≥4 类，每项含 `pattern_id` + 输入中的 `evidence_substring`
  - 最终文本不含 forbidden_terms（delve, serves as, Additionally, In order to, "the future looks bright", "Industry experts say"）
  - 语义保真：`preserved_facts`（具体数字与实体）全部保留
  - 注入个性：句长变化（max/min 句长比 ≥3）或出现第一人称/观点句
  - 输出含 R3 三段：draft + 剩余特征说明 + final
  - `voice_fallback_declared: true`（无样本时声明回退默认声音）

### case_002: 正常路径 — 声音校准（提供样本）
- **输入**: 同一段 AI 文本 + `voice_sample`（短句、口语、用 "stuff"/"things"、少标点）
- **期望**:
  - `voice_analysis` 含 sentence_length_profile / diction_level / punctuation_habits
  - 最终文本句长模式匹配样本（平均句长 ≤ 样本平均的 1.3 倍），不升级用词（"stuff"/"things" 级别）
  - `voice_fallback_declared: false`（使用了样本而非默认声音）
  - 语义保同 case_001

### case_003: 错误路径 — 空文本
- **输入**: `text: ""`
- **期望**: `status == "error"`，`error` 含上下文（哪个输入字段为空）与恢复建议（提供待处理文本或文件路径）；不返回空改写

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。采用**语义等价判定**（改写措辞不可逐字匹配）：

- `status` 精确匹配
- `detected_patterns`：每项 `pattern_id` 必须落在 29 项模式目录内；`evidence_substring` 必须是输入 `text` 的真实子串（P0 可回源）
- `forbidden_terms` 不得出现在 `final_text`
- `preserved_facts` 必须逐字出现在 `final_text`
- 个性注入检查为启发式：句长比或第一人称/观点标记，任一命中即通过
- `output_sections` 必须含 R3 规定的 3 个部分
- 错误 case 检查 `status == "error"` 且 `error.suggestion` 非空

## pass_threshold: 1.00

含义：3 个测试用例全部通过。

### 阈值理由
- **设 1.0**：模式识别的 evidence_substring 回源（P0）与语义保真（P3）是硬红线——编造"识别到的模式"或丢失核心事实即失败
- **改写措辞不逐字匹配**：人性化的本质是表达变换，逐字匹配与技能目标冲突；判定锚定在事实保留 + 模式消除 + 结构完整上

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-27 | 初始自设金标准，3 个 case | Synthos Agent |
