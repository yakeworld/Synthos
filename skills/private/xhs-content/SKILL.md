---
name: xhs-content
description: 小红书 (XHS) 内容生成与管理 — 生成发帖正文、标签、封面文案、排版建议。覆盖内容模板、素材管理、发布通道评估。
signature: 'xhs-content -> private: synthetic skill for xhs content'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: 小红书 (XHS) 内容生成与管理 — 生成发帖正文、标签、封面文案、排版建议。覆盖内容模板、素材管理、发布通道评估。
    signature: 'xhs-content -> private: synthetic skill for xhs content'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: social-media
author: Synthos
triggers:
- 需要生成小红书帖子内容
- 需要整理小红书素材（正文+标签+配图建议）
- 需要评估小红书发布方案
---

## IO_CONTRACT

- **input**: 帖子主题与素材 — 知识点内容、数据源/网站链接、事实性素材
- **input**: 配图需求 — 信息对比/步骤说明（Pillow 卡片式）或真实网站展示（浏览器截图）
- **output**: 小红书帖子完整包 — 发帖正文 + 标签 + 封面文案 + 排版建议（≤10词/图，无装饰）
- **output**: 配图组（5张：封面+各源+结论，1080×1440 3:4）+ 发布通道评估结论

|
| 分辨率 | **1080×1440 (3:4)** |
| 底色 | #0F172A |
| 卡片 | #1E293B |
| 强调色 | #3B82F6 蓝 / #8B5CF6 紫 / #EF4444 红 |
| 文字 | #E2E8F0 / #94A3B8 |
| 字体 | Noto Sans CJK SC（粗体 `/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc`，常规 `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`）|
| 每图文字 | ≤10词/图，纯数据无装饰 |

**脚本位置：** 任意路径如 `/home/yakeworld/gen_xhs_v2.py`，运行后输出到 `/home/yakeworld/xhs_images/`。

**风格要求：** 无装饰圆/渐变/装饰线，只画必要的卡片框和文字。每张图只展示一个知识点，不堆叠。

**方式B：浏览器截图（适合展示真实网站/数据源）**

1. `browser_navigate(url="https://...")` 加载目标页面
2. `browser_vision(question="Screenshot of ...")` 截图（即使vision失败截图文件仍在）
3. 截图路径从 `browser_vision` 返回的 `screenshot_path` 获取
4. 用 `MEDIA:<path>` 直接发送

**配图选择原则：** 信息对比/步骤说明 → 方式A；网站/数据源展示 → 方式B。两种可混搭。

### 标准帖子流程
1. `skill_view(name='xhs-content')` 加载技能
2. 根据素材生成内容（按上方格式模板）
3. 写 `/tmp/xhs_all_figures.py` 批量生成配图（5张：封面+各源+结论）
4. 输出完整帖子

## Pitfalls
- **"讲多的是错的"** — 任何超出事实的叙述/评论/背景/互动收尾都是错误。写完检查：删除所有可以删的字。
- 小红书不支持代码高亮 — 用截图展示代码
- Pillow 圆角矩形：用 `draw.rounded_rectangle()` 而非 `draw.rectangle()` + `radius`
- 配图路径无约定，发帖前用 `MEDIA:` 发送
- font 回退：先用 Noto Sans CJK，不存在则用 `load_default()`

## Verification
- 内容是否符合"讲多的是错的"原则（字数≤目标1/3）
- 配图文字量是否≤10词/图
- 所有事实是否基于真实代码/数据（先读技能再写）

## Golden 集合 · GOLDEN SET

- **Golden Input**: 帖子主题 "Linux 环境排障三步法" + 素材（df/lock/venv 三个知识点的事实性内容），配图需求：信息对比卡片式（Pillow）。
- **Golden Output**: 完整帖子包 — 正文（≤目标字数 1/3，"讲多的是错的"原则）、标签、封面文案、排版建议（≤10词/图）；5 张配图（1080×1440 3:4，底色 #0F172A，Noto Sans CJK），每张图只展示一个知识点，无装饰。
- **Golden Error**: 正文含"值得一提的是……""总结一下，我们……"等叙事性评论（超出事实范围）→ 诊断：违反"讲多的是错的"原则；修复：删除所有可删字，仅保留事实陈述与数据，重写后逐字检查。

## 验证清单 · VERIFICATION
- [ ] 正文字数 ≤ 目标字数的 1/3（"讲多的是错的"原则），删除所有叙事性评论/互动收尾
- [ ] 5 张配图均为 1080×1440 (3:4)，底色 #0F172A，每张图 ≤10 词纯数据无装饰
- [ ] 所有事实性声明（df/lock/venv 等知识点）可追溯至真实代码或数据源，非凭记忆生成
- [ ] 配图路径已通过 `MEDIA:<path>` 发送验证（非仅本地文件存在）
- [ ] font 渲染正常（Noto Sans CJK SC，非 `load_default()` 回退），无方块/乱码
## 示例 · EXAMPLES
- **示例一（Linux 排障三步法帖子）**：主题 "Linux 环境排障三步法"，素材：df/lock/venv 三个知识点事实。产出：正文 ≤150 字（仅陈述 df -h → 查 lock → venv 隔离三步）、标签 5 个（#Linux #排障 #MiKTeX #venv #运维）、封面文案 "三步定位环境故障根因"、5 张 Pillow 卡片式配图（封面+df+lock+venv+结论），1080×1440，#0F172A 底色，每张 ≤10 词。
- **示例二（数据源网站展示帖子）**：主题 "OpenML 数据集检索"，素材：OpenML 网站 URL + 检索步骤。产出：正文 ≤200 字（事实性步骤描述）、方式B 浏览器截图 2 张（OpenML 搜索页 + 结果页）、方式A Pillow 卡片 3 张（封面+步骤+结论），发布通道评估：个人账号可发（非医疗领域）。
## 约束规则 · RULES
1. **讲多即错**：正文禁止叙事性评论（"值得一提的是""总结一下"等），写完逐字检查删除所有可删字，字数 ≤ 目标 1/3。
2. **事实先行**：所有知识点必须基于真实代码/数据（先读源文件再写），禁止凭记忆或推测生成。
3. **配图规范**：1080×1440 (3:4)，#0F172A 底色，Noto Sans CJK SC 字体，每图 ≤10 词纯数据，无装饰圆/渐变/装饰线，每图只展示一个知识点。
4. **代码截图**：小红书不支持代码高亮，涉及代码一律用截图展示，禁止贴代码块。
5. **发布通道评估**：医疗/敏感领域内容需评估账号权限与平台合规，不确定的通道标注 UNVERIFIED 不发布。
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[XHS-001]** 撰写正文时 → 严格执行“讲多即错”原则，删除所有叙事性评论与互动收尾，确保字数不超过目标字数的 1/3
- **[XHS-002]** 生成事实性内容时 → 必须基于真实代码或数据源（先读源文件再写），禁止凭记忆或推测生成知识点
- **[XHS-003]** 设计配图时 → 遵循 1080×1440 (3:4) 规格，使用 #0F172A 底色与 Noto Sans CJK SC 字体，每图仅展示一个知识点且文字≤10词
- **[XHS-004]** 展示代码内容时 → 因平台不支持代码高亮，一律使用截图展示，禁止直接粘贴代码块
- **[XHS-005]** 选择配图方式时 → 信息对比/步骤说明采用 Pillow 卡片式生成，真实网站/数据源展示采用浏览器截图，两者可混搭
- **[XHS-006]** 评估发布通道时 → 对医疗/敏感领域内容需评估账号权限与合规性，不确定通道标注 UNVERIFIED 并禁止发布
- **[XHS-007]** 处理字体渲染时 → 优先加载 Noto Sans CJK SC 字体，若不存在则回退至 `load_default()` 以避免方块/乱码