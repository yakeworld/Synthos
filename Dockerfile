# =============================================================================
# Synthos — Autonomous Research Agent Platform
# Docker image: one-command deploy of Hermes Agent + Synthos cognitive atoms
# =============================================================================

FROM python:3.11-slim-bookworm AS base

LABEL org.opencontainers.image.title="Synthos"
LABEL org.opencontainers.image.description="Autonomous Research Agent — Hermes Agent + Synthos Cognitive Atoms"
LABEL org.opencontainers.image.version="4.3.1"
LABEL org.opencontainers.image.source="https://github.com/yakeworld/Synthos"

# System deps
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
    curl git nodejs npm jq \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash hermes
WORKDIR /home/hermes

# Install Hermes Agent
RUN curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh \
    | bash -s -- --skip-setup 2>&1 | tail -5

ENV PATH="/home/hermes/.local/bin:${PATH}"

# Python extras
RUN pip install --quiet --no-cache-dir \
    pymupdf mcp litellm Pillow python-pptx

# Copy Synthos project
COPY --chown=hermes:hermes . /synthos

# Link skills
RUN mkdir -p /home/hermes/.hermes/skills && \
    for d in /synthos/skills/*/; do \
        name=$(basename "$d"); \
        ln -sf "$d" "/home/hermes/.hermes/skills/$name"; \
    done

# Pre-configure config.yaml
RUN mkdir -p /home/hermes/.hermes && \
    cp /synthos/docker/hermes-config.yaml /home/hermes/.hermes/config.yaml && \
    chown hermes:hermes /home/hermes/.hermes/config.yaml

# Install entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER hermes
ENTRYPOINT ["/entrypoint.sh"]
