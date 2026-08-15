# GOLDEN_SET — dsh-self-evolution

## Golden 用例: connectivity (2026-08-16 实测)

- 输入: `bash -lc 'dsh --profile headless "<创建文件任务>"'`
- 期望输出: 文件 `/media/yakeworld/sda2/Synthos/dsh-synthos-connectivity-test.txt` 内容 `SYNTHOS_DSH_OK`
- 实测结果: PASS (exit 0, 文件已创建)
- 负例: 非登录 shell 调用 → `MISSING_CREDENTIAL: llm-pi-ai: no credential for provider route "vllm"` (预期失败)

## 判定标准

1. 连通性: dsh headless 能完成简单文件任务且 exit=0
2. 单轮耗时 < 5 分钟（简单任务）
3. 复杂任务（≤15 文件改进）< 30 分钟，超时按任务失败处理
