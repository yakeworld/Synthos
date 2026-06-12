---
name: serving-llms-vllm
desc
## 原理层·文言

> 文以验法，技乃所产。Deploy, manage, and interact with vLLM for high-throughput LLM serving.。
ription: Deploy, manage, and interact with vLLM for high-throughput LLM serving.
  Covers Docker-based deployment, model loading, coexistence with training, API usage,
  quantization (NVFP4/GPTQ/GGUF), and performance tuning. Captures the user's specific
  deployment on work1 (Qwen3.6-35B-NVFP4, TP=4).
allowed-tools:
- terminal
- read_file
- write_file
- search_files
license: MIT
dependencies: []
metadata:
  synthos:
    author: Synthos Agent
    signature: 'model: str, config: dict -> endpoint_url: str'
    related_skills:
    - crispdm-helix-experiment
    - experiment-recipes
    - huggingface-hub
    - medical-image-centerline
    - remote-gpu-training
    version: 1.0.0
    tags:
    - vllm
    - serving
    - inference
    - llm
    - docker
    - mlops
---


# vLLM Serving — High-Throughput LLM Serving

## Trigger

- User asks to start, stop, check, or configure a vLLM server
- User asks to query a model served via OpenAI-compatible API
- User mentions model deployment, Docker-based LLM serving, or NVFP4/GPTQ quantization

## Work1 Deployment (This User's Setup)

The user has a production vLLM deployment on **work1** (NF5468, 8× RTX 4090).

### Container Details

| Field | Value |
|-------|-------|
| **Container** | `vllm-qwen3-nvfp4` |
| **Image** | `vllm/vllm-openai:latest` (22.6GB) |
| **Model** | `/mnt/nfs/models/Qwen3.6-35B-A3B-NVFP4` (host) → `/model` (container) |
| **Port** | `8000` (host) → `8000` (container) |
| **GPUs** | TP=4 (4× RTX 4090) |
| **Status** | Currently **Exited** — do NOT start during active training |

### Exact Start Command (from container inspect)

```bash
docker start vllm-qwen3-nvfp4
```

### CLI Arguments (original run)

```bash
docker run -d --gpus all \
  --name vllm-qwen3-nvfp4 \
  -p 8000:8000 \
  -v /mnt/nfs/models/Qwen3.6-35B-A3B-NVFP4:/model \
  vllm/vllm-openai:latest \
  --model /model \
  --served-model-name qwen3.6-35b-nvfp4 \
  --tensor-parallel-size 4 \
  --trust-remote-code \
  --dtype auto \
  --max-model-len 262144 \
  --kv-cache-dtype fp8 \
  --enable-prefix-caching \
  --max-num-seqs 24 \
  --language-model-only \
  --max-num-batched-tokens 4096 \
  --default-chat-template-kwargs '{"enable_thinking": false}' \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder
```

### Model Details

- **Model**: Qwen3.6-35B-A3B-NVFP4 (NVIDIA FP4 quantized)
- **Path**: `/mnt/nfs/models/Qwen3.6-35B-A3B-NVFP4/`
- **Format**: 3 safetensors shards (model.safetensors, model_mtp.safetensors, config.json, chat_template.jinja)
- **Architecture**: MoE (3.6B dense, 30B sparse), NVFP4 quantized
- **Context**: 262k tokens (131072 native + extended)

## Basic Usage

### Check Server Status

```bash
# From host
curl -s http://localhost:8000/v1/models

# Check container logs
docker logs vllm-qwen3-nvfp4 --tail 20

# Check GPU usage
nvidia-smi --query-compute-apps=pid,used_memory,name --format=csv,noheader
```

### Query the Model (OpenAI-compatible API)

```bash
curl -s http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.6-35b-nvfp4",
    "messages": [{"role": "user", "content": "Hello, what is 2+2?"}],
    "max_tokens": 100
  }' | python3 -m json.tool
```

### Query via Python

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")
resp = client.chat.completions.create(
    model="qwen3.6-35b-nvfp4",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(resp.choices[0].message.content)
```

### For Hermes Agent (configure provider)

```yaml
# ~/.hermes/config.yaml
gateways:
  work1:
    provider: openai
    api_base: http://work1:8000/v1
    api_key: not-needed
    model: qwen3.6-35b-nvfp4
```

## Coexistence with Training ⚠️

**CRITICAL: vLLM consumes significant GPU resources.** The Qwen3.6-35B-NVFP4 model uses TP=4, occupying 4× RTX 4090s simultaneously. This WILL interfere with training jobs.

- Do NOT start vLLM when training is active (check `nvidia-smi` first)
- If training is running, wait for it to complete or ask the user
- Check vLLM container status: `docker ps -a | grep vllm` — should be `Exited` during training
- Only start when user explicitly asks, and all GPUs are free

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs vllm-qwen3-nvfp4 --tail 50

# Common failures:
# - GPU memory exhaustion: nvidia-smi to check utilization
# - Model path missing: check /mnt/nfs/models/<model>/
# - NFS mount issue: df -h /mnt/nfs

# Full reset: remove and recreate
docker rm vllm-qwen3-nvfp4
# (then use the docker run command above with same args)
```

### Model Fails to Load

- Check shard files exist: `ls /mnt/nfs/models/Qwen3.6-35B-A3B-NVFP4/*.safetensors`
- Verify NFS mount: `df -h /mnt/nfs` (should show 10.20.43.5:/volume1/nfs)
- Watch for OOM in docker logs

## Pitfalls

1. **vLLM blocks training resources** — TP=4 uses 4 GPUs. Never start vLLM alongside training. Check with `nvidia-smi` first.
2. **container start vs run** — the container already exists. Use `docker start vllm-qwen3-nvfp4` to resume, not `docker run` which creates a duplicate. If you need a clean start, explicitly `docker rm` first.
3. **NVFP4 requires specific CUDA** — the image has CUDA 12.9. Host driver must be ≥535 (work1 has 580.142 — OK).
4. **Custom all-reduce disabled** — RTX 4090s are PCIe-only; `custom allreduce is disabled` in logs is normal, not a failure.
5. **SymmMemCommunicator warning** — `Device capability 8.9 not supported` is expected for RTX 4090 (sm_89). Harmless.

## See Also

- `remote-gpu-training` — GPU job management alongside vLLM on work1
- `hermes-agent` — configuring vLLM as a provider for Hermes gateway
