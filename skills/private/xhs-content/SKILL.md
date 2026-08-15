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
- 所有事实是否基于真实代码/数据（先读技能再写）---





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
