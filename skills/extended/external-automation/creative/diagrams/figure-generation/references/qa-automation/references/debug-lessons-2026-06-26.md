# Debug Lesson: figure-qa-check — 2026-06-26

## Session Context

用户质疑"你是不是还缺乏一个技能，就是自己检查这个图？"要求对 HCS-3WT Figure 1 生成代码进行自动化 QA 验证。

## 发现的 4 个关键陷阱

### Trap 1: AABB vs (x,y,w,h) 格式混淆

**症状**: 所有文本错误匹配到 input_box，即使是 (7.0, 9.15) 这样远在画布上方的文本。

**根因**: `boxes_raw` 存储 (x_min, y_min, width, height)，但 `determine_text_box` 解包为 `(bx, by, bw, bh)` 后计算 `bx + bw`。当 `bw` 已经是 x_max（而非 width）时，`bx + bw = x_max + x_max` 得到荒谬的右边界值（如 14.0 而非 8.7）。

**修复**: 在 `build_qa_input` 中将 `(x,y,w,h)` 转换为 `(x_min, y_min, x_max, y_max)`，然后所有函数统一使用 AABB 格式。

**验证**: 修复后 (7.0, 9.15) → NO BOX（正确）。

### Trap 2: 字面 `\n` vs 真实换行符

**症状**: "Uncertain\nCases" 报告左溢出 0.10in，但运行时测量显示不溢出。

**根因**: `re.finditer` 捕获源文件中的 `"Uncertain\nCases"` 为 16 字符（含反斜杠+n），但 matplotlib 实际渲染时 `\n` 是换行符，每行独立渲染。静态估算 16 字符宽度 vs 运行时最长行宽度，差异 70%+。

**修复**: `parse_ax_text_calls()` 中 `text.replace('\\n', '\n')`。

**验证**: 修复后 "Uncertain\nCases" 左溢出错误消失。

### Trap 3: fontsize 多行提取

**症状**: 当 `ax.text()` 调用跨多行时，同一行正则匹配不到 `fontsize=`。

**根因**: 源文件代码格式：
```python
ax.text(7, 7.5, "Text...", ha="center", va="center",
        fontsize=7.5, color="#777777")
```
fontsize 在第二行，单行正则无法捕获。

**修复**: 行-based 搜索，从文本所在行起搜索后续 2 行。

### Trap 4: 静态估算严重不准确

**静态估算**: `len(text) * fontsize * 0.55 / 72` → 37字符 × 7.5 × 0.55/72 = 2.12in
**精确测量**: `get_text_extent` → 0.105in
**差异**: 2000%+

**说明**: 静态估算仅用于快速预估，不可作为 QA 依据。`figure_qa_check` 使用 `get_text_extent` 精确测量，最终报告是准确的。

## 验证矩阵

| 场景 | 静态估算 | 精确测量 | 是否准确 |
|------|----------|----------|----------|
| "PowerTransformer" fontsize=7.5 | bottom=6.44 (wrong) | bottom=7.4475, overflow=0.1025in ✅ | 精确测量准确 |
| "Uncertain\nCases" fontsize=8 (no \n fix) | left=0.105 ❌ | N/A (未运行) | 静态估算误报 |
| "Uncertain\nCases" fontsize=8 (with \n fix) | N/A | left=0.33, no overflow ✅ | 精确测量准确 |

## 最终结论

- `figure-qa-check.py` 检测到的 1 个错误（PowerTransformer 溢出）经运行时 `get_window_extent` 验证为**真实有效**
- 另一个错误（Uncertain\nCases）经修复 `\n` 处理后**消除**
- 脚本作为独立类级别技能创建：`figure-qa-check`
