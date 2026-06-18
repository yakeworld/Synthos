# 项目本地技能注册到 Hermes Agent

## 用途

将项目目录中的本地 SKILL.md 文件注册到 Hermes Agent，使 `skill_view()` 能直接加载。适用于：
- Synthos 认知原子（task-router, knowledge-acquisition 等）
- 项目特定工作流 skill
- 任何不在 `~/.hermes/skills/` 下的 SKILL.md

## 方法：Symlink

```bash
ln -s /path/to/project/skills/skill-name ~/.hermes/skills/skill-name
```

## 验证

注册后验证：

```bash
skill_view('skill-name')
```

返回完整 frontmatter + 内容 + linked_files 即表示注册成功。

## 注意事项

- **零复制**：symlink 不复制文件，编辑项目目录中的 SKILL.md 立即生效
- **命名冲突**：注册前先用 `ls ~/.hermes/skills/` 检查是否有同名 skill
- **skill_manage 写操作**：`skill_manage(action='patch|write_file')` 操作的是 Hermes 管理的 skill 副本（位于 `~/.hermes/skills/<category>/skill-name/`），不是 symlink 指向的项目文件。编辑 symlink skill 的内容请直接用工具写文件到项目目录

## 实际案例：Synthos 注册

2026-05-22 将 Synthos 的 15 个技能全量注册：

| 分类 | 技能 | 用途 |
|:-----|:-----|:-----|
| 7 核心原子 | task-router, knowledge-acquisition, knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, viewpoint-verification | 认知管线 |
| 8 扩展技能 | paper-workflow, patent-disclosure, scientific-database-lookup, latex-output, figure-generation, nature-paper2ppt, research-ideation, experiment-recipes | 工作流支持 |

注册后 `skill_view('task-router')` 首次可用。
