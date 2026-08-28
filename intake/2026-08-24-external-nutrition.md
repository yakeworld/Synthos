# 外部营养采集 · 内化存档

> 每日采集 3 维度外部信息（AI前沿 / 工具发现 / 学术动态），提炼可内化知识。
> 评分 ≥8/10 的资源在此落盘为**内化建议**，供进化引擎与后续会话消费。
> 格式：每日一个文件 `YYYY-MM-DD-external-nutrition.md`。低分资源仅记录名称，不落建议。

---

## 2026-08-24

### 采集概况
- AI前沿: 20条 arXiv（cs.CL/AI/CV + eess.SP/q-bio.BM，近7天）— 高价值 2条（1条已内化、1条08-20已内化确认重复）
- 工具发现: 20条 GitHub 新仓（近7天创建, ≥30★）— 高价值 2条（📌观察）
- 学术动态: 8条前庭目标域 PubMed（BPPV/vestibular/nystagmus，最新 PMID）— 高价值 2条（📌观察）
- 内化方式: **cron 下不派 delegate**（2026-08-10 实测子代理 90min+ 无写入）→ 主任务直接 skill_manage/patch 内化。本轮直接 patch skill-authoring，已 stat 验证落盘。
- 数据源: web_search/web_extract 全挂（DaemonThreadPoolExecutor._initializer 基建错）→ 改走 GitHub API + arXiv API + PubMed E-utilities + arXiv abs 页（curl -o 落盘后 python3 解析）。

### ✅ 高价值资源（≥8/10）

#### 1. arXiv:2608.20274 "Break It Down, Pass It On: Cross-Task Skill Transfer in LLM Agents" — 8.5/10 → ✅已内化
- **地址**: https://arxiv.org/abs/2608.20274
- **要点**: 控制实验比较技能归纳方式如何影响跨任务迁移。三轴：task-level vs subtask-level、text vs code 格式。
- **三条实证结论**:
  1. **subtask-level 技能 > task-level**（task-level 大多把 agent 拉到无记忆基线以下；subtask-level 高于基线）→ 印证 Synthos 原子技能架构
  2. **text 技能迁移 > code 技能**
  3. **skill utility score = specificity × abstractness**，且**只需技能+任务描述、无需跑任务**即可算 → 预运行诊断
- **内化理由**: 与 Synthos skill-first 架构同题，给出可直接执行的技能设计判据 + 新技能入库预检指标
- **已执行**: `patch skill-authoring/SKILL.md` 追加「2026-08-24 采集：跨任务技能迁移」节（含3条设计判据 + 效用分入库预检 + 粒度自检）
- **验证**: grep "2608.20274"=1、"skill utility"=1；stat mtime 2026-08-24 07:06 确认落盘
- **状态**: ✅已内化

#### 2. arXiv:2608.20290 "Phantom Gains: Auditing Self-Improvement Against a Measured Null" — 8/10 → 08-20已内化（重复，跳过）
- **地址**: https://arxiv.org/abs/2608.20290
- **要点**: 逐题 gain/loss 转移审计 + 测量零假设（对同一测量对象重复跑的噪声带）判断自改进真伪；单题精确检验 + FDR 控制；自训练 vs 外部蒸馏的逐题不对称（p<1e-8）
- **状态**: 已于 2026-08-20 内化进 `self-deception-risk`（"测量零假设审计"节，lines 64-81）。本轮为 arXiv 近期命中再次出现，**确认为重复，不重复 patch**，仅登记 watchlist 供追溯。

### 📌 观察列表（6-7分，下轮复查）
- **arXiv:2608.20319** "Inducing Task Models from Computer-Use Traces" (TMI) — 7分。从计算机使用痕迹归纳层级任务模型（目标分解 + 控制流），派生技能 held-out +30%。→ automated-research-pipeline / 技能自动生成可借鉴。
- **GitHub: browser-use/macos-harness** (728★) — 7分。最薄 harness 让 LLM 全权控制 Mac。→ computer-use / codex-tmux-control 的 Mac 端参考实现。
- **GitHub: Spielewoy/autoprompt-skill** (767★) — 7分。编码 Agent 提示优化 skill，声称 agentic coding 失败率 -45%。→ 对照 dsh/codex 技能链可评估。
- **PMID 42633580** "Ocular VEMP: 500Hz toneburst vs narrowband CE-Chirp in older adults" (Int J Audiol 08-02) — 6分。前庭目标域。
- **PMID 42630146** "Persistent apogeotropic positional nystagmus of the lateral SCC" (Front Neurol 08-07) — 6分。前庭目标域。

### 本轮采集的其余候选（≤5分，仅记录）
- GitHub: s1dashu/ip-as-logo-skill(3891★, 设计向)、yetone/cumora(2945★, agent群聊)、MengTo/threeui(2840★, 前端)、CopilotKit/OpenBot(2488★, AI coworker)、wang2122/sprix-sage-router(1412★, A2A路由)、duty1g/x64dbg-mcp-server(823★, 调试MCP)、iAmCorey/Wake(537★, Rust agent会话管理)
- arXiv: 2608.20335 4DAnyone(4D人体重建)、2608.20318 AI4AI-Bench(RSI基准)、2608.20314 MidTool(agentic工具中训)、2608.20331 G-CARL(医学报告) — 与Synthos主线相关性弱

### 数据源可用性记录
- web_search / web_extract: ❌ 全挂 `DaemonThreadPoolExecutor._initializer`（cron 基建错，连 2 并行 read_file 也触发 → 本轮全部改串行/terminal）
- api.github.com: ✅ (search/repositories 近7天新仓正常)
- export.arxiv.org (API + abs 页): ✅（abs 页不受 API 限流影响）
- eutils.ncbi.nlm.nih.gov (esearch + esummary): ✅
- 安全拦截: `curl | python3` 被 tirith:curl_pipe_shell 拦 → 一律 curl -o 落盘 + 另起 python3 解析；plain-http arXiv 被拦 → 改 https。
