# 参考文献全文级引用恰当性审查方法

## 背景

形式检查（D10a、孤儿、僵尸、DOI）通过后，用户要求逐篇阅读文献全文检查"引用是否得当"——即文献是否真的支持论文中的论断。这是质的要求，不是量的要求。

## 完整工作流程（2026-06-18 3D Eyeball Iris Segmentation案例）

### 第一步：PDF准备与验证

```bash
# 1. 从bib提取所有条目信息
grep -B1 -A15 '@InProceeding\|@Article\|@inproceedings\|@article' references.bib | grep -E 'title|doi|file'

# 2. 用Semantic Scholar查询openAccessPdf
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:<DOI>?fields=title,authors,year,openAccessPdf,externalIds"

# 3. 下载正确PDF
curl -L -o <key>.pdf "https://arxiv.org/pdf/<arxiv-id>.pdf"

# 4. 验证PDF内容是否匹配主题
strings <pdf> | grep -i "<主题关键词>" | head -5
```

**PDF corruption detection**: 下载后用`strings`搜索论文主题关键词。如果找到完全不相关领域的内容（如OLED显示器、光纤传感器），说明PDF错误。

### 第二步：逐篇审查

对49篇参考文献，逐篇执行：

1. **提取引用语境** — 论文中在哪里引用了这篇文献？上下文是什么？
2. **阅读PDF全文** — 文献实际内容是什么？核心结论是什么？
3. **比对** — 文献是否真的支持论文中的论断？有无张冠李戴/断章取义/夸大？
4. **记录** — 每篇记录：引用语境、PDF内容验证、结论

### 第三步：报告生成

报告结构：
- 审查结论总览（表格：恰当数量、修复数量、可验证数量）
- 逐篇审查详表（按主题分组）
  - 引用语境描述
  - PDF内容验证（文献标题、作者、核心内容）
  - 引用恰当性判断（✅/⚠️/❌）
- 修复报告（PDF错误的发现、修复过程、验证结果）
- 总体质量评估（恰当性百分比、准确性、必要性、完整性、格式）
- 伦理声明（逐篇验证声明、无学术不端结论）

### 关键技术点

1. **Semantic Scholar API** 是查找开放获取PDF的最佳工具，返回openAccessPdf字段（含arXiv链接）
2. **strings命令** 快速验证PDF内容匹配度，不需要完整文本提取
3. **按主题分组** 审查（核心方法→数据集→深度学习→3D眼模型→当前趋势），逻辑更清晰
4. **修复报告要详细** — 记录错误内容、正确内容、原因、修复方法、验证结果

## 输出文件

- 逐篇报告: `citation_verification_report.md`
- 修复报告: 包含在报告中
- 每篇PDF验证结论: 记录在报告中

## 注意事项

- 全文级审查无法完全自动化，需要逐篇人工判断
- AI可以辅助（提取语境、生成报告模板），但"引用是否得当"的判断需要人类专家或大模型全文分析
- PDF文件错误是常见陷阱，必须在审查前验证PDF内容正确性
- 49篇文献的全套审查大约需要30-60分钟（人工）或15-30分钟（大模型辅助）
