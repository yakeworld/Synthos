---
name: chinese-form-automation
description: "自动填写中文政府/教育/学术申请表格（docx+xlsx模板）。扫描版通知→OCR提取要求→分析模板结构→填充单元格→生成提交指引。适用于教师/医生/科研人员的中国高校、医院、政府机构表单填报。"
signature: "template: str, data: dict -> filled_form: str"
related_skills: [airtable, google-workspace, jupyter-live-kernel, linear, maps]
allowed-tools: [terminal, read_file, write_file, search_files]
version: 1.3.0
author: Hermes Agent + Synthos
license: MIT
metadata:
  hermes:
    tags: [form-filling, chinese, docx, xlsx, automation, ocr]
    related_skills: [ocr-and-documents]
---

# Chinese Form Automation — 中文表格自动填写

> 适用于中国高校/医院/政府机构的 docx + xlsx 模板表单填报。

## 核心流程

```
通知(扫描PDF) → OCR提取要求 → 分析附件模板结构 → 本地搜索用户信息 → 填充 → 提交指引
```

## Step 0: 文件接收与分析

用户上传的通常是三类文件（来自通知包）：

| 文件 | 格式 | 用途 |
|:-----|:-----|:-----|
| 遴选/申报通知 | 扫描PDF | 提取要求、时间、联系人 |
| 附件2-资格申请表 | docx | 个人填报，含表格 |
| 附件3-汇总表 | xlsx | 学院/单位汇总，含表格 |
| 附件1-管理办法 | PDF(可文字/扫描) | 提取选聘条件 |

## Step 1: 通知OCR（扫描PDF）

先用 `pdftotext` 检验文本层：
```bash
pdftotext notification.pdf - | wc -c
```

**< 100 chars → 扫描件，走 tesseract 路线：**
```bash
# 转图像
pdftoppm -png -r 300 notification.pdf /tmp/notice_page

# OCR（中文）
for f in /tmp/notice_page-*.png; do
  tesseract "$f" "${f%.png}" -l chi_sim 2>/dev/null
done
cat /tmp/notice_page-*.txt

# 提取关键信息：
# - 时间节点（如"6月1日前提交"）
# - 联系人/电话/邮箱
# - 提交材料清单
# - 盖章要求
```

**> 500 chars → 有文本层，直接读：**
```bash
pdftotext notification.pdf -
```

## Step 2: 附件1 管理细则解读（PDF/扫描）

同样用 `pdftotext` 或 `tesseract` 提取，关注：
- 选聘条件（职称、学历、年限要求）
- 申请流程
- 职责与管理规定

## Step 3: Docx 模板分析（附件2）

```python
from docx import Document

doc = Document('附件2.docx')
table = doc.tables[0]  # 一般申请表是第一个表格

# 打印所有单元格，定位标签和值字段的位置关系
for ri, row in enumerate(table.rows):
    for ci, cell in enumerate(row.cells):
        txt = cell.text.strip()
        if txt:
            print(f"[{ri},{ci}] '{txt[:40]}'")
```

**注意事项：**

### ⚠️ Merged Cell 核心陷阱（2026-05-27 实战教训）

**docx 合并单元格的底层行为：**
- 水平合并的多个单元格（gridSpan>1）共享同一个 XML `<tc>` 元素
- `table.cell(ri, ci)` 返回的 Cell 对象，对不同 (ri,ci) 坐标可能指向 **同一个 XML 节点**
- 写入一个单元格，**所有跨度的单元格同时改变** — 因为底层是同一个元素

**典型表现：**
```python
# 模板中 [1,0]~[1,4] 合并为 "专业领域" 标签
# 当你写入 cell(1, 1) 时，cell(1, 0) 的标签也会被覆盖
write_cell(table, 1, 1, '医学技术（神经病学）')
# → 结果：cell(1,0)='医学技术（神经病学）'，标签 "专业领域" 丢失 ❌
```

**❌ 错误做法（会丢失标签）：**
```python
# 清空所有单元格 → 含标签的合并单元格也被清空
for ri in range(9):
    for ci in range(8):
        cell = table.cell(ri, ci)
        for p in cell.paragraphs:
            for r in p.runs:
                r.clear()  # ❌ 标签被删掉
```

**✅ 正确做法：保留标签，增量追加内容**
```python
from docx import Document
doc = Document('模板.docx')
table = doc.tables[0]

# 不删除原有内容，直接对值单元格设置文本
# 对于 标签+值 合并的单元格，写值同时标签保留（在同一个cell内上下行）
val_cells = {
    (0, 1): '杨晓凯',    # 姓名值，独立单元格 → 安全写入
    (1, 1): '医学技术（神经病学）',  # 合并单元格 → 标签共享，一起显示
    (1, 7): '330324...',  # 独立值单元格
}

for (ri, ci), text in val_cells.items():
    cell = table.cell(ri, ci)
    # ✅ 不删已有段落/run，直接设文本
    cell.paragraphs[0].text = text

# 对于多行内容（工作经历、项目等），直接写在所在行的第一个单元格（合并区的anchor）
cell = table.cell(6, 0)
cell.paragraphs[0].text = '多行内容...'
```

**判定规则：**

| 单元格布局 | 行为 | 写法 |
|:-----------|:-----|:-----|
| 标签和值在不同单元格（非合并） | 各自独立，安全写入 | 分别写标签cell和值cell |
| 标签和值在合并单元格内 | 共享同一XML元素，写入即覆盖整个区域 | 直接写文本，标签自然保留在同一cell内 |
| 跨越多列的大字段（工作经历/项目） | 整行合并，anchor在col=0 | 写 cell(ri, 0) |

**验证方法：**
```python
# 写入后逐单元格检查，确认标签未丢失
for ri in range(9):
    for ci in range(8):
        txt = t.cell(ri, ci).text.strip()
        if txt:
            print(f'[{ri},{ci}] {txt[:50]}')
```

## Step 4: Xlsx 模板分析（附件3）

```python
import openpyxl

wb = openpyxl.load_workbook('附件3.xlsx')
ws = wb['汇总表']

# 查看合并单元格范围（避免写merged cell）
print(list(ws.merged_cells.ranges))

# 查看每行每列的值
for row in ws.iter_rows(min_row=1, max_row=5, values_only=False):
    for cell in row:
        print(f"[{cell.row},{cell.column}] coord={cell.coordinate}, val='{cell.value}'")
```

**注意事项：**
- **MergedCell 不可写入**：`MergedCell` 对象属性 `value` 是只读的，会抛 `AttributeError`
- **只写数据行**：表头行（标题行、表头行）通常是 merged，跳过；从第一个空数据行开始写
- **列对应关系**：通常是 序号、姓名、单位、专业领域、性别、出生日期、学历、学位、职称、职务、工作年限

```python
# 正确写法：跳过表头行，从数据行开始
vals = [1, '杨晓凯', 'INSTITUTION_NAME_PLACEHOLDER', '医学技术（神经病学）', ...]
for ci, v in enumerate(vals, 1):
    ws.cell(row=data_row, column=ci, value=v)
```

## Step 5: 个人信息本地搜索策略

填写前，从本地文件搜索用户个人信息：

```bash
# 搜索已知文件名模式
ls ~/文档/*.{md,txt,doc,docx,pdf} 2>/dev/null
ls ~/桌面/*.{md,txt} 2>/dev/null

# 搜索个人信息关键词
grep -r "出生\|身份证\|手机\|电话\|邮箱\|学历\|学位\|毕业" ~/文档/*.md 2>/dev/null

# 搜索用户全名上下文
grep -r "杨晓凯" ~/文档/*.md 2>/dev/null | head -20

# 搜索邮递/通讯地址
grep -r "yakeworld\|ghfdshgf" ~/ 2>/dev/null

# 搜索NSFC/基金申请书中的个人信息页
# （通常在文件开头或末尾的JSON/YAML段）
```

**常见信息来源优先级：**

| 信息 | 可能来源 |
|:-----|:---------|
| 姓名/单位/职称 | memory / user profile / 开源文章 |
| 政治面貌 | 提案文件、党派相关文档 |
| 学历/毕业学校 | 个人简历、发表文章（通讯作者单位）、基金申请书 |
| 出生年月/身份证/手机 | **通常不在本地文件**，需用户当面补充 |

## Step 6: 条件匹配与可行性判断

从附件1/通知中提取的关键条件，对照用户信息逐条判断：

```
选聘条件                    →  用户情况              →  结论
┌────────────────────────┐    ┌──────────────────┐    ┌─────────┐
│ 高级职称/硕士+5年经验   │    │ 主任医师/硕导     │    │ ✅ 符合 │
│ 医院/疾控等一线单位     │    │ INSTITUTION_NAME_PLACEHOLDER    │    │ ✅ 符合 │
│ 距退休≥3年             │    │                 │    │ ❓ 需确认│
│ 硕导可直接认定          │    │ 已认定硕导       │    │ ✅ 符合 │
└────────────────────────┘    └──────────────────┘    └─────────┘
```

## Step 6.5: 数据来源质量闸门 ⚠️ 强制步骤

**仅在涉及商业计划书、可行性报告、课题申请书等含具体数字/声明的文档时需要此步骤。** 纯表格填写（姓名/电话等）跳过。

**用户核心要求：「计划书一定要实事求是的。所有数据都要有来源。」**

对文档中每一项有具体数字或判断性声明的数据，做三级分类审计：

| 类别 | 判定标准 | 举例 | 处理方式 |
|:-----|:---------|:------|:---------|
| ✅ **有据可查** | 来自用户profile、本地文件、已知论文、官方年报 | 团队信息、学术成果 | 保留，可标注来源 |
| 🟡 **合理估算** | 基于已知事实的推算，有明确假设 | 门诊量、BOM成本、营收预测 | 保留但加注假设条件 |
| ❌ **需补充** | 无任何本地/公开依据，纯推测 | 市场规模、竞品价格、增长率 | 替换为定性表述或补充引用 |

### 审计操作

```python
# 对商业计划书中的每项数据，记录来源状态
audit = {
    "数据项": "...",
    "计划书中值": "...",
    "来源": "...",     # 本地文件/用户profile/公开报告/估算假设/无来源
    "置信度": "高/中/低",
    "建议操作": "保留/加注释/替换",
}
```

### 特别关注的数据类型

| 数据类型 | 常见陷阱 | 正确的做法 |
|:---------|:---------|:-----------|
| 市场规模 | "据XX报告"但报告不存在 | 改为定性表述（"市场空间广阔"），或查到具体报告编号 |
| 竞品价格 | 来自印象而非公开报价 | 改为"据行业公开招标信息"或列出范围 |
| 政策文件 | 文件名正确但具体条款存疑 | 核实具体文号和发布年份 |
| 学术成果 | 期刊名张冠李戴、论文数量虚报 | 从本地论文目录逐篇核对，确认投稿状态 |
| 财务预测 | 无假设的绝对数字 | 加注假设条件（BOM分解、销售渠道拆解） |
| 技术参数 | 尚未验证的规格写为事实 | 改为"目标指标"或"设计参数" |

### 网站/公开页面交叉验证

用户可能已有个人/团队网站（如WordPress搭建的实验室主页），往往包含最完整的信息：

| 信息类型 | 网站常见位置 | 提取方法 |
|:---------|:------------|:---------|
| 个人背景/职称/头衔 | 关于我们 / 团队介绍 | `curl → 去标签提取文本` |
| 论文清单（含DOI） | 期刊论文栏目 | `curl → grep DOI/pdf链接` |
| 专利清单（含授权号） | 成果转化 / 专利栏目 | `curl → grep ZL/CN/授权` |
| 科研项目列表 | 科研项目栏目 | `curl → grep 项目名称/基金号` |
| 产品/原型机状态 | 产品/成果栏目 | `curl → 提取产品名称和阶段` |

**典型命令链：**
```bash
# 1. WordPress REST API获取页面列表
curl -s "https://xxx.top/wp-json/wp/v2/pages?per_page=50"

# 2. 获取特定页面内容
curl -s "https://xxx.top/about-page/" | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub(r'<[^>]+>', '\n', html)
# 提取文本段落
"

# 3. 提取专利号、基金号等
curl -s "https://xxx.top/patents/" | grep -oP 'ZL\d+\.\d+|CN\d+\.\d|基金号'
```

> ⚠️ 网站数据可能与本地文件不一致——以网站为准（通常是更新后的公开版本）。

### 学术成果核实（特殊关注）

商业计划书中的论文声明必须可追溯。从以下位置交叉验证：

| 来源 | 查找方式 | 确认项 |
|:-----|:---------|:-------|
| `article_todo/` | `ls ~/桌面/article_todo/` | 人工撰写论文（有投稿状态） |
| `Synthos/outputs/papers/` | `ls /media/yakeworld/sda2/Synthos/outputs/papers/` | 质量门通过论文（有PDF+质量报告） |
| 用户profile/memory | `memory` / `fact_store probe` | 项目、课题、门诊量等背景信息 |

### 审计报告输出

审计完成后输出 `质量评估报告.md`，明确标注每项数据的来源和置信度，供用户逐项确认。

> 详见 `references/competition-data-source-audit-2026-05-30.md` — 实战案例（医学装备大赛商业计划书完整审计过程）。

## Step 7: 填写 docx

```python
from docx import Document

doc = Document('附件2_模板.docx')
table = doc.tables[0]

fill_map = {
    (0, 1): '杨晓凯',    # 姓名
    (0, 3): '男',        # 性别
    (0, 7): '民进会员',  # 政治面貌
    (3, 3): 'INSTITUTION_NAME_PLACEHOLDER',  # 工作单位
    ...
}

for (ri, ci), val in fill_map.items():
    write_cell(table, ri, ci, val)

doc.save('附件2_已填写.docx')
```

## Step 8: 填写 xlsx

```python
import openpyxl

wb = openpyxl.load_workbook('附件3_模板.xlsx')
ws = wb['汇总表']

# 找到数据起始行（表头之后的第一行）
data_row = 4  # 通常是第4行（空行1+表标题2+表头1=前3行）

for ci, val in enumerate([1, '杨晓凯', 'INSTITUTION_NAME_PLACEHOLDER', ...], 1):
    ws.cell(row=data_row, column=ci, value=val)

wb.save('附件3_已填写.xlsx')
```

## Step 9: 生成提交指引

整合通知中的关键信息，生成步骤清晰的提交清单：

```markdown
### 📋 提交材料清单
- ☐ 附件2申请表（纸质+PDF扫描版，单位盖章）
- ☐ 附件3汇总表（学院盖章）
- ☐ 学历学位证书复印件
- ☐ 职称证书复印件
- ☐ 主持/参与项目佐证材料

### 🗓 关键时间节点
| 节点 | 日期 |
|:----|:-----|
| 个人提交截止 | 6月1日 |
| 学院初审 | 6月4日 |

### 📞 联系人
- 学院/部门 | 联系人 | 电话 | 邮箱
```

## 已知陷阱

| 陷阱 | 表现 | 解决 |
|:-----|:-----|:-----|
| **docx merged cell 深层陷阱** | 写入值单元格后，标签单元格内容也被覆盖 | **不理解docx合并单元格共享XML元素**。`table.cell(ri,ci)`对合并范围内不同坐标返回同一个底层`<tc>`节点。写入一个即覆盖全部。**修复：不清除段落run，直接用 `cell.paragraphs[0].text = val` 增量写入** |
| **xlsx MergedCell 只读** | `cell.value = val` 抛 `AttributeError` | 用 `ws.cell(row, col)` 写非合并的单元格 |
| **扫描PDF OCR乱码** | 中文变乱码 | 确认 `-l chi_sim` 已安装；用 `pdftoppm -r 300` 提高分辨率 |
| **用户信息不在本地** | 搜索无结果 | 制作"待补充清单"向用户提问，不要无限搜索 |
| **docx 段落/表格混淆** | 关键字段在表格里不在段落中 | 先用 `doc.tables` 检查表格数量，大部分申请表数据在 table[0] |\n| **商业计划书数据无来源** ⚠️ | 市场数据、竞品价格、财务预测等凭印象填写 | **审计闸门**：对每个数字项执行三级分类（有据可查/合理估算/需补充），见 Step 6.5 |

## 实战参考

- `references/hangzhou-medical-college-industry-mentor-2026.md` — 杭州医学院行业导师申请表完整填写案例（docx+xlsx结构、个人信息来源、关键命令）
- `references/competition-application-workflow-2026-05-30.md` — 医学装备创新大赛参赛全流程（项目评审→资料收集→报名表→商业计划书→发件）
- `references/competition-data-source-audit-2026-05-30.md` — 商业计划书数据来源质量审计实战案例（逐项溯源方法论，含学术成果交叉验证）
- `references/researcher-profiling-via-notebooklm.md` — 基于NotebookLM的研究者面貌分析与补充工作流（数据提取→上传→逐问分析→修正补全）
- `templates/competition-business-plan.md` — 商业计划书通用模板（9章结构，含财务预测/风险控制/融资方案）
