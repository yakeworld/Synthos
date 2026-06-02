# NotebookLM Access Troubleshooting & Fallback Protocol

> 当 `notebooklm use` + `summary` 返回 "account-routing mismatch" 时，不惊慌。
> 本文档提供从诊断→修复→降级兜底的完整流程。

---

## 1. 症状识别

### 典型错误

```
RPC rLM1Ne returned null result with status code 5 (Not found).
If you have multiple Google accounts signed in, this is commonly
an account-routing mismatch — the request defaults to account
index 0 when no authuser is set.
```

另见 `notebooklm auth check` 通过但 `notebooklm use <id>` + `summary` 仍失败的情况。

### 根因

`notebooklm-py` 的 `__Host-GAPS` cookie 包含 `1:...` 前缀表示 authuser=1，但 RPC 请求默认路由到 authuser=0（第一个 Google 账号）。当实际 NotebookLM 项目在第二个账号下时，请求找不到项目。

---

## 2. 诊断步骤

```bash
# 1. 检查认证状态
notebooklm auth check

# 2. 检查 GAPS cookie 的 authuser 索引
python3 -c "
import json
with open('/home/yakeworld/.notebooklm/profiles/default/storage_state.json') as f:
    data = json.load(f)
cookies = data.get('cookies', [])
for c in cookies:
    if 'GAPS' in c.get('name',''):
        print(f\"{c['name']}: {c['value'][:80]}\")
        # 若前缀为 1: 则 authuser=1
        if c['value'].startswith('1:'):
            print('  → authuser=1 (RPC默认authuser=0，路由错位)')
        elif c['value'].startswith('0:'):
            print('  → authuser=0 (正常)')
"

# 3. 检查列表是否可读（list 与 use 可能使用不同 auth 路径）
notebooklm list
# 如果能 list 但不能 use + summary，确认是 authuser 路由问题
```

---

## 3. 修复尝试（按优先级）

### 3.1 刷新 Cookie（最轻量）

```bash
notebooklm auth refresh
notebooklm use <id> --force 2>&1 && notebooklm summary
```
成功率：低（仅当 cookie 过期时有效）

### 3.2 重新登录（推荐）

```bash
notebooklm auth logout
notebooklm login
```
登录成功后重试：
```bash
notebooklm list
notebooklm use <id> && notebooklm summary
```

### 3.3 指定浏览器（当默认 Chromium 卡住时）

```bash
# 查看可用浏览器
notebooklm login --help

# 尝试系统 Chrome（如果已安装）
notebooklm login --browser chrome
```

### 3.4 手动从浏览器拷贝 cookie（兜底）

如果 CLI 的 headless Chromium 始终卡住（在无 GUI 环境下常见）：
1. 在用户的桌面浏览器打开 https://notebooklm.google.com
2. 按 F12 → Application → Storage → Cookies → `notebooklm.google.com`
3. 导出 `__Host-GAPS` cookie 值
4. 写入 storage_state.json

---

## 4. 降级兜底：NotebookLM 不可用时的 P-1 流程

当所有修复尝试失败后，**不要阻塞论文管线**。直接降级到外部 API 搜索。

### 4.1 降级条件

> 连续尝试以下两项失败后即进入降级：
> 1. `notebooklm auth refresh && notebooklm use <id> --force`
> 2. `notebooklm auth logout && notebooklm login`（超时或失败）

### 4.2 降级管线

| 原 NotebookLM 步骤 | 降级替代 |
|:--------------------|:----------|
| Q1: notebooklm ask "文献覆盖度评估" | OpenAlex 搜索 + 人工梳理 |
| Q2: notebooklm ask "Gap质量评估" | 文献对比 → 手动Gap推导 |
| Q1-Q6: 逐问文献获取 | OpenAlex → Semantic Scholar → PubMed 串行搜索 |
| 文献综合表构建 | 外部搜索结果整理 |

### 4.3 文献搜索执行规范（NotebookLM 不可用时）

```bash
# Step 1: OpenAlex（无速率限制，首选）
curl -s "https://api.openalex.org/works?filter=title_and_abstract.search:KEYWORD,publication_year:2020-&sort=cited_by_count:desc&per_page=10&select=id,doi,title,cited_by_count,publication_year,primary_location"

# Step 2: Semantic Scholar（串行，间隔≥3秒）
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=KEYWORD&limit=10&fields=title,authors,year,citationCount,externalIds"
sleep 3

# Step 3: PubMed（生物医学主题必需）
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=KEYWORD&retmax=10&retmode=json"
```

### 4.4 文献地图构建格式

每次搜索后立即整理为结构化表格：

```markdown
## [主题] 文献地图

| 年份 | 第一作者 | 标题 | 期刊 | 被引 | 关键发现 |
|:----:|:--------:|:-----|:-----|:----:|:---------|
| 2023 | Author | Title | Journal | N | Key finding |
```

最终汇合为：
- **已有综述级文献**（3-5篇高引综述）
- **关键研究论文**（每类眼动参数1-2篇代表性文献）
- **Gap证据**（什么没被研究过 → 构建研究空白）

### 4.5 搜索技巧（生物医学主题）

由于搜索引擎的全文匹配限制，生物医学论文可能需要尝试多种关键词变体：

| 概念 | 关键词变体 |
|:-----|:-----------|
| 眼动追踪 | "eye tracking" OR "video-oculography" OR "oculomotor" OR "eye movement" |
| 帕金森 | "Parkinson disease" OR "Parkinson's" OR "Parkinsonian" OR "PD" |
| 固视微动 | "fixational" OR "fixation stability" OR "microsaccade" OR "ocular drift" |
| 扭转 | "torsion" OR "torsional eye movement" OR "ocular counter-roll" OR "Listing's law" |

**关键原则**：如果第一次搜不到相关结果，**调整关键词而非重复搜索**。OpenAlex 的 `title_and_abstract.search` 过滤器对长关键词组合敏感——过长的短语（5+词）可能返回不相关结果。适当缩短、拆分或替换。

---

## 5. 后续恢复

当 NotebookLM 重新可用后：

```bash
# 验证访问
notebooklm use <id> && notebooklm summary

# 将已构建的文献地图上传为 source
notebooklm note create "Literature Map: [Topic] - [Date]"
notebooklm note add "<source_text>"

# 使用 NotebookLM 验证搜索质量
notebooklm ask "评估我上传的文献地图是否有重大遗漏？"
```

这样既保证了论文管线不阻塞，又保留了日后与 NotebookLM 知识库对接的可能性。

---

## 6. 永久修复：多账号 profile 隔离（推荐方案）

当遇到多个 Google 账号导致的 authuser 路由错位时，临时修复（刷新 cookie、重新登录）只能管一段时间。**永久修复**是用 `--all-accounts` 将每个账号提取为独立 profile，并将项目最多的账号设为 default。

### 6.1 提取所有账号为独立 profile

```bash
# 从浏览器提取所有已登录 Google 账号的 cookie
notebooklm login --browser-cookies auto --all-accounts

# 查看可用 profile
notebooklm profile list
# 输出示例：
# ┃ *  │ default    │ -                    │ not authenticated ┃
# ┃    │ ghfdshgf79 │ <USER_EMAIL> │ authenticated     ┃
# ┃    │ yakeworld  │ <USER_EMAIL>  │ authenticated     ┃
# ┃    │ gushiedu   │ <EXAMPLE_EMAIL>   │ authenticated     ┃
```

### 6.2 查找项目所在的 profile

```bash
# 在每个 profile 下搜索目标 notebook
notebooklm -p ghfdshgf79 list | grep -i "pima\|helix\|synthos"
notebooklm -p yakeworld list | grep -i "pima\|helix\|synthos"

# 或用已知 project ID 直接尝试
notebooklm -p ghfdshgf79 use <project_id>    # 成功则在此 profile
```

### 6.3 设为默认 profile

找到正确的 profile 后，修改 `~/.notebooklm/config.json`：

```bash
cat ~/.notebooklm/config.json
# {"language": "zh_Hans", "default_profile": "default"}

# 改为项目最多的 profile 名
echo '{"language": "zh_Hans", "default_profile": "ghfdshgf79"}' > ~/.notebooklm/config.json
```

验证：
```bash
notebooklm use <project_id>   # 此时应直接工作
notebooklm ask "测试"         # Q&A 正常工作
```

### 6.4 多 profile 使用语法

即使设置了默认 profile，仍可在特定命令中切换到其他账号：

```bash
# 临时切换到其他账号
notebooklm -p yakeworld use <another_id>

# 查看切换后的状态
notebooklm status

# 切回默认
notebooklm -p ghfdshgf79 use <id>
```

### 6.5 适用场景

| 场景 | 推荐方案 |
|:-----|:---------|
| 首次遇到 authuser 错误 | `--all-accounts` → 设 default_profile |
| 已有 profile 但想添加新账号 | 重新执行 `--all-accounts`（会更新已有的 profile） |
| 只想用一个账号 | `--browser-cookies auto --account <email>` |
| 脚本/自动化环境 | 用 `-p <profile>` 确保使用正确的账号 |

