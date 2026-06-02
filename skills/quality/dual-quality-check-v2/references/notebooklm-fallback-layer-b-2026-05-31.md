# NotebookLM 降级实战：Pima CRISP-DM Layer B 手动七维评审（2026-05-31）

## 背景

NotebookLM CLI 上传41篇参考文献PDF+编译论文后，所有源显示`status=error`和`Unknown source type code 0`。尝试 `--new` 开始新对话，结果删除了服务器端全部对话历史，且新对话中 `ask` 返回 "I couldn't find enough context"。触发降级协议。

## 降级步骤

### 1. PDF文本提取

```bash
# 途径A (pdftotext) - 首选
pdftotext 01-manuscript/pima-crispdm-v3.pdf /tmp/pima-paper.txt

# 途径B (PyPDF2) - 后备
python3 -c "
from PyPDF2 import PdfReader
r = PdfReader('01-manuscript/pima-crispdm-v3.pdf')
with open('/tmp/pima-paper.txt', 'w') as f:
    for i, p in enumerate(r.pages):
        f.write(f'--- Page {i+1} ---\n')
        f.write(p.extract_text() + '\n')
"

# 结果: 1682行文本, 37.9KB
```

### 2. 逐段精读

逐段读取文本（每300-400行），记录:
- 论文结构: IMRaD, 22页, 41篇参考文献
- 核心方法: CRISP-DM Helix框架, 34个基线模型, 5x2 CV paired t-test
- 关键结果: F1=0.7541, Recall=0.7500, Lambda=0.090, +8.6% F1 inflation
- 局限性: 仅PIDD单一数据集, SHAP视觉估算, RandomizedSearchCV

### 3. 七维评分

| 维度 | 评分 | 关键依据 |
|:-----|:----:|:---------|
| D1 科学贡献 | 0.84 | 系统审计50篇+框架形式化定义, 但PIDD非新数据集 |
| D2 方法学 | 0.90 | 5x2 CV t-test, 34模型, 嵌套CV, 形式化假设 |
| D3 结果可信 | 0.88 | 适中报表, 消融量化解, 但仅单一数据集 |
| D4 完整性 | 0.85 | IMRaD完整, 但无外部验证 |
| D5 清晰性 | 0.82 | 重复段落+长句, 图表自说明不足 |
| D6 新颖性 | 0.72 | 泄漏结论已建立, 框架复用scikit-learn, 无算法创新 |
| D7 引用质量 | 0.82 | 41篇充足, 但arXiv/低影响因子占比较多 |
| **平均** | **0.83** | |

### 4. 保存报告

保存为 `07-quality/layer-b-qc.md`，包含:
- 逐维评分卡(1. Strengths 2. Weaknesses 3. Recommendations)
- 历史评分对比表 (vs 2026-05-22)
- 关键修复项P0-P4排序

## 关键教训

1. **`--new` 不可逆**: 销毁全部对话历史, 在新会话中源可能无法立即使用
2. **手动评审更严格**: 手动评分(0.83) vs 历史Gemini评分(0.86) 低0.03
3. **PDF文本提取质量**: pdftotext提取的公式/表格格式混乱, 但正文内容完整可读
4. **D6最敏感**: 手动评审对"已知想法的重新包装"类贡献的评分低于Gemini

## 用户反馈

用户未对降级方法提出异议，接受了手动评审结果作为Layer B.
