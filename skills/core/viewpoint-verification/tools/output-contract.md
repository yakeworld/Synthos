---
name: tool-verification-output
category: tool
description: viewpoint-verification 输出契约 — 验证报告 JSON + Markdown、Bayesian 评分结构
version: 1.0.0
---

# 验证输出契约

> **工程层**：本文档只定义输出交付的工具契约（路径、格式、内容结构）。
> 反方观点、证伪条件、Bayesian 评分逻辑见上层 `viewpoint-verification/SKILL.md`（哲学层）。

## 输出交付（Step 6）

```bash
mkdir -p outputs/{session}/
python3 -c "import json; json.dump(verification_report, open('outputs/{session}/verification.json','w'), indent=2, ensure_ascii=False)"
cat > outputs/{session}/verification_report.md << 'EOF'
# 验证报告: {假设名称}

## 可证伪性
✅ 可证伪 — 3个可检验反例条件

## Bayesian 置信度
先验: 0.70 → 后验: 0.85（中等支持）
EOF
```

## 产出清单

| 文件 | 格式 | 内容 |
|------|------|------|
| `outputs/{session}/verification.json` | JSON (UTF-8, indent=2) | verification_report 结构化（反方观点/证伪条件/似然比/后验） |
| `outputs/{session}/verification_report.md` | Markdown | 人类可读验证报告（可证伪性 + Bayesian 置信度） |

## 错误处理

| 症状 | 处置 |
|------|------|
| 输出目录不存在 | 先 `mkdir -p outputs/{session}/` |
| JSON 中文乱码 | 必须 `ensure_ascii=False` |
| 后验缺失 | Bayesian 评分未完成，报告不得输出 |
