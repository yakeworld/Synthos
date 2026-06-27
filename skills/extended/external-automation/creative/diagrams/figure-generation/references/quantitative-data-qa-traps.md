# 定量数据图视觉 QA 陷阱记录

## Session: 2026-06-27 HCS-3WT Breast Cancer Paper Figures

### 通用规则（适用于所有定量数据图）

#### Rule 1: 重叠/高聚合值曲线必须多维度区分
**问题**: ROC 曲线上 5 个模型的 AUC 都在 0.985+，曲线在左上角高度重叠，仅用不同颜色无法区分。
**修复**: 使用**线形 + 标记形状**双重编码：
- Solid line + circle
- Dashed line + square
- Dotted line + triangle
- Dash-dot line + diamond
- Dashed line + inverted triangle
**规则**: ≥3 条曲线时，仅靠颜色不够。必须组合 line style + marker shape 区分。

#### Rule 2: 图例内联 vs 图表外部
**问题**: 内联图例可能遮挡数据曲线。
**修复**: ROC 等高聚合曲线 → 图例放左下角或外部。指标表放图表外部下方（用 ax.text 的负 y 偏移），不要放在 plot area 内部。

#### Rule 3: 子图指标框必须统一对齐
**问题**: 混淆矩阵子图中某个指标框位置偏移，颜色也不一致。
**修复**: 所有子图的 metrics box 使用完全相同的参数：
- 相同的 `ax.text()` 位置（0.5, -0.28，即 x 居中，y 低于 axes）
- 统一的 `facecolor='#F0F4F8'`，仅 `edgecolor` 用模型对应色
- 相同的 `bbox=dict(boxstyle='round,pad=0.12', ...)` 参数
- 相同的 `fontfamily='monospace'` + `fontweight='bold'`

#### Rule 4: 水平条形图 — 颜色编码必须有图例
**问题**: 按特征类型（worst-case vs mean-case）用不同颜色，但缺少图例，读者无法理解颜色含义。
**修复**: 
- 当按语义类别着色时，必须添加 `ax.legend()`
- 图例位置放在右下角（`loc='lower right'`），不遮挡数据
- 颜色语义在图例中明确说明（"Worst-case features" / "Mean-case features"）

#### Rule 5: 水平条形图 — 右侧空间必须干净
**问题**: 条形图 x 轴上限设置过大（0.40 vs 最大条 0.32），右侧产生大片空白。
**修复**: 
- x 轴上限设为 `max_value * 1.28`（约 28% 余量），不要设死值
- 右侧区域只放图例和脚注，不放空白
- 使用 `fig.savefig(..., bbox_inches='tight')` 确保裁剪

#### Rule 6: 网格图 — 低值标签必须额外间距
**问题**: 消融研究图中 Random 模型的 AUC=0.500 与 x 轴下限 0.55 重叠，导致 "Random 0.500" 文字不可读。
**修复**: 
- x 轴下限设为 `min_value - 0.05`（给低值标签留出空间）
- 低值（<0.7）的标签使用额外偏移 `x_offset=0.008`，高值用 `0.003`
- 检查所有 value label 是否超出 xlim

#### Rule 7: 双面板图 — 共享 Y 轴设计
**问题**: 双面板趋势图中两个 panel 的 Y 轴范围必须严格一致，否则视觉对比误导。
**修复**: 
- 两个 panel 使用相同的 `ylim`（如 0-0.65）
- 左 panel 的图例放右上角，右 panel 放左上角，避免重叠
- 阴影区域颜色：Primary metric 用主色 alpha=0.2，其他指标不填充
- 阈值线（`axvline`）颜色统一为红（`#B64342`），标注用 `bbox` 框高亮

#### Rule 8: 表格内联 — 不要放 plot area 内部
**问题**: 内联表放在 ROC plot 区域，遮挡了灰色随机线。
**修复**: 
- 指标表放在 axes 外部（y < -0.1），使用 `ax.text()` 的 `transform=ax.transAxes`
- 或使用 `fig.text()` 放在 figure 级别
- 永远不要把表格放在 `ax.set_xlim/ylim` 定义的区域内

#### Rule 9: 标题与页脚的层级
**问题**: 多层标题/页脚挤在一起（fig.suptitle → ax.set_title → fig.text → ax.text）。
**修复**: 
- `fig.suptitle`: fontsize 9-10, fontweight='bold', y=0.97
- `ax.set_title`: fontsize 8-9, pad=5-12
- `fig.text` footer: fontsize 6, style='italic', color='#999999', y=0.01-0.02
- 确保各层级之间至少有 0.1 的垂直间距

### 本会话修复汇总

| Figure | 问题 | 修复 |
|--------|------|------|
| fig2 ROC | 5条曲线重叠，内联表遮挡 | 线形+标记双编码；表格移至 plot 下方 |
| fig3 CM | 指标框位置不一致、颜色不统一 | 统一 text 位置、facecolor、bbox参数 |
| fig4 FI | 无图例、右侧大空白 | 添加 legend；x-limit 动态计算 |
| fig5 AS | Random 标签重叠（0.500 vs 0.55 xlim） | xlim 下延至 0.42；低值额外 offset |
| fig6 TS | 无显著问题 | ✅ 通过 |
