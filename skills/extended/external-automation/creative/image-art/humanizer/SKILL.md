---
name: humanizer
description: "AI文本检测规避方法论 — 识别并消除AI生成文本的29种模式特征，注入人类写作个性与声音，使文本听起来自然、有观点、有灵魂。"
version: 1.2.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: []

---

## IO_CONTRACT

- **input**: `text: str, target_tone: str` — 待处理文本、目标语调
- **output**: `humanized_text: str` — 人性化改写文本

> 对应原则：P2（机械原子暴露输入输出规范）

## CHANGE_LOG

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-06-27 | 1.2.0 | 重构：提取思想/原则/方法/规则结构，具体代码与案例移至 references/ |

---

# Humanizer: AI文本人类化方法论

## 一、思想

> 文以载道，道在人情。

LLM 使用统计算法预测下一个词。结果趋向最统计可能的完成——这恰好是所有 AI 写作模式的根源。**AI写作的本质不是错误，而是过度平滑**。

**核心洞察**：人类写作的核心特征不是语法正确，而是**不均衡性**——句子长短交替、语气波动、观点偏袒、偶发混乱。完美结构是算法性的；适度的"混乱"才是人性。

## 二、原则

### P1. 去平滑原则

消除一切"过度平滑"的特征：均匀句长、中性语调、完整结构、无偏袒陈述。

### P2. 有魂原则

避免AI模式只是半份工作。空洞、无声音的写作同样明显。好文字背后必须有人——有观点、有情绪、有立场。

### P3. 保真原则

保留核心语义，只改变表达方式。不丢失信息，只转换语调。

### P4. 声音匹配原则

如果用户提供写作样本，优先匹配其声音特征，而非替换为默认"自然"声音。

## 三、方法

### 方法 1：AI模式识别

扫描以下五大类模式（共 29 项）：

**内容模式**（6项）：
1. 过度强调意义、遗产与趋势 — 填充"这代表了更广泛的..."
2. 过度强调知名度和媒体报道 — 堆砌媒体引用
3. 浅层的 -ing 结尾 — "highlighting...", "ensuring...", "reflecting..."
4. 宣传广告式语言 — "vibrant", "breathtaking", "nestled in the heart"
5. 模糊归因与虚词 — "Industry reports say...", "Experts argue..."
6. 大纲式"挑战与展望"章节 — "Despite its... faces challenges..."

**语言与语法模式**（7项）：
7. 过度使用的AI词汇 — "delve", "crucial", "pivotal", "tapestry", "underscores"
8. 避免系动词 — "serves as" 替代 "is"，"boasts" 替代 "has"
9. 否定并列句与尾部否定 — "Not only...but...", "no guessing" 做尾巴
10. 三分法滥用 — 强行将想法分组为三个
11. 优雅变体（同义词循环）— protagonist → main character → central figure → hero
12. 虚假范围 — "from the singularity to the cosmic web"
13. 被动语态与无主语片段 — "No configuration file needed"

**风格模式**（6项）：
14. Em dash 过度使用 — "—not by the people themselves. You don't say"
15. 粗体字过度使用 — 机械强调短语
16. 内联标题垂直列表 — "**Key:** description" 格式
17. 标题大小写 — "Strategic Negotiations And Global Partnerships"
18. 表情符号 — 装饰标题或要点
19. 弯引号 — "..." 替代 "..."

**沟通模式**（3项）：
20. 协作沟通产物 — "I hope this helps!", "Certainly!"
21. 知识截止免责声明 — "as of [date]", "Up to my last training update"
22. 谄媚/服务态度 — "Great question! You're absolutely right..."

**填充与模糊**（7项）：
23. 填充短语 — "In order to achieve this goal" → "To achieve this"
24. 过度模糊 — "could potentially possibly be argued"
25. 通用积极结论 — "the future looks bright", "exciting times lie ahead"
26. 连字符词对过度使用 — "cross-functional", "data-driven", "decision-making"
27. 说服权威套路 — "The real question is...", "at its core"
28. 路标与公告 — "Let's dive in", "here's what you need to know"
29. 碎片化标题 — 标题后跟仅重述标题的一句话

### 方法 2：重写策略

对每种识别出的模式：
1. 定位具体位置
2. 用自然表达替换（参考 patterns 列表中的 Before→After 对照）
3. 保持语义等价

**通用替换规则**：
| AI模式 | 替换为 |
|--------|--------|
| "serves as" | "is" |
| "Additionally" | 删除或换 "Also" |
| "In order to" | "To" |
| "It is important to note that" | 删除 |
| "The future looks bright" | 具体陈述 |
| "Industry experts say" | 具体来源 |
| "Despite challenges..." | 直接陈述问题 |

### 方法 3：注入个性

在去除AI模式之后，主动注入以下特征：

**拥有观点**：不只是报告事实——对事实做出反应。"I genuinely don't know how to feel about this" 比中立列出优缺点更有人味。

**变化节奏**：短促有力的句子。然后长句子慢慢到达目的地。混合使用。

**承认复杂性**：真实的人有矛盾感受。"This is impressive but also kind of unsettling" 优于 "This is impressive."

**适当使用第一人称**："I keep coming back to..." 或 "Here's what gets me..." 表明真实的人在思考。

**允许一些混乱**：完美结构感觉是算法的。旁白、插入语、未完成的想法是人类的。

**具体描述感受**：不说 "this is concerning"，说 "there's something unsettling about agents churning away at 3am while nobody's watching."

### 方法 4：声音校准

如果用户提供写作样本：

1. **读取样本**，分析：
   - 句子长度模式（短促有力？长而流畅？混合？）
   - 用词水平（随意？学术？之间？）
   - 段落开头方式（直接跳入？先给上下文？）
   - 标点习惯（破折号？括号？分号？）
   - 重复短语或口头禅
   - 过渡处理方式

2. **在重写中匹配声音**：如果写短句子，不产生长句子。如果写 "stuff" 和 "things"，不升级为 "elements" 和 "components"。

3. **无样本时**：回退到默认自然声音（个性化、变化、有观点）。

### 方法 5：最终AI检测循环

```
1. 呈现改写草稿
2. 自问："什么让下面明显是AI生成的？"
3. 简要回答剩余特征（如有）
4. 自问："现在让它不明显是AI生成的。"
5. 呈现最终版本（修订后）
```

## 四、规则

### R1. 触发条件

当用户需要：
- "humanize"、"de-AI"、"de-slop"、"un-ChatGPT" 文本
- 改写文本使其不像是LLM写的
- 编辑草稿（博客文章、论文、PR描述、文档、备忘录、邮件、推文、简历）使其更自然
- 匹配其写作声音
- 在发布前审查文本的AI痕迹

### R2. 输入来源

文本通常以三种方式到达：
1. **内联** — 用户直接粘贴。就地处理，回复改写。
2. **文件** — 用户指向文件。用 `read_file` 加载，用 `patch` 或 `write_file` 应用编辑。
3. **声音校准样本** — 用户提供额外样本并要求匹配。先读取样本，再重写。

### R3. 输出格式

提供：
1. 改写草稿
2. "什么让下面明显是AI生成的？"（简要要点）
3. 最终改写版本
4. 变更摘要（可选）

### R4. 文件编辑规范

对文件编辑，展示 diff 或变更部分——不要静默覆盖。对仓库中的 markdown 文档，按 section 用 `patch` 比重写整个文件更干净。

### R5. 自我审查

Hermes 在撰写用户端散文时也应应用此技能——发布说明、PR描述、文档、长篇解释、摘要。

### R6. 语义保真

改写后必须：
- 朗读时听起来自然
- 自然变化句子结构
- 使用具体细节而非模糊声明
- 保持上下文的适当语调
- 适当使用简单结构（is/are/has）

## 五、参考

| 文件 | 内容 |
|------|------|
| `references/ai-patterns-full.md` | 29项AI模式的完整Before→After对照 |
| `references/voice-calibration.md` | 声音校准的详细指南 |
| `references/full-example.md` | 完整的改写示例（含Before/After对比）|
| `BOUNDARY.md` | 技能边界声明 |
| `EVIDENCE_SCHEMA.md` | 技术证据架构 |
| `IO_CONTRACT.md` | 输入输出规范 |

## 六、版本历史

- **v1.0.0** (2026-03): 初始版本，基于 Wikipedia "Signs of AI writing"
- **v1.1.0** (2026-06): 新增声音校准章节
- **v1.2.0** (2026-06): 重构为思想/原则/方法/规则结构

> 本技能改编自 [blader/humanizer](https://github.com/blader/humanizer)（MIT 许可），基于 [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)，由 WikiProject AI Cleanup 维护。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
