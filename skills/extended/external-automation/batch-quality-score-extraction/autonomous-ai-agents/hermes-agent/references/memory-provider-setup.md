# Memory Provider Setup

> Hermes Agent 记忆系统 — 配置文件内置文件内存 vs 外部 provider  
> 2026-05-27 实测: 只有 **holographic** 零依赖可用

## 架构概览

```
Hermes 记忆系统
├── 内置文件内存（默认）→ MEMORY.md + USER.md
│   ├── 2,200 字符上限注入系统提示
│   └── 无外部依赖，纯文件，不需要任何配置
│
└── 外部 Memory Provider（通过 config 激活）
    ├── holographic ✅ → local SQLite + FTS5 + 实体推理
    ├── honcho       → pip install honcho-ai
    ├── mem0         → MEM0_API_KEY（云API）
    ├── supermemory  → supermemory pip（云）
    ├── byterover    → brv CLI（二进制）
    ├── retaindb     → RETAINDB_API_KEY（云）
    ├── openviking   → OPENVIKING_ENDPOINT（服务端）
    └── hindsight    → hindsight-client pip（云/本地）
```

## 激活 Holographic（推荐）

激活只需两步，纯本地，零 API 密钥：

```bash
# 1. 设置 provider
hermes config set memory.provider holographic

# 2. 可选：启用自动事实提取（会话结束时自动分析并存储事实）
# 编辑 ~/.hermes/config.yaml，添加：
#   plugins:
#     hermes-memory-store:
#       auto_extract: true
#       default_trust: 0.5
```

验证加载：
```bash
hermes doctor                             # 检查配置
python3 -c "
from plugins.memory import load_memory_provider
p = load_memory_provider('holographic')
print('Available:', p.is_available() if p else 'FAILED')
"                                       # 确认加载成功
```

## Holographic 能力

| 维度 | 内置文件内存 | Holographic |
|:-----|:------------|:------------|
| 容量 | 2,200 字符 | 无限（SQLite） |
| 检索 | 关键词匹配 | FTS5 全文检索 |
| 实体 | 无 | 实体解析 + 关系跟踪 |
| 信任 | 无 | 信任评分 + feedback |
| 推理 | 无 | HRR 组合检索 |
| 工具 | 1 个(memory) | 2 个(fact_store 9动作 + fact_feedback) |

## Config 参数

```yaml
# ~/.hermes/config.yaml
memory:
  memory_enabled: true        # 内置文件内存仍启用（fallback）
  user_profile_enabled: true
  provider: holographic       # ← 外部提供者
  nudge_interval: 10

plugins:
  hermes-memory-store:
    auto_extract: true        # 会话结束自动提取事实
    default_trust: 0.5        # 新事实默认信任分
    min_trust_threshold: 0.3 # 低于此信任分的事实不被检索
    db_path: ~/.hermes/memory_store.db  # 默认路径
```

### 中文搜索说明

Holographic 对中文（CJK）查询自动走 `LIKE` 回退而非 FTS5 MATCH（FTS5 `unicode61` tokenizer 把连续 CJK 文本当作单个 token）。英文查询走 FTS5，失败时自动降级到 LIKE。19/19 测试全部通过。

详见 `references/holographic-cjk-search.md`。

### 工具参考

激活 Holographic 后，Agent 获得两个新工具：

### fact_store

9 种动作，用于结构化记忆管理：

| 动作 | 用途 | 示例 |
|:-----|:-----|:------|
| `add` | 存储事实 | `fact_store(action='add', content='用户偏好简洁输出', category='user_pref')` |
| `search` | 关键词检索 | `fact_store(action='search', query='constitution version')` |
| `probe` | 查询实体的所有事实 | `fact_store(action='probe', entity='task-router')` |
| `related` | 查询与某实体相关的实体 | `fact_store(action='related', entity='evolution')` |
| `reason` | 多实体组合推理 | `fact_store(action='reason', entities=['evolution', 'skill']` |
| `contradict` | 查找冲突事实 | `fact_store(action='contradict')` |
| `update` | 修改事实（信任分等） | `fact_store(action='update', fact_id=1, trust_delta=0.1)` |
| `remove` | 删除事实 | `fact_store(action='remove', fact_id=3)` |
| `list` | 列出所有事实 | `fact_store(action='list', limit=20)` |

### fact_feedback

训练信任分：

| 动作 | 含义 |
|:-----|:------|
| `helpful` | 该事实准确有用，信任分 ↑ |
| `unhelpful` | 该事实过时/错误，信任分 ↓ |

## 常见问题

### 两个记忆系统冲突吗？
不冲突。文件内存（MEMORY.md/USER.md）仍作为系统提示的冻结快照注入。Holographic 作为互补存储——存更多、更细、可搜索。两者并行工作。

### 切换 provider 会丢失内存吗？
只会丢失 Holographic 存储的事实（换了数据库）。文件内存独立于 provider 设置，不受影响。切换前可备份：`cp ~/.hermes/memory_store.db ~/.hermes/memory_store.db.bak`。

### 其他 provider 怎么激活？
仅 holographic 零依赖可用。其他（honcho/mem0/supermemory 等）需先安装对应包或注册 API Key，然后：
```bash
hermes config set memory.provider <name>
```
