# NotebookLM 故障时的文献检索备用方案

## 触发条件
- NotebookLM source add 返回 400/500 错误
- NotebookLM ask 连续超时
- Notebook create/upload 失败

## 替代方案: web_search + delegate_task 5方向法

当 NotebookLM 不可用时，用 web_search + delegate_task 替代 P1 文献检索阶段：

### 5方向搜索法

对每个论文主题，并行搜索5个关键词方向：

```
方向(a): 核心方法术语 + "pupil localization" / "eye tracking" / "VOG"
方向(b): 核心技术 + "pupil fitting" / "ellipse fitting" / "iris thickness"  
方向(c): 建模方法 + "3D eye model" / "anatomical model" / "calibration"
方向(d): 相关参数 + "kappa angle" / "corneal reflection" / "gaze estimation"
方向(e): 边界技术 + "detection" / "refraction correction" / "boundary"
```

每个方向搜索3组关键词变体，每组带回 top 5-10 篇论文。

### 产出格式

```
## (a) 方向名
| 核心论文 | 年份 | 局限 |
|:---------|:----:|:------|

## Cross-cutting Gaps
| 创新点 | Novelty |
|:-------|:-------:|
```

### 执行方式

```python
delegate_task(
    goal="执行5方向文献检索并汇总",
    toolsets=["web"],
    context=paper_idea_description
)
```

### 与 NotebookLM 方案的关系
- web_search 方案产出不如 NotebookLM 详细（无全文理解），但覆盖速度和广度更优
- NotebookLM 恢复后应回传 Notebook 进行深度分析
- 混合方案：web_search 快速扫盲 + NotebookLM 深度逐问
