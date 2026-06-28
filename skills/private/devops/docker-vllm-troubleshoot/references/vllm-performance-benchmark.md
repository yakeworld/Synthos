# vLLM 吞吐量基准测试方法论

> 记录时间: 2026-06-19
> 场景: 检测 vLLM 服务器性能退化，决定切换服务器

## 基准测试流程

### 1. 快速连通性检查

```bash
curl -s --max-time 5 http://<ip>:8000/v1/models | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Model: {d[\"data\"][0][\"id\"]}')"
```

### 2. 吞吐量测量

```bash
# 发送简单请求测量时间
start=$(date +%s%N)
curl -s http://<ip>:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.6-35b-nvfp4","messages":[{"role":"user","content":"Write 1000 Chinese characters about mathematics."}],"max_tokens":1100,"temperature":0.7}' \
  > /tmp/bench.json
end=$(date +%s%N)

# 解析结果
python3 -c "
import json
with open('/tmp/bench.json') as f:
    d = json.load(f)
u = d['usage']
c = d['choices'][0]['message']['content']
tps = u['completion_tokens'] * 1000 / elapsed_ms if elapsed_ms > 0 else 0
print(f'completion_tokens: {u[\"completion_tokens\"]}')
print(f'completion_time: {elapsed_ms}ms')
print(f'throughput: {tps:.1f} tok/s')
print(f'actual_chars: {len(c)}')
"
```

### 3. 判定标准

| 吞吐量 | 状态 | 操作 |
|--------|------|------|
| > 150 tok/s | 正常 | 继续使用 |
| 100-150 tok/s | 注意观察 | 继续测试几次 |
| < 100 tok/s | 异常 | 检查原因，准备切换 |
| < 50 tok/s | 严重退化 | 立即切换备用服务器 |
| 超时 (>60s) | 不可用 | 立即切换 |

### 4. 跨服务器切换

测试多个服务器后，选择性能最优的作为主端点。

**实测对比 (2026-06-19):**

| 服务器 | 平均吞吐 | 延迟 | 状态 |
|--------|----------|------|------|
| 100.82.27.51 (旧) | 120 tok/s | 8.3 ms/tok | 退化 (曾降到30 tok/s) |
| 100.125.10.93 (新) | 176 tok/s | 5.69 ms/tok | 正常 |

**切换步骤：**
1. 更新 `.hermes/config.yaml` 的 `model.base_url`
2. 更新 `.codex/config.toml` 的 `model_providers.vllm.base_url`
3. 保持旧服务器作为 `custom_providers` 的 fallback
4. 验证切换后连通性：`curl http://<new-ip>:8000/v1/models`

## Pitfalls

- **冷启动惩罚**: 第一个请求慢（PTH 重加载），warmup 后恢复正常
- **curl 超时**: 测试长输出时确保 timeout > 60s
- **字符 vs token**: 中文输出 char/token ≈ 2，但 benchmark 用 `completion_tokens` 更准确
- **服务器负载波动**: 单次测量可能有噪声，至少测 3 次取中位数
- **混合语言 prompt**: NotebookLM ask 对中文 prompt 可能有安全扫描，但 vLLM 直接调用不受影响