#!/bin/bash
# 快速检查三节点vLLM集群状态
# 用法: bash scripts/quick-node-check.sh

IPS=("100.100.252.99" "100.125.10.93" "100.82.27.51")
NAMES=("amax" "amax-backup" "amax-fallback")

echo "=== vLLM 三节点集群状态 ==="
for i in "${!IPS[@]}"; do
  ip="${IPS[$i]}"
  name="${NAMES[$i]}"
  
  # Try curl first (faster than SSH)
  status=$(curl -s --connect-timeout 3 http://$ip:8000/v1/models 2>/dev/null)
  if [ $? -ne 0 ] || [ -z "$status" ]; then
    echo "$name ($ip): ❌ UNREACHABLE"
    continue
  fi
  
  model=$(echo "$status" | python3 -c "import json,sys; d=json.load(sys.stdin); m=d['data'][0] if d.get('data') else {}; print(f'{m.get(\"id\",\"?\")} ctx={m.get(\"max_model_len\",\"?\")}')" 2>/dev/null)
  
  # Container uptime via docker
  uptime=$(curl -s --connect-timeout 3 http://$ip:8000/v1/models 2>/dev/null && echo "✅" || echo "❌")
  
  echo "$name ($ip): $model"
done

echo ""
echo "=== Provider 配置一致性 ==="
python3 -c "
import yaml
c = yaml.safe_load(open('/home/yakeworld/.hermes/config.yaml'))
print('Hermes custom_providers:')
for p in c['custom_providers']:
    print(f'  {p[\"name\"]}: {p[\"base_url\"]}')
print(f'model.provider: {c[\"model\"][\"provider\"]}')
print(f'delegation.provider: {c[\"delegation\"][\"provider\"]}')
" 2>/dev/null

echo ""
echo "=== Codex base_url ==="
grep 'base_url' ~/.codex/config.toml 2>/dev/null || echo "  config.toml not found"
