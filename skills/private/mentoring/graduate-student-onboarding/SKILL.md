---
name: graduate-student-onboarding
description: Onboard new graduate students under 杨晓凯 — define research direction, set up workstation, create compressed training plan, establish weekly cadence.
version: 1.0.0
signature: "graduate-student-onboarding -> processed_result"
---

# Graduate Student Onboarding

**Trigger:** User (杨晓凯教授) says a new graduate student has joined the lab and needs research direction, workstation, or training plan.

**Core Philosophy:** 以战代练 — tools are learned by writing the first paper, not by studying them separately. Compress tool-learning phase to 1-2 weeks maximum.

## Workflow

### Phase 1: Profile the Student

Ask (or infer from context):

1. **Background**: 本科专业 (临床/计算机/生医工/其他)
2. **Skill level**: 编程基础 (None / Python basics / OpenCode user / Experienced)
3. **Degree type**: 科研型硕士 / 专业型硕士 / 博士
4. **Year**: 研一/研二/博一
5. **学院**: 温州医科大学 或其他

### Phase 2: Define Research Direction

Map student background to the lab's core pillars:

| Background | Recommended Primary Direction | Rationale |
|:-----------|:-----------------------------|:----------|
| 医学背景 + OpenCode | 三维眼动分析 (Kappa角/瞳孔定位) | 临床知识是优势，OpenCode 补编程短板 |
| 计算机/CV | 瞳孔/虹膜分割算法 | CV 技能直接对齐 |
| 生医工 | 三维眼球建模 / 仿真 | 工程+医学交叉 |
| 临床型硕士 | 公开数据集方法论审计 | 上手快，流程明确 |

**研究范围全景** (executive summary, 2026-06-22):

```
三维眼动分析（深度优先，全流程）
├── ① 瞳孔/虹膜分割 — 椭圆拟合、边界检测、3D重建
├── ② 眼球三维模型建模 — Kappa角、3D瞳孔定位、校准
├── ③ 半规管空间姿态 — CT/MRI 3D重建、空间几何
├── ④ BPPV虚拟仿真 — ODE动力学、Epley手法模拟
├── ⑤ VOR数字孪生 — PINN/ODE建模、前庭眼动仿真
├── 算法组件（边缘检测、特征点提取、校准）
└── 公开数据集分析 / 方法论审计

Synthos科研辅助系统
AI辅助教学

← 暂停：角膜/晶状体/玻璃体/泪膜/睑板腺/耳鸣/脑震荡
   (外围方向仅提取空白和假设，不进论文管线)
```

### Phase 3: Create the Training Plan

Use the template in `templates/training-plan.md`. Key principles:

1. **Time compression**: 
   - Tool learning: 1 week max (not months)
   - Data collection: begin Week 1, parallel with everything else
   - First paper draft: aim for Week 6-8
   
2. **Paper-first approach**: 
   - Week 1: choose topic, read 3-5 core papers, set up environment
   - Week 2-3: data prep + first figure + methods section
   - Week 4-5: results + discussion
   - Week 6-8: revision + submit

3. **Self-collected data preferred**:
   - Lab has eye-tracking equipment at 温州市人民医院
   - IRB can use department's existing approval or fast track
   - Target: 50-80 healthy controls for first study

4. **Public datasets as backup/training**:
   - GazeCapture, Lund2013, NVGaze, OpenEDS
   - Use while waiting for IRB or equipment setup

### Phase 4: Set Up Workstation

**Primary workstation:** work2 (100.100.252.99)

**SSH access approach:** Use `sshpass` for batch setup, then instruct student to change password.

```bash
# Install sshpass first (one-time on local machine)
sudo apt install -y sshpass
```

> ⚠️ **sshpass timeout trap**: `sshpass` may timeout on commands that take >10s (npm install, uv install). **Always split into short individual SSH calls** (5-15s each). Never batch `npm install + curl | sh + apt` into one sshpass command.
> 
> ❌ `sshpass -p '<pw>' ssh student@host 'big long script with npm install'` → times out
> ✅ `sshpass -p '<pw>' ssh student@host 'curl -LsSf https://.../install.sh | sh'` → works
> ✅ Then next SSH call for npm install with timeout ≥ 60s.
> 
> Alternatively, create a setup script locally, `scp` it to the remote machine, then execute it (avoids the timeout).

Standard setup checklist:

1. **Account**: `sudo useradd -m -s /bin/bash -c '姓名拼音' 用户名` (done by system admin)
2. **Login**: SSH with password (initial), recommend changing after first login
3. **Core tools**:
   - `uv` (Python package manager) — install via `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Python 3.14+ with venv at `~/workspace/eye-tracking/.venv/`
   - Scientific stack: `numpy, scipy, opencv-python, matplotlib, pandas, jupyter, scikit-learn`
6. **Codex CLI** (the lab's primary coding assistant):

```bash
# Install via nvm and npm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm install --lts
npm install -g @openai/codex

# Codex config — local vLLM (work2 runs vLLM natively at localhost:8000)
mkdir -p ~/.codex
cat > ~/.codex/config.toml << 'CFG'
model = "qwen3.6-35b-nvfp4"
model_provider = "vllm"

[model_providers.vllm]
name = "vLLM"
env_key = "VLLM_API_KEY"
base_url = "http://localhost:8000/v1"
wire_api = "responses"

[projects."/home/<student>"]
trust_level = "trusted"

[projects."/home/<student>/workspace"]
trust_level = "trusted"

[projects."/home/<student>/projects"]
trust_level = "trusted"

[ask_for_approval]
policy = "never"

[sandbox]
mode = "danger-full-access"

[shell_environment_policy]
inherit = "all"

[features]
hooks = true
goals = true
memory = true
CFG
```

> **Tip**: vLLM runs locally on work2 at localhost:8000 with qwen3.6-35b-nvfp4. No external API key needed — set VLLM_API_KEY to any dummy value.

5. **Hermes Agent** (the lab's AI research assistant):

```bash
# Install
pipx install hermes-agent

# Verify
hermes --version

# Config — local vLLM
mkdir -p ~/.hermes
cat > ~/.hermes/config.yaml << 'CFG'
model:
  default: qwen3.6-35b-nvfp4
  provider: custom:local

custom_providers:
- name: local
  base_url: http://localhost:8000/v1
  api_key: EMPTY
  model: qwen3.6-35b-nvfp4

agent:
  max_turns: 150
  gateway_timeout: 1800
  tool_use_enforcement: auto
CFG
```

> **Tip**: vLLM runs locally on work2 at localhost:8000 with qwen3.6-35b-nvfp4. No external API key needed — set VLLM_API_KEY to any dummy value.

7. **Workspace structure**:
   ```
   ~/workspace/
     eye-tracking/        # 主项目（含 .venv）
     papers/              # 论文相关
   ~/projects/
     3d-eye-tracking/    # 代码仓库
   ~/data/
     raw/                 # 原始数据
     results/             # 分析结果
     datasets/            # 公开数据集
   ~/scripts/
   ```
8. **Git config**: `git config --global user.name` + `git config --global user.email`
9. **GitHub SSH key**: Guide student to generate and add to GitHub account
10. **OpenCode**: Install and configure API key\n\n**Supporting file**: `references/work2-environment.md` for exact paths, IPs, and credentials.

### Phase 5: First-Week Plan

Provide a concrete Day 1-7 schedule:

| Day | Task | Deliverable |
|:----|:-----|:------------|
| 1 | Login + read training plan + GitHub SSH key | Working SSH + git access |
| 2 | Run dual-ellipse demo code | First running figure |
| 3-5 | Explore public dataset + basic stats | First plot (distribution) |
| 6-7 | Draft abstract + intro | 300-word abstract for review |

### Phase 6: Establish Cadence

| Phase | Meeting Frequency | Focus |
|:------|:-----------------|:------|
| First month | Weekly (30min) | Unblock + direction check |
| Paper writing | Biweekly | Results + draft review |
| Second paper+ | Monthly | Progress check |
| Emergency | Anytime (WeChat/Feishu) | Blocked >2 hours |

## Pitfalls

- **Don't over-plan the tool phase**: user explicitly corrected "months of tool learning" → compress to 1-2 weeks.
- **Don't assume student can code**: medical background students may have zero programming. Rely on OpenCode/Codex for code generation, focus student on clinical understanding.
- **Don't delete competition/private repos without checking**: always check if there's an external repo with the same content before removing.
- **First paper topic should be narrow**: 3D Kappa angle distribution, or 3D vs 2D pupil localization comparison. Not a full system paper.
- **SSH key for GitHub**: private repos need authentication. Student must generate (`ssh-keygen`) and add to GitHub Settings → SSH Keys themselves.
- **APT/OS-level installs need sudo**: ask for password; use `sshpass -p <password>` for one-off setup, then set up passwordless sudo.
- **sshpass security**: Hermes blocks `|-sudo -S|` (pipe password to sudo). Use `sshpass` for user-level setup only (no sudo needed). If sudo is required, ask the user to either pre-configure the account or provide `SUDO_PASSWORD` in `.env`.
- **vLLM is local on work2**: localhost:8000 — no network dependency, no auth needed. Set VLLM_API_KEY to any dummy value. This is faster and more reliable than routing through external servers.
- **First paper topic must be narrow**: 3D Kappa angle distribution, or 3D vs 2D pupil localization comparison. Not a full system paper.
- **Repository cloning fails without SSH key**: Private GitHub repos need auth. List them as a post-setup step for the student to complete.

## Reference Files
- `references/work2-environment.md` — work2 server details, IPs, credentials, paths.
- `templates/training-plan.md` — Training plan template to customize per student.

## Related Skills
- project-health-audit — for repo-level structure cleanup
- project-experience-distillation — for extracting patterns from student projects back into skills

## Appendix: Research Convergence Enforcement

When redefining research scope (e.g., from broad exploration to focused depth), update these system components:

| Component | Action |
|:----------|:-------|
| **Memory** | Write the convergence decision as a durable fact |
| **Cron: autonomous-core-researcher** | Update prompt: list allowed + prohibited directions explicitly |
| **Cron: paper-repair** | Add scope constraint — only repair in-scope papers |
| **Cron: paper-quality-review** | Skip out-of-scope papers |
| **Cron: paper-layer-b-review** | Skip out-of-scope papers |
| **Cron: literature-monitor** | Core directions → full report; peripheral → appendix only |

Scope tiers:
- **Core** (全流程): 5 pillars + Synthos + teaching + algorithm components + public dataset analysis
- **Peripheral** (仅空白+假设): cornea/lens/vitreous/tear film/tinnitus/concussion biomechanics

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


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

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
