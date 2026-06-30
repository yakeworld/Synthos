# SS API Key 管理指南

## 真实 Key

- **Semantic Scholar API Key**: `iYTNXXDH278PVXl2FJ2YU1TyZ5joLAZr3WA9IVzt`（40字符，无前缀）
- **存储位置**: `~/.secrets`（mode 600）

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 403 Forbidden | 使用 `s2k-` 前缀的旧 key | 改用无前缀的 key |
| 429 Too Many Requests | 并行调用或频率过高 | 1 req/sec，串行调用 |
| 空结果/0篇 | 子shell未source `.secrets` | 脚本中显式 `source ~/.secrets` |
| 占位符 key | `.bashrc` 中 `s2k-HT...TmBD` 被替换 | 使用 `~/.secrets` 中的真实 key |

## `.env` 文件状态

**无 `.env` 文件包含真实 SS API Key**。所有 `.env` 文件中的值为：
- `***`（占位符，如 `Synthos/.env.example`）
- 空或模板（如 `paper-manager/.env.template`）

## PubScholar

- **正确地址**: `pubscholar.cn`
- **错误地址**: `nfschina.com`（已失效）
- **API**: `https://pubscholar.cn/api/v1/paper/search`（返回 200）

## 环境变量隔离问题

子 shell（`execute_code`、`terminal` 后台任务、cron job）**不自动 source `~/.secrets`**。

**修复方案**：
```bash
# 方案1: 在脚本开头显式 source
source ~/.secrets 2>/dev/null
export SEMANTIC_SCHOLAR_API_KEY

# 方案2: 直接在脚本中 export（仅当你知道真实 key 时）
export SEMANTIC_SCHOLAR_API_KEY="iYTNXXDH278PVXl2FJ2YU1TyZ5joLAZr3WA9IVzt"

# 方案3: 在 .bashrc 末尾添加 source（影响所有交互 shell）
echo 'source ~/.secrets 2>/dev/null' >> ~/.bashrc
```

## Key 格式

SS 接受两种格式，但**只有无前缀格式当前有效**：
- ✅ `iYTNXXDH278PVXl2FJ2YU1TyZ5joLAZr3WA9IVzt`（40字符，当前可用）
- ❌ `s2k-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`（全部返回 403）
