---


name: social-media
description: 社交媒体 — X/Twitter发帖、搜索、DM；小红书（XHS）内容生成与发布。
author: Synthos
license: MIT
version: 1.1.0
license: MIT
triggers:
  - 需要执行social-media下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 社交媒体 — X/Twitter发帖、搜索、DM；小红书内容生成与发布。"
    signature: 'social-media -> sub-skills: [xurl, xhs-content]'
    related_skills: ["xurl"]


---


## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# social-media

> 父级技能目录，包含 1 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `xurl` — X/Twitter 发帖、搜索、DM（官方 CLI xurl）
- `xhs-content` — 小红书内容生成（SKILL.md在本目录的 xhs-content/ 子目录）

## 子技能详情

- `xurl`  → 技能目录：`xurl/`
- `xhs-content`  → 技能目录：`xhs-content/`（含 references/ 发布指南、templates/ 内容包模板）

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='xurl')      # 加载 Twitter 技能
skill_view(name='xhs-content')  # 加载小红书技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。

## 技能目录结构

```
social-media/
├── SKILL.md              ← 本文件（父级索引）
├── xhs-content/          ← 小红书内容生成技能
│   ├── SKILL.md
│   ├── references/
│   │   └── xhs-posting-guide.md
│   └── templates/
│       └── xhs-content-bundle-template.md
├── xurl/                 ← X/Twitter 发帖技能
│   ├── SKILL.md
│   └── references/
│       └── README.md
└── [future]              ← 更多社交媒体平台
```

## 小红书 (XHS) 发布现状

- 内容生成能力已就绪：系统内有已成型的小红书帖子素材（`/home/yakeworld/桌面/social-media/xhs/`）
- 发布通道：暂无官方API，需通过手动复制粘贴或浏览器自动化完成
- 内容格式：正文+标签+封面文案建议+排版建议，详见 xhs-content 技能
- 待补齐：小红书开放平台 OAuth 认证或第三方发帖工具集成

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
