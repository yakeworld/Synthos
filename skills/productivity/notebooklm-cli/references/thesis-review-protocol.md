# Thesis Review Protocol — NotebookLM 毕业论文学术审查

> 通过 NotebookLM Gemini 对中文硕/博士学位论文进行三维审查（质量评审 + 引用审计 + 格式术语检查），输出完整审查报告。
>
> 实战验证（2026-06-02）：用户确认"可以直接利用notebook LM进行论文审查"——这是首选的论文全文审查方式，无需人工通读。

## 适用场景

- 用户要求审查某篇毕业论文、学位论文
- 论文已上传到 NotebookLM（PDF 或 DOCX 格式）
- 需要结构化评审而非简单通读

## DOCX 格式处理（非PDF/MD）

毕业论文常以 `.docx` 格式发送。docx 不能直接上传 NotebookLM（CLI不支持）：

```bash
# 用 python-docx 提取纯文本
python3 -c "
from docx import Document
doc = Document('thesis.docx')
full = '\n'.join([p.text for p in doc.paragraphs])
with open('/tmp/thesis.txt','w') as f: f.write(full)
print(f'Total chars: {len(full)}')
"

# 检查基本信息
grep -n "参考文献\|摘要\|引言\|封面" /tmp/thesis.txt | head -10

# 分块上传到 NotebookLM（72K chars 分2块，每块60K）
python3 -c "
import subprocess
content = open('/tmp/thesis.txt').read()
for i in range(0, len(content), 60000):
    chunk = content[i:i+60000]
    pi = i//60000 + 1
    total = len(content)//60000 + 1
    subprocess.run(['notebooklm','source','add','--type','text',
        '--title',f'毕业论文 (part {pi}/{total})',
        '--timeout','120','-n','nb_id', chunk])
"
```

**陷阱**：python-docx 提取会丢失公式、表格、图片——纯文本文档。但 Gemini 仍能理解内容并发现公式乱码等问题。

```
论文已在NotebookLM中
  ↓
Step 1: 提取全文
  notebooklm source fulltext <source_id> -o /tmp/thesis.txt
  查看基本信息（标题/学校/专业/页数/引用数）
  ↓
Step 2: 七维评审（一次性提问，不分步）
  notebooklm use <nb_id> && notebooklm clear
  notebooklm ask "请对[论文标题]进行全面7维SCI质量评审，每维评分0-1..."

  七维:
  D1 创新性 — 新概念/新方法？
  D2 方法学严谨性 — 建模/实验设计/数学推导
  D3 结果可信度 — 数据支持结论？统计方法？
  D4 完整性 — IMRaD结构？缺什么？
  D5 清晰性 — 写作质量/图表/逻辑
  D6 新颖性 — vs现有文献的新贡献
  D7 引用质量 — 充分性/相关性/规范

  每维要求: 评分 + 硬伤列表 + 优化建议
  最后: 综合评价 + 是否达到学位论文水平判定
  ↓
Step 3: 参考文献审计
  notebooklm ask "请对毕业论文的参考文献进行完整的引用审计..."

  审计项:
  - 正文引用 vs 参考文献列表一致性（孤儿引用/僵尸引用）
  - 引用频率分析（各节引用分布）
  - 引用类型分布（期刊/专著/网络）
  - 时效性（近5年/近10年占比）
  - 自引分析
  - 格式规范（作者/标题/期刊/年份/卷期页码逐条检查）
  ↓
Step 4: 格式/文字/术语审查
  notebooklm ask "请对毕业论文进行格式/文字/术语方面的逐项审查..."

  审查项:
  - 格式硬伤：标点混用、空格错误、图表编号连续性、字体字号
  - 文字硬伤：错别字、病句、中英文混排
  - 术语硬伤：拼写错误、缩略语未定义、前后不统一、公式排版
  - 排版规范：段首缩进、行距、页眉页脚、页码
  ↓
Step 5: 参考文献排版检查（可选）
  notebooklm ask "请严格检查参考文献列表的排版格式，逐条检查..."

  检查项:
  - 作者格式（姓前名后？缩写空格？）
  - 标题格式（大小写统一？）
  - 期刊名（全称vs缩写？）
  - 年份/卷期/页码（格式统一？）
  - 标点符号（中英文混用？）
  - 整体排版（缩进行距）
  ↓
Step 6: 保存报告
  方式A: 本地文件
    write_file → ~/桌面/毕业论文审查报告_<主题>.md
  方式B: NotebookLM笔记
    notebooklm note create "..."
  方式C: NotebookLM源文件（大文件用Python subprocess）
    python3 -c "import subprocess; ..."
  ↓
报告发送给用户
```

## 关键提问模板

### 七维评审（中文硕/博论文版）

```bash
notebooklm ask "请对毕业论文《标题》进行全面评审。按以下7个维度评分(0-1)并给出具体改进建议：

1. **创新性** — [论文核心创新点]的独创性如何？
2. **方法学严谨性** — [方法描述，如实验设计/仿真建模/临床研究]是否严谨？
3. **结果可信度** — 数据是否支持结论？
4. **完整性** — IMRaD结构？缺什么？签名和日期缺了什么？
5. **清晰性** — 写作质量、逻辑性、图表
6. **新颖性** — 与现有文献相比，实质性新贡献？
7. **引用质量** — 参考文献是否充分且相关

每维给0-1分，逐项列出必须修正的硬伤和可优化的建议。最后给综合评价和是否达到学位论文水平的判定。"
```

### 参考文献审计

```bash
notebooklm ask "请对毕业论文的参考文献进行完整的引用审计。逐一检查：

1. **正文引用 vs 参考文献列表一致性** — 列出所有孤儿引用(正文有但列表无)和僵尸引用(列表有但正文无)
2. **引用频率分析** — 哪些只在引言出现一次？核心方法/结果部分引用了哪些？
3. **引用类型分布** — 期刊/专著/网络资源分别多少？
4. **时效性** — 近5年占比？近10年占比？
5. **自引分析** — 作者团队自己的工作有多少条被引用？
6. **格式规范** — 参考文献条目是否格式一致（作者、标题、期刊、年份、卷期页码是否完整）？"
```

### 格式/文字/术语审查

```bash
notebooklm ask "请对毕业论文进行格式、文字、术语方面的逐项审查。重点检查：

1. **格式硬伤** — 中英文标点混用、空格错误、图表编号连续性、图表标题格式统一
2. **文字硬伤** — 错别字、病句、中英文混排、逻辑连接词误用
3. **术语硬伤** — 医学术语拼写错误、缩略语首次出现是否标注全称、同一概念前后术语不一致、数学符号/公式排版
4. **排版规范** — 段首缩进、行距、页眉页脚、页码

逐条列出每个硬伤的具体位置(章节+行号或位置描述)和修正建议。"
```

## 陷阱：clear 清空 notebook 上下文

`notebooklm clear` 会清除当前 notebook ID，之后需重新 `notebooklm use <nb_id>` 再 `ask`。正确顺序：

```bash
# ❌ 会失败
notebooklm clear && notebooklm ask "..."          # use 上下文丢失

# ✅ 正确
notebooklm clear && notebooklm use <nb_id> && notebooklm ask "..."
# 或省略 clear（自动开启新线程）
notebooklm use <nb_id> && notebooklm ask "..."
```

## 报告交付

审查完成后将报告发送给用户：

```bash
# 方式A：飞书附件（推荐）
write_file → ~/桌面/毕业论文审查报告_<主题>.md
send_message target=feishu:oc_xxx message="MEDIA:~/桌面/...md"

# 方式B：NotebookLM 笔记 + 源文件
notebooklm note create "..." --title "毕业论文审查报告"
# 大文件（>60KB）用 Python subprocess 上传为 source
python3 -c "import subprocess; ..."

# 方式C：本地文件 + NotebookLM 双保险
# 本地存 ~/桌面/，NotebookLM 存 source + note
```

1. **Shared笔记本的source fulltext** — Owner可用，Shared可用；但Shared不能`source delete`
2. **公式乱码** — PDF转文本时公式会变成乱码（`6ππaaρ(xρ-uρ)`），Gemini能识别并建议修正
3. **参考文献名颠倒** — Gemini能发现 `Jm E.` 应为 `Epley JM.` 等作者名错误
4. **术语不统一** — 正文用"上半规管"而综述用"前半规管"，Gemini能交叉检测
5. **图表编号跳跃** — 二进制PDF转文本后表格编号仍可被Gemini检测（如表8→表9→表11→表13 缺表10、表12）
6. **大文件分块上传** — 完整审查报告>60KB时用Python subprocess分块上传到NotebookLM

## 验证清单

- [ ] Step 1: 全文提取成功（确认≥50000 chars）
- [ ] Step 2: 七维评审完成，每维有评分+具体硬伤
- [ ] Step 3: 引用审计覆盖一致性/频率/类型/时效/自引/格式
- [ ] Step 4: 格式/文字/术语审查覆盖所有子项
- [ ] Step 5: 参考文献排版逐条检查（可选）
- [ ] Step 6: 报告已保存（本地和/或NotebookLM笔记）
- [ ] 报告已发送给用户
