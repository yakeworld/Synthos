---
name: powerpoint
description: >-
  创建/读取/编辑.pptx — python-pptx: 幻灯片/表格/图表/模板。
  覆盖环境陷阱（sandbox venv无包→系统Python）、复杂表格、
  多页模板化PPTX生成。关联 skill: nature-paper2ppt。
metadata:
  synthos:
    version: 1.2.0
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
| pipx/shared env 的 lxml ABI 与 sandbox python 不兼容 | 始终用 pipx shared python 或系统 python3，不用 sandbox venv |
| python-pptx 多处可能损坏（.local/、myenv/） | 始终用 `/home/yakeworld/.local/share/pipx/shared/bin/python3` 作为可靠源 |
| 函数名与变量名冲突（如 `card` 既是函数又是列表变量） | 命名严格区分：`mkcard()` 函数、`card` 变量 |

```bash
# 正确做法：
# 1. 写脚本到文件（/tmp/gen_pptx_*.py）
# 2. /usr/bin/python3 /tmp/gen_pptx_*.py
# 或：
# 2. /home/yakeworld/.local/share/pipx/shared/bin/python3 /tmp/gen_pptx_*.py
```

## 关键 API 陷阱

- **`from pptx import Presentation` — 没有 `Document`**：python-pptx 的入口类是 `Presentation`，不是 `Document`。`Document` 是 `python-docx` 的。
- **`Paragraph.add_run()` 不接受参数**：必须 `r = p.add_run()` 然后 `r.text = "text"`，不能用 `p.add_run("text")`。
- **Title 布局（layout[0]）无 `.subtitle` 属性**：用 `placeholders[1]` 或向 title text_frame 追加 paragraph。
- **`font.name` 当前系统用 `'微软雅黑'`**，不是 `'Microsoft YaHei'`。
- **cell访问**: `cell.text_frame.paragraphs`（非 `cell.paragraphs`）→ 详见 `references/python-pptx-table-cell-pitfall.md`
- **word_wrap**: 必须显式设置 `cell.text_frame.word_wrap = True`
- **表格样式**: 每行交替背景色用 `i % 2`；header行用不同颜色
- **交付物质量审查**: 任何PPT/申报材料需通过L0.5数据诚实门——对照原始申报书逐条验证学历/专利号/经费/团队/版本等所有数值。详见 references/ppt-quality-review-checklist.md
- **多页模板**: 定义 helper 函数（`header()`, `footer()`, `snum()`, `shp()`, `tb()`, `mkcard()`）统一风格
- **add_slide layout**: 空 Presentation 用 `prs.slide_layouts[6]`（BLANK），已有PPT用 `[0]`（TITLE）或 `[1]`（CONTENT）
- **形状填充**: `MSO_SHAPE.RIGHT_ARROW` 等形状默认 `_NoneFill`，必须先 `.fill.solid()` 再设 `fore_color.rgb`

## 脚本

| 路径 | 用途 |
|:-----|:-----|
| scripts/add_slide.py | 添加带统一格式的幻灯片 |
| scripts/clean.py | 清理模板PPTX |
| scripts/reorder_pptx.py | 通过zip修改ppt/presentation.xml重排幻灯片顺序（见references/python-pptx-direct-edit.md） |

## 多页PPTX生成模式

适用于竞赛答辩、项目申报、汇报场景的结构化PPTX生成：

1. **定义配色方案** — NAVY/DARK_BLUE/TEAL/GREEN/BLUE/GOLD 等5-7色 palette
2. **定义 helper 函数** — `header()`, `footer()`, `snum()`, `shp()`, `tb()`, `mkcard()`
3. **按页循环构建** — 每页一个代码块，保持结构清晰
4. **统一元素** — 页眉彩色条、页脚机构名、页码、卡片圆角矩形
5. **保存** — `prs.save(output_path)`

## ⚠️ 页面顺序调整陷阱（PPTX内部XML操作）

**核心发现（2026-06-09）**：python-pptx 维护两套sldId引用——`prs.slides._sldIdLst`（lxml Element）和 `prs.part._element` 中的sldIdLst。修改任何一套都不影响另一套，保存时用的是 `prs.part._element` 中的XML。`prs.slides._sldIdLst.sldId_lst` 是 property 无setter。

**可靠方案：zip直接修改XML（参见 scripts/reorder_pptx.py）**

```python
import zipfile, re
from pptx import Presentation

# 1. 用python-pptx创建新页面 → 保存到临时文件
prs.save("/tmp/temp.pptx")

# 2. 用zip修改ppt/presentation.xml中的sldIdLst
with zipfile.ZipFile("/tmp/temp.pptx", 'r') as zin:
    pres_xml = zin.read('ppt/presentation.xml')
    # 提取所有sldId
    sldId_full = re.findall(r'<p:sldId id="(\d+)" r:id="(rId\d+)"/>', pres_xml)
    # 新顺序：历史版0-5 + 新页面(索引12-13) + 历史版6-11
    new_order = sldId_full[0:6] + sldId_full[12:14] + sldId_full[6:12]
    # 重建
    new_block = '\n'.join(f'    <p:sldId id="{s}" r:id="{r}" />' for s, r in new_order)
    replacement = '<p:sldIdLst>\n' + new_block + '\n  </p:sldIdLst>'
    new_xml = re.sub(
        r'(<p:sldIdLst>).*?(</p:sldIdLst>)',
        replacement,
        pres_xml.decode(),
        flags=re.DOTALL
    )
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        zout.writestr('ppt/presentation.xml', new_xml.encode())
        for m in zin.namelist():
            if m != 'ppt/presentation.xml':
                zout.writestr(m, zin.read(m))
```

**关键注意点：**
- 新页面索引：`add_slide()` 追加到最后，所以索引 = 原页数...原页数+1
- `sldIdLst` tag 包含 `'sldIdLst'`（不是 `slideIdLst`！）
- `prs.part._element` 不是标准lxml Element（是CT_Presentation），迭代行为不确定
- `prs.slides._sldIdLst` 的parent是 `prs.part._element`，但修改children不影响保存
- `sldId_lst` 是property，`del lst[:]` + `extend()` 也不影响保存

参考 `references/python-pptx-direct-edit.md` 获取完整技术细节。

参考 `references/competition-material-preparation.md` 获取完整竞争类材料模板。