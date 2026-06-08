---
name: powerpoint
description: >-
  创建/读取/编辑.pptx — python-pptx: 幻灯片/表格/图表/模板。
  覆盖环境陷阱（sandbox venv无包→系统Python）、复杂表格、
  多页模板化PPTX生成。关联 skill: nature-paper2ppt。
metadata:
  synthos:
    version: 1.1.0
    author: Synthos
    signature: 'skill_set: pptx_files -> presentation: bytes'
    related_skills:
    - nature-paper2ppt
    - pil-image-generation
---

# PowerPoint (.pptx) Generation

创建/读取/编辑.pptx — python-pptx: 幻灯片/表格/图表/模板。

详细内容请加载对应 references/ 目录下的参考文件。

## 环境陷阱

| 陷阱 | 修复 |
|:-----|:-----|
| `execute_code` 沙盒 venv 无 python-pptx | 代码写入文件 → 用 `/usr/bin/python3` 执行 |
| 函数名与变量名冲突（如 `card` 既是函数又是列表变量） | 命名严格区分：`mkcard()` 函数、`card` 变量 |

```bash
# 正确做法：
# 1. 写脚本到文件（/home/yakeworld/gen_pptx.py）
# 2. /usr/bin/python3 /home/yakeworld/gen_pptx.py
```

## 核心陷阱

- **cell访问**: `cell.text_frame.paragraphs`（非 `cell.paragraphs`）→ 详见 `references/python-pptx-table-cell-pitfall.md`
- **word_wrap**: 必须显式设置 `cell.text_frame.word_wrap = True`
- **表格样式**: 每行交替背景色用 `i % 2`；header行用不同颜色
- **多页模板**: 定义 helper 函数（`header()`, `footer()`, `snum()`, `shp()`, `tb()`, `mkcard()`）统一风格
- **字体**: 必须设置 `font.name = 'Microsoft YaHei'` 保证中文字体正确渲染
- **add_slide layout**: 空 Presentation 用 `prs.slide_layouts[6]`（BLANK），已有PPT用 `[0]`（TITLE）或 `[1]`（CONTENT）
- **形状填充**: `MSO_SHAPE.RIGHT_ARROW` 等形状默认 `_NoneFill`，必须先 `.fill.solid()` 再设 `fore_color.rgb`

## 脚本

| 路径 | 用途 |
|:-----|:-----|
| scripts/add_slide.py | 添加带统一格式的幻灯片 |
| scripts/clean.py | 清理模板PPTX |

## 多页PPTX生成模式

适用于竞赛答辩、项目申报、汇报场景的结构化PPTX生成：

1. **定义配色方案** — NAVY/DARK_BLUE/TEAL/GREEN/BLUE/GOLD 等5-7色 palette
2. **定义 helper 函数** — `header(slide)`, `footer(slide)`, `snum(slide, n)`, `shp()`, `tb()`, `mkcard()`
3. **按页循环构建** — 每页一个代码块，保持结构清晰
4. **统一元素** — 页眉彩色条、页脚机构名、页码、卡片圆角矩形
5. **保存** — `prs.save(output_path)`

参考 `references/competition-material-preparation.md` 获取完整竞争类材料模板。