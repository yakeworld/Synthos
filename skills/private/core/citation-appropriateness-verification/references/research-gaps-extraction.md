# 论文参考文献重建方法论

## 触发条件
论文原始参考文献全部丢失（`.bib` + `references.bib` + `thebibliography` 均缺失），但有完整 `paper.tex`。

## 标准流程（6步）

### Step 1: 完整读取 paper.tex
- 提取标题、摘要、引言、方法、结果、讨论、结论
- 识别所有 `\cite{}` 键（即使 `.bib` 不存在，`paper.tex` 中仍保留引用键）
- 确认缺失状态：`thebibliography` 是否存在？`.bib` 文件是否存在？

### Step 2: 提取研究空白和科学假设
从以下段落提取：
- **引言（Introduction）**: 研究背景 → 研究空白 → 本文贡献
- **方法（Methods）**: 使用的技术框架（PINN/ODE/CNN等）
- **讨论（Discussion）**: 与现有工作的对比
- **结论（Conclusion）**: 未来工作方向

输出格式：
```markdown
## 研究空白
1. [空白描述]
2. [空白描述]

## 科学假设
1. [假设描述]
2. [假设描述]

## 核心技术
- [技术1]: [说明]
- [技术2]: [说明]
```

### Step 3: 按领域分类
将研究主题分为 6+ 个领域：
1. 基础理论（如：生物力学、流体力学）
2. 方法技术（如：PINN、ODE、CNN）
3. 临床应用（如：白内障、青光眼诊断）
4. 硬件/设备（如：眼球追踪设备、成像系统）
5. 数据分析（如：ML分类、统计分析）
6. 相关疾病/症状（如：前庭疾病、神经退行性疾病）

### Step 4: 批量检索
对每个领域：
- **PubMed/NCBI**: 搜索医学/生物医学相关论文
- **Crossref**: 搜索DOI和元数据（通过Tor SOCKS5代理）
- **PubScholar** (`pubscholar.cn`): 补充中英文论文
- **注意**: SS API Key `iYTNXXDH278...` 在 `~/.secrets`，子shell不自动source

### Step 5: 生成 DOI 映射
- 将检索结果与原始 `\cite{键名}` 匹配
- BibTeX 条目使用**原始引用键名**（如 `\cite{Raissi2019}` → `@article{Raissi2019}`）
- 确保引用键无特殊字符、无 `{` 符号
- 年份从 API 返回的 `published-print.date-parts` 提取（数组格式 `[2019]` → `2019`）

### Step 6: 处理失败
- **Issue-level DOI**（期刊整期DOI，如 `10.1111/ceo.2008.36.issue-5`）：手动搜索作者+标题
- **Crossref 500错误**：重试或改用 PubMed
- **无法匹配**：保留原始键，标注 `MISSING`，建议人工补充
- **标题截断 < 20字符**：跳过（可能是 Editorial/Masthead/Erratum 等非论文条目）

## 验证标准
- 原始引用键覆盖率 ≥ 85%
- 每条引用有 DOI
- 引用键与 `\cite{}` 完全匹配
- 无特殊字符、无重复键

## 示例
输入：`paper.tex` 中有 20 个 `\cite{键名}`，但 `.bib` 完全缺失
输出：`references.bib` 包含 18-20 条 BibTeX 条目，键名完全匹配原始 `\cite{}`
