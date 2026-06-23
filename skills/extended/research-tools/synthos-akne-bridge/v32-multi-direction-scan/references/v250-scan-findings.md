# v250 Rotation Scan — 关键发现（2026-06-22）

## 精确查询漏检竞争者（⚠️ 方法论陷阱）

**观察:** 在 v250 扫描中，BPPV Virtual Simulation 方向使用精确查询
`"BPPV+virtual+simulation+repositioning+otolith+trajectory"` 返回 PubMed=0（ABSOLUTE_WHITE），
但放宽条件后（去除特定术语限制）发现 2 篇 2025 年直接竞争者：
- PMID 40492172 — *Enhancing the security of horizontal canal BPPV repositioning maneuvers: insights from virtual simulation*
- PMID 40035862 — *Minimal stimulus strategy for diagnosis and treatment of BPPV: a virtual simulation study*

**根因:** 精确定义的查询词可能过滤掉实际相关但措辞不同的文献。PubMed 索引不总是使用你最精确的术语。

**修复规则：**
1. 对每个返回 ABSOLUTE_WHITE 的方向，立即执行一个二级宽查询（移除最严格的条件词、使用更广的同义词、添加年代范围作为唯一约束）
2. 对得分 ≥15 的方向（新候选管线），宽查询必须执行
3. OpenAlex 的全文搜索通常比 PubMed 标题/摘要搜索更宽泛——优先使用 OpenAlex 作为二级确认

## WHITE→OBSERVED 方向变化（壶腹嵴偏移）

**观察:** 壶腹嵴偏移（Cupula Deflection）在 v247（2026-06-13）为 ABSOLUTE_WHITE（PubMed=0），
在 v250（2026-06-22）变为 WHITE_OBSERVED（PubMed=4）。9天内出现4篇论文。

**应对方案：**
1. 记录新论文的 PMID 和标题
2. 评估每篇论文的相关性和威胁等级
3. 如为核心方向 → 更新竞争态势评估
4. 如为直接竞争者 → 检查是否有同团队未发布的预防稿

**发现的论文：**
- PMID 42268297 (2026) — *Should perilymph be considered when modeling the lateral semicircular canal?* — 新发表，直接影响 SCC 建模假设
- PMID 31069593 (2019) — *Asymmetric cupula displacement due to endolymph vortex in the human semicircular canal* — 数值模型，非全新
- PMID 27059257 (2016) — *Numerical simulation of the role of the utriculo-endolymphatic valve* — 较老
- PMID 20448336 (2009) — *Mechanical properties and motion of the cupula of the human semicircular canal* — 基础文献

**结论:** 仅有1篇真正的新竞争者（2026年篇），其余为旧文献重新被索引。非紧急，但需监控。

## 未完成 stub 论文检查

旋转扫描后，应检查 agent-tracker.json 中的 `remaining_stubs` 或 `notes` 字段。
v250 时发现 2 个核心方向 stub 仍为「待启动」：
1. **individualized-bppv** — BPPV 个体化复位仿真（面临竞争压力，白色空间在关闭）
2. **scc-pd-biomarker** — SCC 螺旋参数作为 PD 生物标志物（仍为开阔白色空间）

**检查流程：**
1. 读取 `agent-tracker.json`
2. 查找 `remaining_stubs`（如果有）或 `notes` 中提及的待启动论文
3. 评估每篇的竞争压力（v250：BPPV 仿真有 2 篇 2025 竞争者 → P0；SCC-PD 无竞争者 → P2）

## 核心方向文献动态（2025-2026）

- **瞳孔椭圆拟合 / 3D 虹膜分割**: PubMed 0 篇（2025-2026）— 仍为 ABSOLUTE_WHITE
- **3DeepVOG** 框架论文仍活跃（2025-2026），但非椭圆拟合方法竞争者
- **Synchrotron 内淋巴管研究**（PMID 2026）— Meniere 病方向，非 BPPV
