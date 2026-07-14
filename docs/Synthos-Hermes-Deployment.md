# Synthos — Hermes Agent 部署配置

> 本文档记录如何搭建一个能运行完整 Synthos 的 Hermes Agent 实例。

## 核心原理

Hermes Agent 支持通过 `skills.external_dirs` 配置多个技能目录，Agent 启动时自动扫描并加载所有 SKILL.md。

```yaml
skills:
  external_dirs:
    - /path/to/Synthos/skills
```

**关键**：配置 `external_dirs` 后，Agent 扫描 `~/.hermes/skills/` + `external_dirs` 下的所有 SKILL.md，按全路径区分不同技能。同名不同路径的技能会被分别加载。

## 完整配置

```yaml
# ~/.hermes/config.yaml (相关节)

skills:
  external_dirs:
    - /path/to/Synthos/skills       # Synthos 技能目录
  template_vars: true
  inline_shell: false
  inline_shell_timeout: 10
  guard_agent_created: false
  write_approval: false
  creation_nudge_interval: 15

curator:
  enabled: true                      # 自动提炼/清理技能
```

## 目录结构

```
Synthos/skills/                          # Git管理的技能仓库
├── core/                                # 认知原子 + 核心逻辑
│   ├── task-router/                     # 入口：最短路径路由
│   └── knowledge-acquisition/           # 文献检索（已合并到 literature）
├── extended/                            # 扩展技能
│   └── research-tools/
│       └── research/
│           └── literature/              # 文献检索统一入口（含代码）
│               ├── SKILL.md
│               ├── scripts/
│               │   ├── literature.py
│               │   ├── sources/         # 8个数据源
│               │   └── download/        # 下载层
│               └── references/
├── private/                             # 个人技能（按需）
├── devops/                              # 运维技能
├── paper-tools/                         # 论文工具
├── research/                            # 研究领域技能
└── ... (共162个SKILL.md)

~/.hermes/skills/                        # Agent管理的技能（~80个）
├── literature/                          # [已删除，合并到Synthos]
├── pdf-to-markdown/                     # Agent自有技能
├── paper-quality-audit/                 # Agent自有技能
└── ...
```

## 环境变量

```bash
# Semantic Scholar API Key（单key，已移除双key轮换）
export SEMANTIC_SCHOLAR_API_KEY="your_key_here"

# 可选：CORE API Key（免费注册 https://core.ac.uk/api-key/）
export CORE_API_KEY="your_core_key"
```

存储位置：`~/.secrets`（mode 600）+ `~/.bashrc`（交互shell自动source）。

## 技能合并历史

| 技能 | 原始位置 | 当前状态 |
|------|---------|---------|
| `literature` | 代码在Synthos，SKILL.md在.hermes | 已合并：SKILL.md+references复制到Synthos，删除.hermes副本 |
| `knowledge-acquisition` | core/knowledge-acquisition | REDIRECT到literature |

**规则**：Synthos 目录（Git管理）是技能的唯一来源。`.hermes/skills/` 只保留 Agent 自己创建/管理的技能。

## 快速验证

```bash
# 1. 确认配置生效
grep -A2 'external_dirs' ~/.hermes/config.yaml

# 2. 确认技能可加载
ls /path/to/Synthos/skills/extended/research-tools/research/literature/SKILL.md

# 3. 测试文献检索
python3 /path/to/Synthos/skills/extended/research-tools/research/literature/scripts/literature.py search "BPPV" --sources crossref pubmed --max 3

# 4. 确认S2单key正常
python3 -c "
import importlib.util, os, sys
sys.path.insert(0, '/path/to/Synthos/skills/extended/research-tools/research/literature/scripts')
spec = importlib.util.spec_from_file_location('ss', 'sources/semantic_scholar.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('API keys:', len(mod.SemanticScholar.API_KEYS))  # 应为1
print('Key:', mod.SemanticScholar.API_KEYS[0][:8] + '...')
"
```

## 技能加载优先级

```
~/.hermes/skills/ (默认路径)
+ external_dirs (通过配置添加)
= Agent加载的所有技能
```

**注意**：
- 同名不同路径的技能会被分别加载（如 `.hermes/skills/foo` 和 `external_dir/foo` 是两个独立技能）
- 如果存在同名同路径的技能（如两个 `literature/SKILL.md`），Agent 行为取决于文件扫描顺序（不可靠）
- **最佳实践**：确保所有技能路径全局唯一

## 清理原则

1. Git管理（Synthos/skills/）是技能源码仓库
2. `.hermes/skills/` 是 Agent 运行时加载目录
3. 技能应同时存在于两个位置，但路径必须不同
4. 技能合并/迁移后，需从旧位置删除，避免重复加载