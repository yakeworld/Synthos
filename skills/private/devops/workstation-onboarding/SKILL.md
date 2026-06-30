---
name: workstation-onboarding
description: "研究生工作站环境配置 — 在远程服务器上创建用户账号、安装 Python 科学计算环境 + Codex CLI + Hermes Agent"
version: 1.2.0
author: Synthos
license: MIT
category: devops
metadata:
  synthos:
    priority: P2
    atom_type: skill
    description: "标准化工作站环境配置流程：用户创建 → uv/Python → 科学计算库 → Codex CLI → Hermes Agent → Git 配置 → 培养方案"
    related_skills: [codex-install-guide, hermes-agent]
signature: "workstation-onboarding -> processed_result"
---

## 触发条件

需要在远程工作站（如 work1/work2/work3）上为新研究生建立独立的开发与科研环境时。

## 前置条件

- 工作站已创建操作系统用户账号（`sudo useradd -m -s /bin/bash -c '姓名拼音' 用户名`）
- 本地有 `sshpass` 用于初次密钥部署（或已有 SSH key 免密登录）
- 学生已有 `python3`（目标系统至少 Python 3.11+）

## 标准配置流程

### Phase 1: 基础环境

```bash
# 登录测试
ssh 用户名@主机名

# 目录结构
mkdir -p ~/workspace ~/projects ~/data ~/scripts
mkdir -p ~/workspace/eye-tracking ~/workspace/papers
mkdir -p ~/projects/研究项目名
mkdir -p ~/data/raw ~/data/results ~/data/datasets
```

### Phase 2: Python 科学计算栈

```bash
# 安装 uv（推荐，快于 pip/pipx）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建 venv + 安装核心库
cd ~/workspace/[项目名]
uv venv .venv
source .venv/bin/activate
uv pip install numpy scipy opencv-python matplotlib pandas jupyter scikit-learn
```

### Phase 3: Codex CLI (OpenAI Codex)

```bash
# 安装 nvm + Node.js
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm install --lts

# 安装 Codex
npm install -g @openai/codex
```

### Phase 4: Codex 配置

创建 `~/.codex/config.toml`：

```toml
model = "模型名"
model_provider = "vllm"

[model_providers.vllm]
name = "vLLM"
env_key = "VLLM_API_KEY"
base_url = "http://localhost:8000/v1"
wire_api = "responses"

[projects."/home/用户名"]
trust_level = "trusted"

[projects."/home/用户名/workspace"]
trust_level = "trusted"

[projects."/home/用户名/projects"]
trust_level = "trusted"

[ask_for_approval]
policy = "never"

[sandbox]
mode = "danger-full-access"

[shell_environment_policy]
inherit = "all"
```

环境变量（如 vLLM 在本地且无需认证，API key 随意填）：

```bash
echo 'export VLLM_API_KEY=*** >> ~/.bashrc
```

### Phase 5: Hermes Agent

```bash
pipx install hermes-agent
```

配置 `~/.hermes/config.yaml`：

```yaml
model:
  default: 模型名
  provider: custom:local

custom_providers:
- name: local
  base_url: http://localhost:8000/v1
  api_key: EMPTY
  model: 模型名

skills:
  external_dirs:
    - /home/用户名/Synthos/skills   # 链接 Synthos 技能库（如已 clone）

agent:
  max_turns: 150
  gateway_timeout: 1800
  tool_use_enforcement: auto
```

### Phase 6: 培养方案与入门指南

```bash
# 复制培养方案到 workspace/
cp 培养方案.md ~/workspace/

# 创建 START_HERE.md
cat > ~/workspace/START_HERE.md << 'EOF'
# 用户名·研究方向入门

## 登录信息
- 服务器: ssh 用户名@主机名
- 密码: 首次登录后自行修改

## 目录结构
- ~/workspace/ — 工作区
- ~/projects/ — 代码仓库
- ~/data/ — 数据文件

## Python 环境
source ~/workspace/项目名/.venv/bin/activate

## 第一步任务
1. 阅读培养方案
2. 配置 GitHub SSH Key
3. 跑通第一个 demo
EOF
```

## 验证清单

| 项目 | 验证命令 | 预期结果 |
|:-----|:---------|:---------|
| Python | `python3 --version` | 3.11+ |
| uv | `uv --version` | 有输出 |
| 科学计算库 | `source ~/workspace/项目名/.venv/bin/activate && python -c "import numpy, cv2, matplotlib, pandas, sklearn, scipy"` | 无错误 |
| bashrc PATH | `grep '\.local/bin' ~/.bashrc` | 包含 `$HOME/.local/bin:$PATH` |
| nvm 加载 | `grep 'nvm.sh' ~/.bashrc` | 包含 `source "$NVM_DIR/nvm.sh"` |
| VLLM_API_KEY | `grep VLLM_API_KEY ~/.bashrc` | 已 export |
| Codex 版本 | `source ~/.nvm/nvm.sh && codex --version` | 有版本号 |
| Codex 功能 | `export VLLM_API_KEY=*** && cd /home/用户名 && codex exec --skip-git-repo-check --disable hooks -c sandbox.mode=danger-full-access 'print("ok")' < /dev/null` | 成功生成并执行代码 |
| vLLM 连通性 | `curl -s http://localhost:8000/v1/models` | 返回模型列表 |
| Hermes 版本 | `hermes --version` | 有版本号 |
| codex-vllm.sh 脚本 | `ls ~/codex-vllm.sh` | 存在且可执行 |
| Hermes 功能 | `hermes chat -q 'test' -Q` | 正常返回 AI 响应 |
| Codex 功能 | `cd /home/用户名 && ./codex-vllm.sh 'print(\"ok\")' < /dev/null` | 成功生成并执行代码 |
| 科学计算栈(全) | `source ~/workspace/项目名/.venv/bin/activate && python -c "import numpy, cv2, matplotlib, pandas, sklearn, scipy, seaborn, PIL"` | 无错误 |
| Synthos 技能 | `ls ~/Synthos/skills/` | 目录存在且有内容 |
| Git 配置 | `git config --global user.name` | 已设置学生姓名 |
| 家目录权限 | `stat -c '%a' ~` | 750 或更宽松 |

## 交付检查与验收

配置完成后，按以下流程验证并生成交付报告。

### Phase 7: 验证 + 生成交付报告

```bash
# 1. 创建 codex 一键启动脚本
cat > ~/codex-vllm.sh << 'SCRIPT'
#!/bin/bash
# Codex CLI with vLLM backend — 一键启动
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
export VLLM_API_KEY=***  # 本地 vLLM 无需认证，但 Codex 要求该变量存在
EXTRA_ARGS="--skip-git-repo-check --disable hooks -c sandbox.mode=danger-full-access"
if [ $# -ge 1 ]; then exec codex exec $EXTRA_ARGS "$@"
else exec codex exec $EXTRA_ARGS; fi
SCRIPT
chmod +x ~/codex-vllm.sh

# 2. 验证 Hermes 能做科研推理
hermes chat -q "Write a Python function to compute 3D pupil normal from ellipse (cx,cy,a,b,theta). Only output code." -Q

# 3. 验证 Codex 能完成科研编码
./codex-vllm.sh "Generate noisy ellipse data, fit with OpenCV, save plot to /tmp/verify.png"

# 4. 验证科学计算栈全部可用
source ~/workspace/eye-tracking/.venv/bin/activate
python -c "
import numpy as np, cv2, matplotlib, pandas as pd, sklearn, scipy, seaborn, PIL
np.array([1,2,3]); cv2.imwrite('/dev/null', np.zeros((10,10)))
matplotlib.pyplot.figure(); pd.DataFrame(); sklearn.preprocessing.StandardScaler()
print('ALL OK')
"

# 5. 生成交付报告（使用下文的报告模板）
# 参考: references/handover-report-template.md
# 复制模板到 ~/workspace/WORK_CHECK_REPORT.md，填入实际数值
```

### 交付物清单

| 文件 | 位置 | 说明 |
|:-----|:-----|:-----|
| codex 一键脚本 | `~/codex-vllm.sh` | 封装环境变量和默认参数 |
| 入门指南 | `~/workspace/START_HERE.md` | 学生首次登录引导 |
| 培养方案 | `~/workspace/*培养方案.md` | 研究方向与里程碑 |
| 工作检查报告 | `~/workspace/WORK_CHECK_REPORT.md` | 环境验收证明（generated） |

## 常见问题

### Q: 工作站 vLLM 需要 API key 吗？
A: 同一台机器的本地 vLLM 通常不需要认证，API key 任意填。跨机器（如 work2→work1）需要确认。

### Q: Codex 沙箱报 `bwrap: Failed RTM_NEWADDR`？
A: 在 v0.141+ 中 `--yolo` 已移除。通过 config 设置 `sandbox.mode="danger-full-access"`，exec 时加 `--skip-git-repo-check --disable hooks`：
```bash
codex exec --skip-git-repo-check --disable hooks -c sandbox.mode=danger-full-access 'prompt'
```
或用永久配置写入 `~/.codex/config.toml`。

### Q: Codex 报 `Missing environment variable: VLLM_API_KEY`？
A: Codex 要求 `env_key` 对应的环境变量必须存在，即使本地 vLLM 无需认证。必须在 `~/.bashrc` 中显式 export（不要只在终端手打）：
```bash
echo 'export VLLM_API_KEY=任意值' >> ~/.bashrc
```
非交互 SSH 不会自动 source bashrc，测试命令需先 `source ~/.bashrc`。

### Q: Hermes 非交互模式怎么用？
A: v0.15+ 用 `-q/--query`（输入）+ `-Q/--quiet`（安静模式）：
```bash
hermes chat -q '你的提示' -Q
```
旧 FAQ 中的 `-m` 是模型选择参数，不是输入参数。`echo "x" | hermes chat` 在 piped stdin 下会进入 TUI 而非执行。

## 参考文件

- `references/graduate-training-plan-template.md` — 研究生培养方案模板（按项目定制）
- `references/handover-report-template.md` — 环境交付报告模板（验证后自动生成）
- `templates/codex-vllm.sh` — Codex CLI 一键启动脚本模板

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 示例 · EXAMPLES

1. **基本用法**: 标准输入 → 标准输出
2. **边界用例**: 空输入、特殊字符、异常路径
3. **错误场景**: 缺失依赖、权限不足、网络异常


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每个示例必须可独立运行、有明确输入输出、包含错误处理。



# Workstation Onboarding

