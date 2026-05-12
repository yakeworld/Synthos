#!/bin/bash
set -e

# Synthos Docker Entrypoint
# Configures API keys from environment variables, then launches Hermes.

ENV_FILE="/home/hermes/.hermes/.env"
> "$ENV_FILE"

write_key() {
    local var="$1"
    local val="${!var}"
    if [ -n "$val" ]; then
        echo "$var=$val" >> "$ENV_FILE"
    fi
}

write_key DEEPSEEK_API_KEY
write_key SEMANTIC_SCHOLAR_API_KEY
write_key OPENROUTER_API_KEY
write_key ANTHROPIC_API_KEY
write_key OPENAI_API_KEY
write_key PUBMED_API_KEY

cd /synthos

if [ $# -eq 0 ]; then
    exec hermes --skills "task-router" --profile default
else
    exec "$@"
fi
