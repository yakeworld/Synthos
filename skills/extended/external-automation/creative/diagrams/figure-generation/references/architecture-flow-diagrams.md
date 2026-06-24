# 架构/流程图程序化布局 (matplotlib patches)

> 2026-06-24 新增, PIMA-CRISP-DM Figure 1 实战沉淀

## 适用场景

- 科研论文中的系统架构图、流程图、模块关系图
- 非定量展示（不包含数据面板、坐标轴）
- SCI期刊出版级输出

反例：带误差棒/统计检验的定量图 → 用 `quantitative-grid` 原型。

## 核心原则

1. **一切从变量计算，不手写坐标**
2. **从底部向上计算 y 位置**（保证页面最底部元素不溢出）
3. **统一设计系统**：单行框高、双行框高、间隙大小全部用常量定义
4. **框形态一致**：所有 FancyBboxPatch 用同一 `pad` 值
5. **生成前 QA 验证**：文字不超框、箭头不悬空

## 设计系统变量

| 变量 | 推荐值 | 控制内容 |
|:----|:------:|:---------|
| `SINGLE_H` | 0.50" | 单行文字框高 (fs=6.5~7, ~0.20"文字 + padding) |
| `DOUBLE_H` | 0.70" | 双行文字框高 (核心/输出/消融/注册箱) |
| `BOX_W` | ≥3.0" | 侧栏框宽 (≥3.0避免"Engineering Execution Strand"碰边) |
| `CORE_W` | 4.8" | 核心框宽 |
| `BOT_W` | 5.2" | 底部链框宽 |
| `PAD_BOX` | 0.12 | 所有框统一内边距 |
| `GAP_S` | 0.20" | 同区框间距 |
| `GAP_M` | 0.55" | 区间隔 |
| `GAP_T` | 0.35" | 标题间距 |

## 色板

| 元素 | 颜色 | 用途 |
|:-----|:-----|:------|
| 方法论/临床 | `#8BCF8B` (Nature绿) | Clinical Credibility Strand |
| 工程/执行 | `#E8954A` (橙) | Engineering Execution Strand |
| 核心/创新 | `#7B5EA7` (紫) | CRISP-DM Helix Core |
| 输出/结果 | `#D0E8D0` (浅绿底) | Output Benchmark |
| 消融/比较 | `#F0E8C0` (浅黄底) | Ablation Study |
| 基线/参考 | `#F0C8C8` (浅红底) | Dataset Baseline Registry |

## 箭头连接类型

1. **侧栏→核心**: 从子箱底部垂直引出，汇聚到核心顶边内侧 1/4 和 3/4 处 (弧度 rad=±0.20)
2. **核心→下一级**: 从核心底边垂直引出，进入下一箱体的顶边
3. **底部链**: 依次垂直连接，最后一条用虚线
4. **折线 (备用)**: `(x1,y1) -- ++(0,-offset) -| (x2,y2)` 先直下再横折再直下

## 文件名规范

- 生成脚本: `<project>/03-code/generate_figN.py`
- 输出: `<project>/05-figures/figN_<name>.pdf`
- LaTeX 引用: `\includegraphics[width=0.85\textwidth]{../05-figures/figN_<name>.pdf}`

## QA 验证 (生成前强制)

脚本必须在 `plt.subplots()` 之前嵌入 `QAReport` 类：

```python
def text_width_inches(text, fontsize_pt):
    return len(text) * fontsize_pt * 0.60 / 72.0

class QAReport:
    def __init__(self): self.issues = []
    def check_text_fits(self, label, text, fs, bw, bh, pad):
        tw = text_width_inches(text, fs)
        avail_w = bw - 2*pad; avail_h = bh - 2*pad
        if tw > avail_w: self.issues.append(...)
        if fs/72 > avail_h: self.issues.append(...)
    def check_arrow_inside(self, label, x2, y2, tn, tx, ty, tw, th):
        if not (tx <= x2 <= tx+tw and ty <= y2 <= ty+th):
            self.issues.append(...)
    def assert_clean(self):
        if self.issues: sys.exit(1)  # 不输出无效PDF
```

**必须为每个 box 配一个 check_text_fits，每个 arrow 配一个 check_arrow_inside。**
