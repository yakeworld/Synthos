# Paper Writing via NotebookLM: Iterative Q&A Protocol

> 2026-05-28 实战：SCC 3D对数螺旋模型论文完整构建。
> 核心原则：所有内容必须通过 NotebookLM ask 从源文件提取，不直接从 AI 记忆写。

## 四轮Q&A协议（从文献→论文）

### Round 1：文献知识提取

从已上传的源文件（PDF、MD）中提取关键信息：

```
Q1: Bradshaw2010的SCC数学模型的方程是什么？用了什么假设？参数多少？RMSE？
Q2: Rabbitt2019的经典扭转摆模型方程？截面假设？Reynolds数？
Q3: Santina2005测量了什么参数？标本量？是否正交？
Q4: David2016的方法？对比骨vs膜？
```

目的：建立Introduction的事实基础。

### Round 2：空白定位

基于Round 1的提取结果，定位研究空白：

```
Q5: 有没有文献提出闭合形式参数方程？（对照本研究的核心创新）
Q6: 有没有文献系统比较骨vs膜中心线参数？
Q7: 非平面度有没有被量化过？
Q8: 椭圆截面解耦阻尼-灵敏度有没有被提出过？
```

目的：确认Innovation claim的可信度。

### Round 3-4：逐节写作

```
Round 3 → Introduction + Methods
Round 4 → Results + Theory  
Round 5 → Discussion + Conclusion
```

每个Round的 prompt 必须包含：
1. 已有的数据分析结果（数值表）
2. 需要引用的文献
3. 需要回答的具体科学问题

### Round 5：双质检

作为 Layer B Gemini 评审：
```
Q: 请对论文进行全面7维SCI评审（D1-D7），每维评分+改进建议
```

## 保存规范

每个Q&A的输出保存到 `{paper_dir}/tmp/qa_r{N}_{topic}.txt`

```
paper_dir/
├── tmp/
│   ├── qa_r1_q1.txt (Bradshaw知识提取)
│   ├── qa_r1_q2q3.txt (Rabbitt+Santina)
│   ├── qa_r2_gap.txt (空白定位)
│   ├── qa_r3_intro_methods.txt (Introduction+Methods)
│   ├── qa_r4_results_theory.txt (Results+Theory)
│   ├── qa_r5_discussion.txt (Discussion+Conclusion)
│   └── layerB_review.txt (7维评审)
├── paper.tex
└── paper.pdf
```

## 被禁止的做法

- ❌ 直接在 execute_code/terminal 中写 LaTeX 正文（无源文件追溯）
- ❌ 跳过 NotebookLM 的文献导入，仅凭 AI 训练数据记忆写论文
- ❌ 一次问多个不相关问题（违反逐问法原则）
