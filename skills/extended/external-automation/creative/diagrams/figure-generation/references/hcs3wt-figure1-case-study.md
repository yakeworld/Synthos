# HCS-3WT Figure 1 案例研究：文字/箭头重叠检测实战

> 2026-06-26，HCS-3WT 乳腺癌论文 Figure 1 重叠修复

## 核心发现：文字超框的精确检测方法

### 关键方法：`fig.canvas.get_renderer()` 获取精确 text bounding box

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(1, 1))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

def get_text_extent(text, fontsize, fontweight='normal'):
    """精确测量 matplotlib 文字渲染尺寸（英寸）。"""
    text_obj = ax.text(0, 0, text, fontsize=fontsize, fontweight=fontweight)
    fig.canvas.draw()
    bbox = text_obj.get_window_extent(fig.canvas.get_renderer())
    bbox_fig = bbox.transformed(fig.transFigure.inverted())
    w = bbox_fig.width   # 英寸
    h = bbox_fig.height  # 英寸
    text_obj.remove()
    return w, h
```

### 发现的实际问题

1. **PowerTransformer** 文本在 Input Box 内 y=7.20（va="center"），计算得文字高度 0.105 英寸 → 文字占据 y=[7.148, 7.252]。Input Box 底部 y=7.15 → 文字超出 0.0025 英寸。**肉眼看不出来，代码测量发现。**

2. **arrow1** 终点 (7.0, 6.95) 未进入 ExpertB 框（ExpertB top=6.7）。箭头悬在框外 0.25 英寸。

3. **arrow_BtoC / arrow_AtoC** 终点 (2.4, 1.85) 未进入 ExpertC 框（ExpertC top=1.65）。

### 修复措施

- Input Box subtitle: y=7.20→7.25（va="center"，文字不再超出）
- arrow1: 终点改为 (4.5, 6.65)，斜向右下进入 ExpertB
- arrow_BtoC/AtoC: 终点改为 (2.4, 1.60)，进入 ExpertC
- arrow2/3/6: 终点 x=5.3→5.4，进入目标框
- annotation "Uncertain Cases" 从 ExpertA 内部移到两列间空白

### 经验教训

- 肉眼看不出 0.0025 英寸的文字溢出 → QA 必须用代码测量，不能靠目测
- 箭头终点"接近"框边缘不算进入——必须严格在边界内
- 水平箭头和垂直箭头的终点判断方式不同：垂直看 y，水平看 x
