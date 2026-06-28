# Private Skill Classification Pattern

> 从 Synthos 技能库公共/私有分离实战中提取的模式。2026-06-25 实战验证。

## 问题

技能库需要推 GitHub 公开分享，但大量技能含：
- **凭证/SSO**（meddata SSO、Google API key）
- **论文数据**（PIMA 审计、投稿优先级）
- **内部系统**（演化引擎、AKNE 知识图谱）
- **研究方向专有**（BPPV、眼动追踪、乳腺癌诊断）
- **服务器路径**（/media/yakeworld、本机名）

直接推送公开 GitHub 有隐私泄露风险。但全部留在本地又无法分享通用方法论。

## 架构方案

最优方案：**单仓库 + gitignore 子目录**

```
/media/.../Synthos/skills/
├── core/quality-gate/          ← git 追踪，推 GitHub 公开
├── extended/research-tools/    ← git 追踪，推 GitHub 公开
└── private/                    ← gitignore 忽略，永不上推
    ├── meddata-download/       ← 凭证
    ├── pima-audit/             ← 论文审计
    ├── bppv-expert/            ← 研究方向
    └── ...
```

### 为什么不是双 repo？

| 方案 | 问题 |
|:-----|:------|
| 双 repo（公开+私有） | 两套 remote，Hermes 要配两个 external_dirs，Codex 要记两个路径 |
| **单 repo + gitignore** ✅ | 一个目录，一个 external_dirs，Codex 用相对路径，git 自然挡 |

### .gitignore 配置

```gitignore
# 私有技能（凭证/论文审计/系统运维，不入库）
/skills/private/
```

## 三层次分类法

| 层级 | 位置 | 可公开？ | 内容类型 |
|:-----|:------|:--------:|:---------|
| **公开** | Synthos/skills/core,extended/ | ✅ | 通用认知原子、通用研究工具、通用自动化 |
| **私有** | Synthos/skills/private/ | ❌ | 凭证、论文审计、研究专有、内部系统、本机路径 |
| **代理** | ~/.hermes/skills/ | ❌（无 git） | Codex 调度、记忆系统、会话管理、任务状态 |

## 隐私检测检查清单

移动技能到 private/ 前，检查以下信号：

### 自动检测模式

```bash
# 1. 绝对路径
grep -rl '/media/yakeworld' skills/<name>/

# 2. 论文路径
grep -rl 'outputs/papers' skills/<name>/

# 3. 本机名
grep -rl 'yakeworld' skills/<name>/

# 4. 凭证
grep -rli 'api_key\|password\|secret\|meddata\|sso' skills/<name>/ | grep -v DEEPSEEK_API_KEY

# 5. IP 地址（非内网）
grep -rn '\d\{1,3\}\.\d\{1,3\}\.\d\{1,3\}\.\d\{1,3\}' skills/<name>/ | grep -v '0\.0\.0\.0\|127\.0\.0\.1'

# 6. 描述中的 "Synthos 系统" 或 "为 Synthos 系统"
grep -rli '为Synthos系统\|Synthos系统' skills/<name>/
```

### 人工判断规则

即使自动检测全通过，以下情况也判断为私有：

| 场景 | 判断 | 例 |
|:-----|:-----|:---|
| 描述含"为 Synthos 系统..." | 🔒 私有 | capacity-planning、chaos-engineering |
| 跟你的研究方向直接相关 | 🔒 私有 | BPPV、眼动追踪、乳腺癌诊断 |
| 含未发表论文的具体数据 | 🔒 私有 | PIMA 审计、投稿优先级 |
| 通用方法论（无系统/论文引用） | ✅ 可公开 | quality-gate、hypothesis-generation |

## Hermes 配置

```yaml
# ~/.hermes/config.yaml
skills:
  external_dirs:
    - /media/yakeworld/sda2/Synthos/skills
```

一个路径同时覆盖公开和私有，`skill_view` 自动递归加载。

## Codex 访问

```markdown
## 技能加载
公开: cat skills/core/quality-gate/SKILL.md
私有: cat skills/private/meddata-download/SKILL.md
```

相对路径（因为 Codex 工作目录在 Synthos 根）。

## 迁移步骤

```bash
# 1. 创建私有目录
mkdir -p skills/private

# 2. 搬技能
mv skills/core/daily-routine skills/private/core/

# 3. git rm 已跟踪的旧位置
git rm -r --cached skills/core/daily-routine

# 4. 验证 gitignore
git check-ignore skills/private/core/daily-routine/SKILL.md
# 应输出路径（表示已忽略）

# 5. 提交
git add .gitignore
git commit -m "chore: move <name> to skills/private/"
```

## Hermes 本地代理技能（不入任何 git）

以下技能只属于 Hermes 运行时，不应在任何 repo 中：

```
~/.hermes/skills/
├── codex-tmux-control/        ← Codex tmux 调度协议
├── hermes/                    ← Hermes 自身配置
├── memory-feedback-automation/← 记忆系统
├── memory-infrastructure/     ← 记忆引擎
├── session-context-recovery/  ← 会话管理
├── task-state-manager/        ← 任务状态
└── tmux-codex-debugging/      ← Codex 调试
```
