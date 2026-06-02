# TODO 论文优化工作流（Existing Draft Optimization）

> 区别于 paper-pipeline 的"从零写起"流程，本工作流针对桌面上已有初稿的论文进行优化改进。
> 场景：用户说"第⑧篇，优化改进一下"，应对的是半成品/已有初稿。

## 三步法：评估 → 重构 → 编译

### Step 1: 评估现有状态

进入 `~/桌面/article_todo/{target_dir}/` 后，并行检查：

```bash
# 清单
ls *.md *.tex *.pdf
cat paper.md article.md    # 论文骨架和笔记
cat ref.bib | grep -c "@"   # 参考文献数
ls *.pdf 2>/dev/null | wc -l  # 参考PDF数
```

**评估维度**：
- 有完整LaTeX吗？→ 检查 `*v*.tex` 版本号
- 有编译好的PDF吗？→ 确认页数和报错
- 参考文献够吗？（D8标准≥30）
- Results有定量数据还是仅描述性文字？
- 有连接同组已有工作的引用吗？

### Step 2: 重构策略

按以下优先级优化，不做多余修改：

| 优先级 | 优化项 | 典型问题 | 做法 |
|:-------|:-------|:---------|:-----|
| P0 | Title + Abstract | 冗长/无量化结果 | 精简标题，摘要加入数值（均值±SD、p值）|
| P1 | **Results量化** | 仅文字描述，无统计表 | 加表（方向角/偏差/Inter-SCC）+ ANOVA/t-test |
| P2 | Discussion分层 | 单一平铺叙事 | 分解剖/建模/临床三层讨论 |
| P3 | 参考文献扩充 | <25篇 | 加关键文献（同组论文优先）|
| P4 | 跨论文引用 | 未引用同组相关工作 | Discussion中增加本节 |

**特殊：不同期刊模板的编译链**

| 模板 | 编译命令 |
|:-----|:---------|
| `elsarticle` (Elsevier) | `pdflatex → bibtex → pdflatex ×2` |
| `sagej` (Sage) | 同上（.bst文件名可能不同，如 SageV.bst）|
| `article` (普通) | `pdflatex ×2` |

### Step 3: 版本控制

**铁律：永远保留原始版本。** 创建 `articlev2.tex`（或 `{paper-name}-v2.tex`）而非直接覆盖原文件。

```bash
cp articlev1.tex articlev2.tex     # 备份
# 编辑 articlev2.tex ... 编译验证
```

### 实战笔记（2026-05-28 第⑧篇膜性SCC论文）

**原始状态**：
- Sage模板 `sagej.cls`，已编译 `articlev1.pdf`（16页，558KB）
- `paper.md`（261行，完整IMRaD）+ `ref.bib`（278行，19篇文献）
- 3张低清PNG图（586×299 ~ 652×400）
- Results仅描述性文字，无统计量化

**优化内容**：
1. 标题精简（"Enabled by micro-CT, ICT, and MRM" → "via Multi-modal High-Resolution Imaging"）
2. Abstract加入量化结果（mean 2.10°±0.67°, ANOVA p=0.23）
3. **新增3张数据表**：方向角表（Tab.1）、MEM-BONY偏差表（Tab.2）、Inter-SCC角表（Tab.3）
4. 讨论分层：①解剖意义 ②数学建模意义（引用同组SCC对数螺旋论文）③BPPV临床意义
5. 参考文献补齐至19篇（增加 Yang2026SCC 等跨组引用）

**编译结果**：`articlev2.pdf`（13页，820KB，零报错零警告）
