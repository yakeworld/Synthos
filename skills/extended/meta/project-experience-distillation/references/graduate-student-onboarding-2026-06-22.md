# Graduate Student AI Research Environment Onboarding

> Pattern extracted from setting up 郭梓豪 (guozihao) on work2 workstation (2026-06-22).

## Context

A new research-oriented master's student joins the lab with:
- Medical background (no strong coding skills)
- Basic familiarity with OpenCode/Codex CLI
- Needs a complete AI-assisted research environment

## Onboarding Workflow

### Step 1: System Account (requires sudo)

```bash
sudo useradd -m -s /bin/bash -c 'Student 中文名' username
sudo passwd username  # set initial password
```

### Step 2: Workspace Structure

```bash
mkdir -p ~/workspace/{eye-tracking,papers,skills}
mkdir -p ~/projects/3d-eye-tracking
mkdir -p ~/data/{raw,results,datasets}
mkdir -p ~/scripts
```

### Step 3: Python Environment

```bash
# Install uv (fast package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project venv with scientific stack
cd ~/workspace/eye-tracking
uv venv .venv
source .venv/bin/activate
uv pip install numpy scipy opencv-python matplotlib pandas jupyter scikit-learn
```

Add to `~/.bashrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
source ~/workspace/eye-tracking/.venv/bin/activate
```

### Step 4: Codex CLI

```bash
# Install Node.js via nvm (no sudo needed)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm install --lts

# Install Codex
npm install -g @openai/codex

# Configure ~/.codex/config.toml
cat > ~/.codex/config.toml << 'CFG'
model = "qwen3.6-35b-nvfp4"
model_provider = "vllm"

[model_providers.vllm]
name = "vLLM"
env_key = "VLLM_API_KEY"
base_url = "http://localhost:8000/v1"
wire_api = "responses"

[projects."/home/username"]
trust_level = "trusted"

[projects."/home/username/workspace"]
trust_level = "trusted"

[ask_for_approval]
policy = "never"

[sandbox]
mode = "danger-full-access"

[shell_environment_policy]
inherit = "all"
CFG

# Set API key (dummy for local vLLM)
echo 'export VLLM_API_KEY=***' >> ~/.bashrc
```

### Step 5: Hermes Agent

```bash
pipx install hermes-agent

# Configure ~/.hermes/config.yaml
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

security:
  sandbox:
    enabled: false
CFG
```

### Step 6: Git Configuration

```bash
git config --global user.name "Student Name"
git config --global user.email "student@wmu.edu.cn"
ssh-keygen -t ed25519  # add public key to GitHub
```

### Step 7: Training Plan

Copy a structured training plan (with timelines, milestones, paper targets) to `~/workspace/`.

## Pitfalls

1. **sudo password**: Workstations may require interactive sudo. Use `echo 'password' | sudo -S` is blocked by Hermes security. Better: set up passwordless sudo or have the user create the account first.
2. **sshpass timeout**: Long piped commands via `sshpass` may timeout. Break into smaller steps or use `expect`.
3. **Codex sandbox**: `codex exec` may fail with `bwrap: Failed RTM_NEWADDR` on some machines. Use `codex --yolo exec` instead.
4. **vLLM local**: Check if vLLM runs on the same workstation (`localhost:8000`) or a separate server before configuring base_url.
5. **Hermes version**: v0.15+ uses `chat` subcommand instead of `run`. The CLI help shows available commands.
