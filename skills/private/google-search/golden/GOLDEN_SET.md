---
name: google-search
description: GOLDEN_SET.md
---

# 金测集: google-search

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试：SerpAPI 引擎搜索，验证输出契约 {title, url, snippet, p | 见 expected/case_001.json |
| case_002 | 降级链测试：SearXNG 引擎集体 ConnectTimeout 时正确诊断并切换出口 IP（GO | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
