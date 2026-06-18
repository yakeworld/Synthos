# NotebookLM 驱动的专利点数学原理提取

## 用途

在专利挖掘流程中，利用 NotebookLM 逐问法从研究源码、笔记、文献中提取核心技术方案的数学原理。提取结果可直接用作专利交底书 "三、技术方案详细阐述" 中 3.5 节（关键技术参数）和 3.2-3.4 节（系统框图和流程）的数学支撑。

## 工作流

```
Step 1:  创建/选择 NotebookLM 项目
          notebooklm use <project_id>

Step 2:  提取坐标系定义
          notebooklm ask "请解释坐标系定义和基础矢量"

Step 3:  提取核心公式推导
          notebooklm ask "请详细说明公式推导过程和关键变换"

Step 4:  提取闭式解
          notebooklm ask "最终的闭式解公式是什么？"

Step 5:  提取技术实现细节
          notebooklm ask "如何通过3D眼动追踪系统测量每个步骤？"

Step 6:  跨项目验证（如需）
          notebooklm use <project_B_id>
          notebooklm ask "请从另一个角度解释相同原理"
```

## 示例：VOR-Kappa角闭式标定

```bash
# 项目A：Kappa角数学推导
notebooklm use 571024b4 && notebooklm ask "详细解释如何通过三维眼动数据推算Kappa角，重点说明数学公式和坐标变换方法"

# 项目B：VOR神经网络设计（验证是否有冲突视角）
notebooklm use e9b9ee07 && notebooklm ask "关于Kappa角的数学原理"

# 捕获结果 → 直接进入patent-disclosure流程的Step 7（交底书生成）
```

## 关键技巧

| 场景 | 做法 |
|:-----|:-----|
| 需要数学公式 | 在 ask 中加"请说明数学公式和坐标变换方法" |
| 需要对比传统方法 | 加"本方法与传统方法的核心区别是什么" |
| 需要验证新颖性 | 加"是否不需要XXX？"这类否定确认问题 |
| 公式输出为LaTeX | NotebookLM自动输出LaTeX公式，可直接用于交底书 |
| 跨项目提取 | 使用 `use && ask` 链（见 notebooklm-cli pitfall#10） |
| summary 失败 | 直接跳过，执行 `ask`（见 notebooklm-cli pitfall#9） |
