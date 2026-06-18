---
name: powerpoint
description: >-
  创建/读取/编辑.pptx — python-pptx: 幻灯片/表格/模板。
  覆盖环境陷阱（sandbox venv无包→系统Python）、复杂表格、
  多页模板化PPTX生成。关联 skill: nature-paper2ppt。
metadata:
  synthos:
    version: 1.4.0
    author: Synthos
    signature: 'skill_set: pptx_files -> presentation: bytes'
    related_skills:
    - nature-paper2ppt
    - pil-image-generation
---

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）


# PowerPoint (.pptx) Generation

创建/读取/编辑.pptx — python-pptx: 幻灯片/表格/模板。

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
# 1. 写脚本到文件（/tmp/gen_pptx_*.py 或 project/code/gen_pptx.py）
# 2. /usr/bin/python3 /tmp/gen_pptx_*.py
# 或：
# 2. /home/yakeworld/.local/share/pipx/shared/bin/python3 /tmp/gen_pptx_*.py
```

## 页面尺寸陷阱（⚡P0 — 新）

PPT页面尺寸：**宽13.333英寸，高7.5英寸**。所有元素边界必须在此范围内。

### 宽度计算
- 双栏布局：每栏≤3.4英寸（左4.5 + 右2×3.4 = 11.3 ✅）
- 三栏布局：每栏≤2.8英寸（5.1 + 3×2.8 = 13.5 需左移0.2 → 4.9+3×2.8=13.3 ✅）
- 总公式：`left_width + num_cols × col_width ≤ 13.333`

### 高度计算
- 可用高度 ≈ 7.5 - 标题(0.4) - 分隔线(0.1) - 页脚页码(0.3) = **6.7英寸**
- 多行卡片：`y_start + (num_rows-1) × row_height + card_height ≤ 7.5`
- 当页面放不下：先精简左侧，再调整右侧布局

### 列索引计算（⚡P0 — 新）
**绝对不要**用复杂条件链：`col=0 if i<2 else (1 if i<4 else (2 if i<6 else 0))`
→ `i=0` 和 `i=1` 都得到 `col=0`，重叠！

**正确做法**：`col = i % num_cols; row = i // num_cols`（均匀分布）
生成后验证：打印前10个 `(i, row, col)` 确认无重复。

### 完美网格数量
| 项目数 | 推荐布局 |
|--------|---------|
| 4 | 2×2 |
| 6 | 3×2 |
| 8 | 2×4 或 4×2（完美填满）|
| 9 | 3×3 |
| 7 | 2×4（末行空1，比3列2行好）|

**用户偏好**：尽量凑偶数（4/6/8/12），避免奇数导致末行空缺。

## 安全区溢出（⚡P0 — 新）

LibreOffice导出PDF会裁剪超出 **12.8"×7.0"** 的元素。页面默认13.333"×7.5"，所有元素坐标用`Inches()`计算，1英寸=914400 EMU。

**安全策略**：将所有`Inches(N)`（N>0）乘以0.92系数，可安全保持在12.3"×6.9"内。例如：`Inches(1.0)`→`Inches(0.92)`，`Inches(7.5)`→`Inches(6.9)`。注意`Inches(0)`不变（如背景起始坐标 `Inches(0)`）。

**审查公式**：`(shape.left + shape.width) / 914400` 应 ≤ 12.8，`(shape.top + shape.height) / 914400` 应 ≤ 7.0。

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

## 字体基线（⚡P0）

**用户偏好大字号 + 宽松行距。** 字体体系分层：

| 层级 | 字号 | 用途 | 示例 |
|:-----|:----:|:-----|:-----|
| 页面标题 | 24-26pt | `pg()` 函数 | "标志性成果一：..." |
| 卡片标题 | 13-15pt | 分区标题 | "精选成果"、"三大核心卖点" |
| 正文/描述 | 11pt | 卡片内说明文字 | 项目描述、维度说明 |
| 微文字 | 9pt | 专利号等辅助信息 | "(ZL2017...)" |
| 核心大数字 | 44-48pt | `bn()` 大数 | "21"、"101.9" |
| 大数字后缀 | 14pt | `bn()` 的 sub | "篇"、"万" |
| 大数字单位 | 12pt | `bn()` 的 unit | "项目负责人经费" |

**行间距**：`mtx()` 函数内每段 `p.space_after = Pt(5)`，`tx()` 函数内 `p.space_after = Pt(4)`。

**框高利用率**：文本占框高≥60%为佳。若框内文字仅占30-40%高度，框应缩小或字体加大。禁止9pt以下正文。

## 图像优先布局（⚡P0 — 竞赛/答辩PPT）

标志性成果页必须配图，图片应占页面 40-60% 面积。

| 成果类型 | 配图策略 | 来源 |
|:---------|:---------|:-----|
| 系统/软件 | 封面图 + 架构图 | 系统文档 PNG |
| 硬件/设备 | 实物照片 + 架构流程图 | 转化PPT / 项目图 |
| 理论/算法 | 3D重建图 + 公式可视化 + 中心线图 | 论文 figures |

布局模式：**左图右文** 或 **上图下文**。图片嵌入用 `s.shapes.add_picture(path, left, top, width, height)`，宽高按原始比例等比缩放（先 `from PIL import Image; img = Image.open(path)` 获取尺寸再计算）。

## 交付前质量门（⚡P0）

**PPT生成后、告知用户完成前，必须执行三步验证：**

1. **L0.5 数据诚实门** — 对照原始申报书/规范文档逐条验证姓名、职称、学历、专利号、经费、论文数等硬事实。不得近似。

2. **布局数学检查** — 运行 `scripts/quality_check.py <pptx_path>` 检测：
   - 形状溢出（right > 13.333" 或 bottom > 7.5"）
   - 子元素超出父卡片边界
   - 同级元素重叠

3. **规范一致性检查** — 若用户提供了设计规范文档，逐页对比：
   - 标题措辞是否完全一致（"领军" vs "领航"）
   - 元素是否跨页移动（联系方式在指定页）
   - 是否自行添加了规范未列的数据/标签
   - 卡片布局结构是否匹配（分组 vs 独立卡、箭头链 vs 方框）

**违反任一步骤 → 修复后再交付。禁止先交付后修复。**

## 设计规范执行力（⚡P0）

**当用户提供了逐页设计规范文档时，严格照搬，不做任何以下操作：**

| 禁止行为 | 说明 |
|:---------|:-----|
| 添加非规范字段 | 不在页面中添加规范未列的履历/头衔/数据 |
| 移动元素跨页 | 联系方式等元素严格放置在规范指定的页面 |
| 增加额外大数字 | 规范列出几个数据块就做几个，不自行补充 |
| 改变卡片布局结构 | 规范说分类分组就分组，不改为独立卡片 |
| 改箭链为独立卡 | 规范有箭头连接链就保留箭头，不改方框卡片 |
| 修改标题措辞 | 规范写"领军"就不写成"领航" |

**核心原则：规范即内容。不增不减不改不挪。**

## 字体基线（⚡P0 — 新）

**用户偏好大字号 + 宽松行距。** 字体体系分层：

| 层级 | 字号 | 用途 | 示例 |
|:-----|:----:|:-----|:-----|
| 页面标题 | 24-26pt | `pg()` 函数 | "标志性成果一：..." |
| 卡片标题 | 13-15pt | 分区标题 | "精选成果"、"三大核心卖点" |
| 正文/描述 | 11pt | 卡片内说明文字 | 项目描述、维度说明 |
| 微文字 | 9pt | 专利号等辅助信息 | "(ZL2017...)" |
| 核心大数字 | 44-48pt | `bn()` 大数 | "21"、"101.9" |
| 大数字后缀 | 14pt | `bn()` 的 sub | "篇"、"万" |
| 大数字单位 | 12pt | `bn()` 的 unit | "项目负责人经费" |

**行间距**：`mtx()` 函数内每段 `p.space_after = Pt(5)`，`tx()` 函数内 `p.space_after = Pt(4)`。

**框高利用率**：文本占框高≥60%为佳。若框内文字仅占30-40%高度，框应缩小或字体加大。禁止9pt以下正文。

## 交付前质量门（⚡P0 — 新）

**PPT生成后、告知用户完成前，必须执行三步验证：**

1. **L0.5 数据诚实门** — 对照原始申报书/规范文档逐条验证姓名、职称、学历、专利号、经费、论文数等硬事实。不得近似。详见 `references/ppt-quality-review-checklist.md`。

2. **布局数学检查** — 运行 `scripts/quality_check.py <pptx_path>` 检测：
   - 形状溢出（right > 13.333" 或 bottom > 7.5"）
   - 子元素超出父卡片边界
   - 同级元素重叠
   
3. **规范一致性检查** — 若用户提供了设计规范文档，逐页对比：
   - 标题措辞是否完全一致（"领军" vs "领航"）
   - 元素是否跨页移动（联系方式在指定页）
   - 是否自行添加了规范未列的数据/标签
   - 卡片布局结构是否匹配（分组 vs 独立卡、箭头链 vs 方框）

**违反任一步骤 → 修复后再交付。禁止先交付后修复。**

## 设计规范执行力（⚡P0）

**当用户提供了逐页设计规范文档时，严格照搬，不做任何以下操作：**

| 禁止行为 | 说明 | 示例 |
|:---------|:-----|:-----|
| 添加非规范字段 | 不在页面中添加规范未列的履历/头衔/数据 | P2加了"学历/民进/政协/重点实验室" |
| 移动元素跨页 | 联系方式等元素严格放置在规范指定的页面 | 把email/手机号从P10移到了P2 |
| 增加额外大数字 | 规范列出几个数据块就做几个，不自行补充 | P4加了"121技能树"大数字 |
| 改变卡片布局结构 | 规范说分类分组就分组，不改为独立卡片 | P5规范三组分类→做成了8张独立卡 |
| 改箭链为独立卡 | 规范有箭头连接链就保留箭头，不改卡片 | P6-P8左栏规范箭头→做成了方框卡片 |
| 修改标题措辞 | 规范写"领军"就不写成"领航" | P1标题 |

**核心原则：规范即内容。不增不减不改不挪。**

## 照片替换模式

将占位框替换为真实图片。参考 `references/photo-placeholder-replacement.md`。

## 脚本存放约定

所有PPTX生成脚本统一存到项目目录 `code/` 子目录，**不要存 `/tmp`**：
- `/tmp` 随 session 消失，跨 session 无法复用
- 项目 `code/` 目录：可审查、可追溯、可继承
- 示例：`~/瓯越英才申报材料/code/gen_pptx.py`

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
    sldId_full = re.findall(r'<p:sldId id="(\\d+)" r:id="(rId\\d+)"/>', pres_xml)
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