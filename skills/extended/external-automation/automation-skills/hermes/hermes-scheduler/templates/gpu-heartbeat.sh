#!/usr/bin/env bash
# gpu-heartbeat.sh — 监测本地节点GPU和vLLM端点状态
# 用途：无Agent cron任务，定期检查推理节点健康度
# 位置：~/.hermes/scripts/gpu-heartbeat.sh

check_node() {
  local name="$1"
  local url="$2"
  
  if status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$url/v1/models" 2>/dev/null); then
    model_info=$(curl -s --connect-timeout 5 "$url/v1/models" 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    models = [m['id'] for m in d.get('data', [])]
    n = len(models)
    if n > 0:
        print(f'{n} models: {\",\".join(models)}')
    else:
        print('empty response')
except:
    print('parse failed')
" 2>/dev/null)
    echo "✅ ${name} (${url}) — OK — ${model_info}"
    return 0
  else
    echo "❌ ${name} (${url}) — FAIL (HTTP ${status})"
    return 1
  fi
}

check_gpu() {
  local name="$1"
  if command -v nvidia-smi &>/dev/null; then
    gpu=$(nvidia-smi --query-gpu=name,memory.total,temperature.gpu --format=csv,noheader,nounits 2>/dev/null | head -5)
    if [ -n "$gpu" ]; then
      echo "🔥 ${name} GPU:"
      echo "$gpu"
    fi
  fi
}

echo "=== GPU Heartbeat — $(date '+%Y-%m-%d %H:%M:%S') ==="
echo ""

check_node "amax (主节点)"    "http://100.100.252.99:8000"
check_node "amax-fallback (备节点)" "http://100.82.27.51:8000"
echo ""
check_gpu "Hermes主节点"
check_gpu "amax-fallback"
