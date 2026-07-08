# Docker image for Hermes Agent — 一键即用
# Build: docker build -t hermes-agent:latest docker/
# Run:   docker run -it -e API_KEY=xxx hermes-agent:latest
# Run+GUI: docker run -it -p 8080:8080 -e API_KEY=xxx hermes-agent:latest
# Mount Synthos skills: docker run -it -v ~/Synthos/skills:/root/synthos-skills -e API_KEY=xxx hermes-agent:latest

FROM ubuntu:24.04

# Suppress interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install base dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && echo 'export PATH="/root/.local/bin:$PATH"' >> /root/.bashrc

# Install Node.js 22 LTS (for OpenCode CLI)
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash \
    && export NVM_DIR="$HOME/.nvm" \
    && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" \
    && nvm install --lts \
    && nvm alias default --lts

# Set environment
ENV PATH="/root/.local/bin:$NVM_DIR/versions/node/v22*/bin:$PATH"
ENV NVM_DIR="/root/.nvm"

# Upgrade pip and install pipx
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pipx && \
    pipx ensurepath

# Install Hermes Agent
RUN pipx install hermes-agent

# Install OpenCode CLI
RUN npm install -g @ai-sdk/opencode

# Create work directory
WORKDIR /workspace

# Copy default configuration
RUN mkdir -p /root/.hermes /root/.config/opencode /workspace

# Default Hermes config
COPY docker/hermes-config.yaml /root/.hermes/config.yaml

# Default OpenCode config (minimal — user adds API keys)
COPY docker/opencode-config.json /root/.config/opencode/opencode.json

# Verify script
COPY docker/verify.sh /usr/local/bin/verify.sh
RUN chmod +x /usr/local/bin/verify.sh

# Default entrypoint
ENTRYPOINT ["tini", "--"]
CMD ["/bin/bash"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD hermes chat -q "test" -Q || exit 1