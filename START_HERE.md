# START_HERE — 30分钟搭建你的 AI 研究助手

> Synthos 生态的 Hermes Agent + OpenCode 一键入门指南。
> 目标：**拷即用** — 最少手动操作，最多自动配置。

---

## Level 0: 只想体验（5分钟，无需安装）

直接复制下面的命令，在任意 Linux/macOS 终端跑：

```bash
# 体验 Hermes Agent 的聊天能力
pipx install hermes-agent  # 一次性
hermes chat -q "写一段 Python 计算瞳孔椭圆3D法向量" -Q
```

或者直接克隆 Synthos 仓库，用任意 AI Agent 加载技能：

```bash
git clone https://github.com/yakeworld/Synthos.git
# Agent 加载 skills/task-router/SKILL.md 即可开始
```

---

## Level 1: 本地完整环境（20分钟）

### 一键安装脚本

```bash
# 下载并运行
curl -sSf https://raw.githubusercontent.com/yakeworld/hermes-starter/main/install.sh | bash
```

> 目前 install.sh 正在开发中，预计 2026-07 上线。
> 手动安装步骤见下方。

### 手动安装步骤

**Step 1: 基础环境**
```bash
# Python 3.12+
python3 --version

# 安装 uv（包管理，比 pip 快10倍）
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

**Step 2: 安装 Hermes Agent**
```bash
pipx install hermes-agent
hermes --version
```

**Step 3: 安装 OpenCode CLI**
```bash
# Node.js (via nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm install --lts
npm install -g @ai-sdk/opencode
opencode --version
```

**Step 4: 配置 API Key（唯一手动步骤）**

编辑 `~/.hermes/.env`：
```bash
# 添加你的 API Key
export CUSTOM_API_KEY="sk-xxx..."
```

**Step 5: 验证**
```bash
# 1. Hermes 能响应
hermes chat -q "test" -Q

# 2. OpenCode 能列出模型
opencode models

# 3. 两者共存不冲突
codex --version && opencode --version
```

---

## Level 2: 科研级部署（30分钟）

### 2.1 接入本地 vLLM（零成本推理）

```bash
# 假设 vLLM 在 localhost:8000
# 编辑 ~/.hermes/config.yaml
cat > ~/.hermes/config.yaml << 'EOF'
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
EOF
```

### 2.2 接入 Synthos 技能库

```bash
git clone https://github.com/yakeworld/Synthos.git ~/Synthos

# 在 ~/.hermes/config.yaml 中添加
skills:
  external_dirs:
    - ~/Synthos/skills
```

### 2.3 完整验证

```bash
# 所有检查通过 = 部署成功
hermes chat -q "计算瞳孔椭圆3D法向量" -Q
opencode -m hermes/qwen3.6-35b-nvfp4
```

---

## 工具关系图

```
┌─────────────────────────────────────────────────┐
│              用户 (超级个体)                      │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼──────┐          ┌──────▼──────┐
│Hermes    │          │ OpenCode    │
│ Agent    │          │ CLI         │
│          │          │             │
│ 工具链   │          │ 编码主力   │
│ 任务编排 │          │ 多模型切换 │
│ 消息网关 │          │ 项目工作流 │
└────┬─────┘          └──────┬──────┘
     │                       │
     └──────────┬────────────┘
                │
      ┌─────────▼──────────┐
      │   模型层            │
      │                    │
      │  本地 vLLM (免费)  │  ← 日常编码
      │  OpenCode Zen      │  ← 复杂推理
      │  付费 Provider     │  ← 图像/高级模型
      └────────────────────┘
```

---

## 常见问题

**Q: Hermes 和 OpenCode 什么区别？**
A: Hermes 是智能体框架（工具链+任务编排+消息），OpenCode 是编码CLI（多模型切换+项目工作流）。两者互补，不互相替代。

**Q: 需要 GPU 吗？**
A: 体验版不需要（用云端API）。科研级部署建议有 GPU 跑本地 vLLM，零成本。

**Q: 能用在非科研场景吗？**
A: 可以。Hermes 是通用 AI 智能体框架。Synthos 技能库是科研方向的，但 Hermes 核心可以服务任何场景。

**Q: 配置文件放哪？**
A:
- Hermes: `~/.hermes/config.yaml` + `~/.hermes/.env`
- OpenCode: `~/.config/opencode/opencode.json` + `~/.local/share/opencode/auth.json`
- Codex: `~/.codex/config.toml`

**Q: 三者能共存吗？**
A: 能。Codex、OpenCode、Hermes 配置独立、二进制独立，互不干扰。

---

## 下一步

1. 跑通 Level 1 → 验证基本可用
2. 接入 Synthos 技能库 → 获得科研能力
3. 配置 cron job → 自动化日常任务
4. 加入社区 → 分享你的使用经验

**问题/建议？→ [GitHub Issues](https://github.com/yakeworld/Synthos/issues)**