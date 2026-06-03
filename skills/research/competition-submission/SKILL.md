---
name: competition-submission
description: "End-to-end preparation of submission materials for AI, tech, and innovation competitions. Extract requirements from PDFs or websites, map project capabilities to scoring criteria, generate all required documents including technical specifications and roadmaps and demo video scripts and form-filling guides, and produce a submission checklist with deadlines. Covers medical education AI contests, general tech innovation competitions, academic conferences, and Chinese government grant competitions. Supports Chinese and English competition formats."
signature: "competition_metadata: dict -> submission_package: dict"
related_skills: [academic-paper-completion, adhd-eye-tracking-review, arxiv, biorxiv, blogwatcher]
allowed-tools: [terminal, file, web, search]
version: 2.2.0
license: MIT
metadata:
  hermes:
    tags: [competition, submission, pdf-extraction, scoring-criteria, video-script, form-filling, chinese-competitions, medical-education, tech-innovation]
    related_skills: [nsfc-grant-audit, notebooklm-cli, ocr-and-documents, research-paper-writing, powerpoint, obsidian]
---

# Competition Submission — End-to-End Preparation

End-to-end preparation of submission materials for AI, tech, and innovation competitions. Extract requirements from PDFs or websites, map project capabilities to scoring criteria, generate all required documents including technical specifications and roadmaps and demo video scripts and form-filling guides, and produce a submission checklist with deadlines. Covers medical education AI contests, general tech innovation competitions, academic conferences, and Chinese government grant competitions. Supports Chinese and English competition formats.

## Trigger

Load this skill whenever the user:
- Provides a competition PDF or URL and asks to participate
- Needs to prepare submission materials for any academic, tech, or innovation competition
- Has a project and wants to enter it into a contest
- Asks about competition scoring criteria and how to match their project

## ⚡ 先决判断 — Audit Mode vs Generate Mode

在进入任何 Phase 之前，**必须先判断用户已有多少材料**。不要默认从零生成。

### Entry Gate: Inventory Check

当用户说"检查已有报名材料"或"看看我们有什么"时，进入 **Audit Mode**：

1. **搜索已有材料清单**：
   ```bash
   # 检查 submission-summary.json (manifest)
   find PROJECT_ROOT -name "submission-summary.json" 2>/dev/null
   # 检查 docs/ 目录下的竞争材料
   find PROJECT_ROOT/docs -name "*参赛*" -o -name "*competition*" -o -name "*submission*" 2>/dev/null
   # 检查视频文件
   find PROJECT_ROOT/docs -name "*.mp4" -type f 2>/dev/null
   # 检查常见下载目录（用户可能前期准备了但未移入项目）
   find ~/下载 ~/Downloads -name "*参赛*" -o -name "*competition*" -o -name "*submission*" -o -name "*申报*" 2>/dev/null
   ```

2. **如果找到 `submission-summary.json`**：
   - 直接读取作为材料清单
   - 对比 checklist 检查"已完成"和"待完成"项
   - 不要重新生成已有的材料

3. **如果找到 `docs/*参赛材料总索引*` 或 `docs/*配套材料清单*`**：
   - 读取作为完整索引
   - 对每个文件：检查文件是否存在、读取关键内容验证完整性
   - 输出状态表（✅ 已完成 / ⏳ 待完成）

4. **如果找到已有的视频文件**：
   - 用 `ffprobe` 检查时长、码率、分辨率
   - 确认是否符合竞赛要求
   - 不要建议重新录制 — 只需确认是否可用

5. **只有确认没有已有材料时，才进入 Generate Mode (Phase 1)**

### 常见已有材料模式

| 模式 | 特征 | 行动 |
|------|------|------|
| 空白项目 | 无 docs/ 或无竞赛相关文件 | 全程生成 |
| 部分准备 | 有部分文档、缺视频或申报书 | 仅补齐缺项 |
| 已完整准备 | 有 `submission-summary.json` + 9份文档 + 视频 | 审计+检查一致性 |
| 视频已制作 | 多个版本（_最终版, _专业版, _高码率） | 确认哪个是最终版，检查时长/分辨率 |

## Workflow

### Phase 0: Competition Discovery (when user doesn't have a URL)

当用户说"互联网上有没有竞赛"或"帮我找找相关竞赛"时，先进行搜索，不要默认用户已有URL。

1. **首选搜索方式 — DuckDuckGo Lite + curl**：
   ```bash
   curl -sL "https://lite.duckduckgo.com/lite/" \
     -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64)" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "q=搜索关键词&kl=cn-zh"
   ```
   - 提取结果链接：`grep -oP 'class="result-link"[^>]*href="([^"]*)"'`
   - 提取结果摘要：`grep -oP 'class="result-snippet">.*?</td>'`
   - ✅ 比 `browser_navigate` 更可靠（Google屏蔽curl，DDG Lite不过度依赖JS）

2. **搜索关键词策略**：
   - 竞赛全称 + 赛道名（如 `全球数智教育创新大赛 AI for Medicine 赛道`）
   - 加上 `+ 提交材料 + 评审标准 + 截稿` 定位要求页
   - 年份后缀：`+ 2026`
   - 中文竞赛加入主办高校名增加精度（如 `+ 北大医学`）
   - 若搜索结果有限，切换简称/全称交替搜，或搜高校教务处通知

3. **从搜索结果提取关键信息**：
   - 逐一curl结果页，提取：截止日期、提交材料清单、赛组分类、评审标准、联系方式
   - 优先找高校官方通知（.edu.cn），通常附完整的参赛通知和申报书附件
   - 新闻稿（搜狐/光明网/MSN）含概述，但缺少评分细则和附件

4. **竞赛官网不可访问时**：
   - 官网（如 `http://MeedTAC.mh.chaoxing.com`）可能依赖JS渲染或登录，curl直接访问会超时
   - 对策：搜索 `site:edu.cn 竞赛名` 找高校转载版；或搜申报书附件下载链接

### Phase 1: Requirement Extraction

1. **Extract competition requirements from PDF**:
   - Use `pdftotext` from poppler-utils (preferred over `pdfminer.six` for Chinese PDFs): `pdftotext "/path/to/file.pdf" -`
   - Handle Chinese characters, tables, multi-column layouts
   - If PDF is scanned/image-based, use `ocrmypdf` or `pdf2image` + OCR first
   - Key fields to extract: deadline, required materials, scoring criteria, team size, submission format, identity anonymization rules

2. **Extract competition requirements from website**:
   - Use `curl` with proper User-Agent — avoid `browser_navigate` (heavy JS rendering causes timeouts)
   - Parse HTML for scoring tables, material requirements, deadlines
   - If the page requires login or heavy JS, try to find the PDF version or API endpoint

3. **Parse the scoring matrix**:
   - Extract each scoring dimension and sub-dimension
   - Create a mapping table: Project Capability → Scoring Criterion → Score Estimate
   - Identify gaps where the project needs enhancement before submission

### Phase 2: Project Analysis & Scoring Mapping

1. **Analyze the project**:
   - Read project documentation, SKILL.md files, architecture docs
   - If the project uses NotebookLM for sources: use `notebooklm source list` for metadata classification and `notebooklm summary` for overview. Do NOT read individual sources (times out on large notebooks).
   - Identify: core features, technical stack, unique innovations, application scenarios, validation data, user base, scalability

2. **Map to scoring criteria**:
   - Create a detailed scoring matrix (see `references/scoring-matrix-template.md`)
   - Score each dimension (e.g., 医学专业性 30/30, 智能与创新 28/30)
   - Identify strengths (to emphasize) and weaknesses (to address in materials)
   - Calculate estimated total score and target level (gold/silver/bronze)

3. **Enhance weak dimensions**:
   - If "实施与效果" is weak: add real-world usage data, user testimonials, before/after metrics
   - If "可推广性与生态价值" is weak: emphasize open-source, curriculum reusability, multi-institution deployment
   - If "技术先进性与创新性" is weak: highlight novel architecture, unique methodology, first-of-its-kind features
   - If "系统智能化程度" is weak: emphasize perception, decision-making, interaction, adaptation capabilities

### Phase 3: Material Generation

#### 🔍 首要原则：实事求是（Fact-Based Writing）

**所有竞争材料中的声称必须以项目实际产出为依据，不得使用未经验证的效率百分比或模糊的量化数据。** 审稿人和评委可以从论文、代码库和公开记录中验证你的声称。每一条数据声明必须能追溯到以下之一：

| 可接受的数据来源 | 示例 | 不可接受的声称 |
|:-----------------|:-----|:---------------|
| 已发表论文的摘要/正文中的明确陈述 | "53轮进化, 0.98质量分" (论文Abstract) | "效率提升4-6倍" (论文未提及) |
| 代码仓库的README/指标徽章 | "18次外部吸收" (README表格) | "覆盖率95%+" (无来源) |
| 基准测试的明确输出 | "Citation F1 78.3%" (论文Table结果) | "假设生成效率提升5-10倍" (无实验证据) |
| 平台记录（Kaggle排名、GitHub Star数） | "Kaggle首页推荐" | "学生掌握率从30%提升至75%" (不属于系统指标) |

**编写材料时的检查流程**：
1. 对每个效率/效果/量化数字，问：**"论文或项目文档中是否有对应的明确声明？"**
2. 如果没有，**删除该数字**，改用论文中已有的实际数据替代
3. 不要用"我们相信..."或"预期可达到..."等模糊措辞 — 评委看的是现有证据
4. 如果项目有真实用户数据（如教学项目的学生反馈），应单独归类为"应用案例"而非系统本身的能力声称
5. 最后一条防线：整个材料写完后，逐句对照项目论文/README，确保每个声称都有据可查

> **2026-05-25 实战教训**：Synthos 竞赛材料初版包含"文献综述效率提升4-6倍""假设生成效率提升5-10倍""学生方法论掌握率从30%提升至75%+"等数据，但这些数字在 Synthos 论文中从未出现。论文实际提供的可验证数据是：53轮进化、0.98质量分、18次吸收、Citation F1 78.3%、6轴质量评分72/100、2-3次人在回路/篇。所有未经验证的数字已被删除，替换为论文实际的量化数据。

### Phase 3: Material Generation (continued)

Generate ALL required materials. For projects with an existing git repo, **first decide where materials live** — see the "Material Segregation" pattern below before generating anything.

#### Material Segregation: Project Repo vs Submission Package

**Problem**: Competition materials often contain info you don't want in a public GitHub repo (personal names in 申报书, preliminary drafts, large binary files). Yet the main project repo has the documentation needed to write them.

**Pattern — Two Directories**:
```
/media/sda2/ProjectName/              # Main project repo (git-tracked, GitHub public)
  ├── docs/                            # Public docs, architecture, README
  ├── skills/                          # Core skills, evolution engine
  ├── README.md
  └── .gitignore

/media/sda2/ProjectName-competition/   # Submission package (local-only, NO git)
  ├── 智能体建设说明书.md              # Written with char limits
  ├── 附件3-大赛申报书_已填写.docx     # Contains personal info
  ├── Synthos_封面_智能体.png          # Cover image
  └── 参赛材料总索引.md
```

**Workflow**:
1. Keep the main project as the authoritative source for technical content (read from there)
2. Create a separate `-competition` directory for submission materials
3. Write materials referencing project data, not by copying the entire project
4. **NO git init** in the competition dir (or if git exists, ensure it's in .gitignore)
5. If competition materials were previously inside `docs/` and need to move out:
   - `git add` the deletions of moved files from docs/
   - Update `.gitignore` to block the competition dir (e.g. `/竞赛材料/`)
   - Commit + push the cleanup
   - Verify with `git status` that no competition files leak
6. The `-competition` dir is a delivery package — its contents go to the competition website, not to GitHub

**智能体建设说明书 / Project Specification**:
   - Structure: 简介 (背景→拟解决问题→核心功能→技术路线→创新点→应用载体→智能体类型及权限→应用环节与成效) + 应用成效 (实践成果→量化成效→示范价值)
   - Strict word limits: typically 2000 for 简介, 1000 for 应用成效
   - **Character count management**:
     1. Draft the full content first (don't worry about limit)
     2. Count Chinese characters: `python3 -c "import re; s=open('file.md').read(); print(len(re.findall(r'[\u4e00-\u9fff]', s)))"`
     3. Condense strategically: keep quantitative data → merge similar points → remove redundant explanations → keep innovation points and application carrier
     4. Re-count after each condensing pass
     5. Verify all required elements survive (see checklist below)
   - **简介 must cover these specific elements**:
     - ✅ 开发背景 (policy context, current challenges)
     - ✅ 拟解决问题 (2-4 core problems)
     - ✅ 核心功能 (brief description of each module)
     - ✅ 技术路线 (architecture, platform, methodology)
     - ✅ 创新点 (3-6 unique innovations)
     - ✅ **应用载体** — explicit internet link or QR code for accessing the agent (GitHub repo URL, web interface URL, or API endpoint)
     - ✅ **智能体类型及权限属性** — agent classification (cognitive-assistant / data-analysis / teaching-assistant) + permission model (open-source MIT / role-based / login-required)
     - ✅ **具体应用环节与实施路径** — where it's deployed (NSFC grants, graduate teaching, clinical modeling) and how it's used in practice
     - ✅ **量化成效数据** — specific before/after metrics
   - Must be self-contained; reference other materials but not require them for understanding
   - Write in a single block (competition forms are plain text, not markdown-friendly)

**技术路线图 / Technical Roadmap**:
   - System architecture diagram (ASCII art or Mermaid)
   - Input-output data flow
   - Core workflow steps
   - Technology stack table
   - Methodology mapping (e.g., CRISP-DM stages → tool workflow stages)
   - Should visually demonstrate the project's sophistication

**演示视频脚本 / Demo Video Script**:
   - 6-10 minute MP4, 720p+
   - Timestamped sections with narration (旁白) and visual direction (画面)
   - Must include: intro, architecture, core demo, innovation points, applications, conclusion
   - No personal names, school names, or identifiable info in video
   - Naming convention: "{智能体名称}.mp4"
   - See `templates/video-script-6min.md` for template

**申报书填写指南 / Form-Filling Guide**:
   - All form fields with pre-filled content
   - Template recommendation opinions (教务部门意见, 思想政治审查, 学校意见)
   - Step-by-step guide for filling the official form
   - Team member info template

**配套材料清单 / Supporting Materials Checklist**:
   - All supporting documents needed
   - Status tracking (✅ ready / ⏳ pending)
   - Testing account requirements
   - IP documentation requirements

**参赛选手承诺书 / Commitment Letter**:
   - All commitment clauses mapped to project context
   - Signature lines for all team members
   - Must be printed and hand-signed (or electronic signature)

**参赛材料总索引 / Submission Index**:
   - All files organized with status tracking
   - Scoring criterion match summary
   - Action timeline with deadlines
   - Core competitive advantages summary

### Phase 4: Post-Evolution Material Refresh 🔄

当系统经历了**增量进化**（版本升级、指标提升、新增能力，但架构未重构）时，竞赛材料需要系统性**刷新**而非全面重写。区别于 Phase 5 的重构审计，这里专注于数字和描述的增量更新。

#### Trigger
- 系统版本号小/中版本更新（如 v4.0→v4.2，非 v3→v4 架构重构）
- 关键指标提升（质量分数、测试通过率、进化轮次、数据源数量等）
- 新增能力（新API集成、新数据源、新技能吸收）
- 用户说"全面更新"、"更新申请书和演示"

#### 刷新清单 — 逐材料检查点

| 材料类型 | 检查点 | 典型更新内容 |
|----------|--------|-------------|
| **智能体建设说明书** | 版本号、原子数、数据源列表、质量指标、创新点列表 | v3.0→v4.2, 6原子→7原子, 四大→六大数据库, 0.97→全1.0, 6项→7项创新 |
| **技术路线图** | 底部版本戳、技术栈表数据、I/O数据流 | v3.0→v4.2, 7/7→8/8通过, 新增数据源 |
| **演示PPTX** | 架构图文字标签（"六维"→"七维"）、质量仪表盘数值、进化轮次 | 0.97→1.0, 6轮→20轮 |
| **演示PDF** | 若由PPTX导出，PPTX更新后须重新导出 | `libreoffice --headless --convert-to pdf` |
| **申报书** | 版本号、项目简介中的技术描述 | v4.x 描述、新指标 |

#### Workflow（本会话验证流程）

1. **读权威源**：先读 `evolution-state.json` / `evolution-log.md` 获取系统最新版本号、质量指标、进化轮次 — 这些是权威数据源，所有材料中的硬编码数字均应以它们为准
2. **逐材料审计**：按上表检查每个材料（版本号、指标、数据源、架构描述、创新点、文件结构），用 `grep` / 全文搜索找出所有硬编码旧值
3. **按类型更新**：
   - **Markdown文档**：`patch` 替换硬编码版本/指标/描述，一次一个文件，验证 diff 正确
   - **PPTX**：用 `python-pptx` 遍历 slides 找特定文本（如 "0.97"、"六维"、"四大"）并替换 — 同时更新数值和文字标签
   - **申报书Docx**：如果已有已填模板（如 `docs/附件3-大赛申报书_已填写.docx`），更新其中的描述性文本
   - **PDF**：由 Docx/PPTX 重新导出 — `libreoffice --headless --convert-to pdf input.pptx --outdir output/`
4. **同步副本**：用户可能在 `~/下载/` 有独立副本，更新后 cp 覆盖保持一致
5. **更新 submission-summary.json 中的指标**：同步 `quality_metrics` 字段（evolution_count, overall_score, external_absorptions 等）为当前实际值。提交清单与实际指标不一致会引发审核问题。
6. **输出更新总索引**（可选）：创建 `参赛材料总索引.md` 含评分对标分析

#### Pitfalls

- **不要全量重写**：进化更新只需要替换硬编码数字和描述文本。核心内容（背景、解决的问题、技术优势描述）通常仍然准确 — 检查一下就好，不要重写
- **版本号埋藏在多处**：建设说明书正文段落、技术路线图底部、技术栈表、创新点描述、质量指标段 — 每个都需要单独 patch，遗漏任何一个都会造成版本不一致
- **PPTX 文本更新技巧**：`para.clear()` + `para.add_run().text = new_text` 可保留原有样式框架。更新数值的同时一定要更新对应的文字标签（如"六维"→"七维"、"四大"→"六大"、"六原子"→"七技能"），否则页面会自相矛盾
- **LibreOffice 导出PDF**：`libreoffice --headless --convert-to pdf input.pptx --outdir output/` — 注意路径中有空格时要正确引用。耗时约10-30秒，耐心等待
- **用户可能有独立副本**：`~/下载/` 下的 PDF 是用户日常使用的版本，更新项目文档后需手动 cp 覆盖，否则用户下次在下载目录打开的还是旧文件
- **评分对标要实时**：总索引中的评分估计应反映最新指标，不要沿用旧版分数
- **进化日志 vs 状态文件**：`evolution-log.md` 有时记录手动cycle（如 Cycle 7.5），`evolution-state.json` 记录引擎cycle。刷新材料时以 state.json 的 `version` + `quality_metrics` + `evolution_count` 为准

### Phase 5: Post-Refactoring Material Alignment Audit ⚡

当系统/项目经历了重大重构（删除文件、版本升级、架构变更）后，必须进行**材料一致性审计**。不要假设现有材料仍然正确。

#### Trigger
- 用户说 "系统有变动，检查材料是否需要更新"
- 系统/项目版本号跳跃（如 v3.x→v4.x）
- 删除/重命名了核心目录或文件（如 `core/` → 删除，Python脚本 → SKILL.md）
- 关键指标（质量分数、信任度、八维评分）有重大变化

#### Audit Items

| 检查项 | 方法 | 典型问题 |
|--------|------|----------|
| **版本号** | 逐文件搜索硬编码版本号 | 材料写 3.0.0，系统已是 4.2.0 |
| **已删除文件引用** | 全文搜索脚本/模块名 | `skill_network.py`、`evolution_scheduler.py` 已不存在 |
| **关键指标** | 对比材料中的评分/分数 vs 当前系统 | 八维综合 68%→85%，材料还写 68% |
| **文件结构描述** | 对比材料中的项目目录树 vs 实际 | 材料还展示 `core/` 目录，实际已删除 |
| **技术栈表** | 检查组件名是否匹配当前架构 | 引用 Python 脚本作为组件，实际已是纯 SKILL |
| **视频内容** | 检查视频是否展示已删除的架构细节 | 视频中的 Python 代码界面可能已不准确 |

#### Workflow

1. **建立差异基线**：读取 `submission-summary.json` + `evolution-state.json` 获取系统当前版本和指标
2. **逐文件审计**：对每个竞赛材料文件，检查上述6项
3. **分级标记**：
   - 🔴 必须更新：版本号、已删除文件引用、评分
   - 🟡 建议更新：文件结构、技术栈表、数据层描述
   - ✅ 无需更新：纯概念描述、哲学文档、表单模板
4. **批量修复**：按 🔴→🟡 顺序修正，更新 `submission-summary.json` 中的版本和状态
5. **归档旧文档**：如果旧架构文档（如技能树探索、旧审计报告）仍在，加归档声明而非删除

#### Pitfalls

- **不要默认材料正确**：系统重构后，所有引用系统细节的材料都需要验证
- **概念层 vs 实现层**：概念描述（架构图、哲学）通常不受重构影响，实现描述（技术栈、文件名）几乎必定过时
- **系统级文档也要同步**：根目录下的 `falsification-summary.md`、`evolution-state.json` 等系统状态文档也可能有过时引用（如 Python 文件名、旧版本号）。审计范围应超出竞赛 docs/ 目录。`evolution-state.json` 本身是权威源，用它的 scores 覆盖所有材料中的硬编码评分
- **视频需要甄别**：如果视频展示的是概念动画（架构图、流程图），即使重构后也可用；如果展示的是具体代码界面或脚本运行，则需要重录
- **多个视频版本**：用户可能有 _最终版、_专业版、_高码率 等多个版本，先确认哪个是最终版再审
- **提交前统一版本声明**：所有材料修完后，确保文档开头/结尾的"最后更新"时间戳一致

### Phase 6: Cleanup & Archive

重构或大版本升级后，根目录和目标目录下会积累大量旧文件。必须主动清理。

#### Targets

| 文件类型 | 典型示例 | 动作 |
|----------|----------|------|
| **旧Python脚本** | `scripts/*.py`、`docs/gen_*.py` | 移入 `archive/v3-legacy/` |
| **旧版本视频** | `_最终版.mp4`、`_高画质.mp4`、`_高码率.mp4` | 只保留一个确定的最终版，其余移入 `archive/video-intermediates/` |
| **视频中间件** | PNG帧、TS片段、re-encoded segments、临时音频 | 移入 `archive/video-intermediates/` |
| **旧测试报告** | `test-results/`、`outputs/test_results/` | 移入 `archive/v3-legacy/` |
| **旧状态文件** | `falsification-framework.json`、`trust-system.json`、`verification_report.json` | 移入 `archive/v3-legacy/` |
| **旧策划文档** | `TODO.md`、`SUBMISSION_PLAN.md`、`docs/*skill-tree*` | 移入 `archive/v3-legacy/` |
| **旧运行输出** | `outputs/atom*_output.json`、`outputs/cache/`、`outputs/context/` | 移入 `archive/v3-legacy/` |

#### Workflow

1. **创建 `archive/` 目录**（如不存在）
2. **分类归档**：`v3-legacy/`（旧代码/旧文档/旧配置）和 `video-intermediates/`（视频中间件）
3. **保留最简核心文件**：最终MP4 + PPTX源码 + PDF + 叙述文本
4. **不要删除** — 全部移到 `archive/` 下，可随时恢复
5. **更新 `submission-summary.json`**：去掉归档文件的引用

#### Pitfalls

- **视频中间件可能重用**：如果比赛在4天内，视频中间件（scene segments、narration.aac）可能用于重制。确认最终视频没问题后再归档。
- **旧测试报告的数据价值**：如 `test-results/` 含历史趋势数据，但 v4.x 架构变更后已无参考价值。
- **不要归档还在用的东西**：检查 `outputs/runs/` 下的最新运行输出仍然有用。

2. **Generate submission checklist**:
   - File: `SUBMISSION_PLAN.md` with all items, deadlines, and status
   - Include: what's ready, what needs user action, and the final submission deadline

3. **Deliver the complete package**:
   - All generated files in `docs/` directory
   - Summary of what's been prepared
   - Clear list of remaining action items for the user

## Competitive Narrative — Theory-to-Engineering Bridge

当项目既有理论深度（哲学框架、方法论体系、个人认知模型）又有工程实现（系统架构、技术组件、落地效果）时，创建**概念映射表**作为叙事桥梁，可以显著提升材料深度和区分度。

### 映射表格式
```
超级个体理论概念     |  Synthos 工程实现
─────────────────────┼────────────────────────
硅基副脑（第二大脑） |  7个认知原子构成的流水线
知识积木法            |  知识获取→提取→关联
人机共创              |  Agent原生执行+人在回路
```

### 适用场景
- 竞赛需要展示"创新性"时，哲学框架提供了理论原创性证明
- 大多数参赛者只展示"AI工具能做什么"，理论→工程叙事展示了"人应该成为什么样的研究者"
- 为视频脚本/PPT提供"为什么→怎么做→结果"的三段论结构

### 可用素材源
- 项目架构文档中的方法论/哲学声明
- NotebookLM 中关于个人知识管理、认知框架的笔记本
- 用户的个人知识管理方法论笔记

## Pitfalls

- **证明材料双版本管理**：竞赛需要"原始版本（盖章）+ 匿名版本（评审）"两套材料。原始版本含团队姓名和机构名称，用于大赛管理系统（仅组委会可见）；匿名版本隐去个人身份信息，用于专家评审。两个版本的文档结构一致，差异仅在：① 机构/人名→去掉或替换为通用描述 ② 公章栏→删除 ③ 标题注明版本。用同一个 Markdown 源文件维护两份，减少不一致风险。参见 `references/supporting-materials-cn.md`。
- **Privacy separation — personal vs public materials**: Competition materials (建设说明书, 技术路线图, 申报书, 演示PPTX/PDF, 视频) go in `docs/`. Personal analysis reports (NotebookLM audit, internal review notes, evaluation analysis, non-public project assessments) MUST go in a **dedicated private directory** OUTSIDE the project tree (e.g. `~/notebooklm-audit/`). The project `docs/` is typically public (GitHub, shareable link) — personal files there leak private data. Create the private dir with `mkdir -p ~/<project-name>/` if it doesn't exist. NEVER place personal/system-internal analysis into `docs/` by default.
- **Git tracking when separating competition materials**: When moving competition files out of the main project repo into a local-only directory, git will show the old paths as `D` (deleted) and the new dir as `??` (untracked). Handle in this order: (1) `git add` the deletions from the old location → (2) add the new dir path to `.gitignore` (e.g. `/竞赛材料/`) → (3) remove stale `.gitignore` exceptions (e.g. `!docs/Synthos_Full_Demo.pptx` if that file no longer exists in docs/) → (4) commit + push the cleanup → (5) verify with `git status` that the competition dir no longer appears. Do NOT `git add` the competition dir.
- **提交前硬编码指标核查**：竞争材料中的数字（进化轮次、质量分数、技能数、吸收数等）随时间推移会逐渐过时。提交前必须重读 `evolution-state.json` 获取最新值，与材料中的硬编码数字逐项比对。即使材料是7天前创建的，差异也可能大到需要全部重刷。建议在 Audit Mode 的 Inventory Check 阶段就自动执行一次性指标对比。
- **`submission-summary.json` 与材料同步**：刷新材料的数字后，`submission-summary.json` 的 `quality_metrics` 块（`evolution_count`, `average_quality`, `external_absorptions`, `active_skills` 等字段）必须同步更新。材料写 53轮/0.98/18吸收 但 summary 还写 41轮/0.975/5吸收 的话，评审时会被认为材料不一致。在 Phase 4 刷新的最后一步，用 `write_file` 直接覆写 `submission-summary.json` 的完整 metrics 块。
- **Identity anonymization**: Many competitions require submissions WITHOUT personal names, school names, or identifiable info. Remind the user of this constraint for all materials and videos.
- **PDF encoding**: Chinese PDFs from Chinese universities often have encoding issues. Always test `pdftotext` output. If garbled, try `pdfminer.six` as fallback or extract via OCR.
- **Word count strictness**: 建设说明书 简介 typically has 2000 character limit, 应用成效 1000. Count carefully with Python. Chinese character count, not bytes.
- **Multi-column form templates**: Some competition docx templates have 4-column table with Col1=label and Cols2-4 all sharing mirrored content. Setting cells[1].text is often sufficient — cells[2] and cells[3] may auto-mirror in rendering. When in doubt, set all three consistently to be safe.
- **Form fields**: Official forms often have hidden or conditional fields. Always ask the user for team member details BEFORE generating the guide.
- **Video naming**: Competition video files have strict naming conventions. Check and enforce.
- **Professional category mapping**: For Chinese medical education competitions (e.g., 全国医学教育智能体大赛), the "专业大类" field uses clinical specialty classification (临床专业). Default to "临床医学类" / "临床医学" as the category, and "细分专业" should reflect the actual target audience (e.g., "临床医学（AI辅助临床科研与教学）"). Do NOT default to "医学信息学" or "医学教育技术".
- **Teaching project integration**: When a project has both a research tool AND a teaching component, integrate the teaching project as a core application case, not an afterthought. 73+ teaching sources provide strong evidence for "可推广性与生态价值" and "实施与效果" scoring dimensions. This can boost overall scores by 5-8 points. Map the teaching project's methodology (e.g., CRISP-DM) to the tool's workflow for credibility in "内容科学性与规范性".
- **CRISP-DM + TRIPOD+AI mapping**: For clinical prediction model competitions, mapping the 6-stage CRISP-DM methodology to the tool's workflow stages and referencing TRIPOD+AI reporting standards adds significant credibility. Include this in both the建设说明书 and 技术路线图.
- **NotebookLM source analysis**: For large notebooks (70+ sources), use `notebooklm source list` for metadata classification and `notebooklm summary` for high-level overview. Do NOT attempt to read individual sources — it times out. The metadata alone reveals the project structure.
- **Commitment letter**: Competition submission includes a "参赛选手承诺书" (6 clauses). Generate it with each clause mapped to the project's actual context. Must be printed and hand-signed (or electronic signature).
- **Pillow installation**: `pip3 install Pillow` fails on Debian-based systems with "externally-managed-environment". Use `pip3 install Pillow --break-system-packages` or install via `apt install python3-pil`. The `execute_code` sandbox may not have Pillow pre-installed even if the system does — always check with `python3 -c "from PIL import Image"` first, and fall back to terminal execution if Pillow is missing in sandbox.
- **PIL RGBA color format**: Pillow's `draw.line()` and `draw.ellipse()` don't support CSS-style `rgba()` strings. Use tuple format `(R, G, B, A)` or use solid colors. This is a common error when porting CSS color codes.
- **申报书 PDF**: The official form is filled by the user on the competition website (http://MeedTAC.mh.chaoxing.com for Chinese contests). Generate a template with pre-filled content, but the user must fill it out on the website and export the PDF themselves.
- **docx template cells**: When modifying docx templates with python-docx, always inspect the full table structure first (rows, columns, merged cells) before modifying. Templates often have merged cells, hidden rows, or unexpected column counts. When setting Chinese fonts: `rPr` may already exist but `rFonts` may lack `w:eastAsia` attribute (it may only have `w:hint`). Always do: check `rPr is None` → create it; check `rFonts is None` → create it; then `rFonts.set(qn('w:eastAsia'), font_name)`. Don't try to replace the rFonts element — just add the attribute. For clearing cell content: use `p.clear()` on the first paragraph, then add runs.
- **docx table structure discovery**: Before modifying any table, print all rows and cells to understand the layout. Templates often have the first row as headers, subsequent rows as data, and the table may have empty cells that should be left alone. Always verify content after writing by re-reading the file.
- **User data**: Do not fabricate team member names, hospital names, or personal info. Generate templates with placeholders and ask the user to fill in real data.
- **Check common download dirs**: Users may have prepared PDFs (申报书, 演示材料) in `~/下载/` or `~/Downloads/` but not yet moved them into the project. Always check these locations during Inventory Check — you might find existing materials that save hours of work.
- **DuckDuckGo Lite as search fallback**: When `browser_navigate` times out (common with JS-heavy pages) and curl to Google returns 400, use DuckDuckGo Lite (`https://lite.duckduckgo.com/lite/`) with POST + `kl=cn-zh` for Chinese results. This is the most reliable web search method in a CLI-only environment.
- **Competition URL unreachable**: Many Chinese competition portals (like `http://MeedTAC.mh.chaoxing.com`) are internal systems that require login or heavy JS. Don't rely on them for requirement extraction; find .edu.cn mirror pages instead.
- **Project directory discovery**: When the user says "Synthos目录下面应该已经有写好的材料" or similar, do NOT keep searching filesystem blindly. Ask directly: "项目目录在哪里？" then systematically check: (1) `find /media -maxdepth 3 -type d -iname "*projectname*"` (2) `find /mnt -maxdepth 3 ...` (3) common mount points like `/media/$USER/`, `/mnt/`, removable drives. Users often have projects on external drives. Also check Trash (`~/.local/share/Trash/files/`) — projects may have been accidentally deleted.
- **Always start from the original source file**: When the user asks for "最小改动" (minimal changes) to an existing PPTX/DOCX — e.g. "只改数字, 新增一页" — always start from the ORIGINAL unmodified file, NOT from a previously-optimized/modified version. Building on an already-modified file produces unbounded scope creep. Workflow: (1) find the original source (`*Original*` or backup) (2) verify with `python3 -c "from pptx import Presentation; prs=Presentation('file.pptx'); print(len(prs.slides))"` (3) Apply ONLY the requested changes (4) Save as output. If a previously-modified version exists (e.g. `*_优化版*`), it should replace the original only with explicit user confirmation — never assume.
- **PPTX quality metric updates**: When updating PPTX for a system that has evolved, the quality dashboard slides are the most important. Use python-pptx to find the specific shape by its current text (e.g., "0.97") and replace it. For text labels (e.g., "六维"→"七维"), use `para.clear()` + `para.add_run()` to preserve formatting. After all updates, re-export to PDF with LibreOffice.
- **PPTX minimal modification — stack discipline**: When the user asks for "只改数字" or "最小改动", enforce strict stack discipline: (1) Always start from the ORIGINAL (never from a previously-modified version) (2) Before writing code, dump the original slide structure with `python3 -c "from pptx import Presentation; prs=Presentation('ORIGINAL.pptx'); [print(f'Slide {i}: {[s.text_frame.text[:40] for s in slide.shapes if s.has_text_frame][:5]}') for i, slide in enumerate(prs.slides)]"` (3) Apply only the delta: N numerical replacements + M new slides + Z deletions (4) Verify output page count = original + M - Z before delivering. If you accidentally modified an already-modified version, scrap it, restore from original, and redo from scratch.
- **DOCX vs MD 双版本验证**：当同时维护 Markdown 源文件和 DOCX 填写版时，patch 只更新了.md 不意味着.docx 也同步。两种格式可能分布在不同的目录，DOCX 的指标可能比 MD 滞后数日。必须在 Phase 4 刷新中对**两个版本都执行指标检查**，使用 python-docx 搜索 .docx 中的旧数值并替换。
- **封面图片单独生成**：比赛封面（1920×1080 PNG）不能依赖 PPTX 导出。用 Pillow 程序化生成比设计软件更可控。流程：Python脚本 → 指标更新 → 检查匿名合规（无姓名/学校）→ git add 到私有仓库。见 `references/cover-generation-pillow.md`。
- **私有仓库提交流程**：竞赛材料（含个人信息的申报书、视频中间件等）不适合推送公开仓库。流程：`gh repo create name --private` → `.gitignore` 排除大文件 → `git add` 核心文件 → `git push`。主仓库和竞赛仓库保持分离。
- **Demo PDF regeneration**: After updating a PPTX, always regenerate the demo PDF: `libreoffice --headless --convert-to pdf docs/NAME.pptx --outdir docs/`. This ensures the demo PDF always matches the PPTX. If the user also has a copy in `~/下载/`, sync it: `cp docs/NAME.pdf ~/下载/`.

## Demo Video Production

> Absorbed from: `competition-video-production` skill (archived). The video production pipeline is an implementation detail of the competition submission workflow, not a standalone domain.

### Pipeline Overview

```
PPTX (python-pptx) → PDF (LibreOffice) → PNG (pdftoppm 300dpi) → Per-segment MP4 → TS concat → Final MP4 + Narration
```

Two paths exist depending on whether the user already has presentation slides:

**Path A: Full Production** (generate PPTX from scratch using python-pptx with dark navy theme, accent cards, data viz)
**Path B: Fast Track** (existing PPTX → PDF → PNG → video, lighter pipeline)

### Key Patterns

| Pattern | Description | Reference |
|:--------|:------------|:----------|
| Per-slide audio alignment | Generate per-slide audio, measure exact duration, compose per-segment videos with precise sync | `references/per-slide-alignment-pattern.md` |
| Edge-TTS rate adjustment | TTS reads faster than speech; use `rate` param to hit duration targets | `references/per-slide-alignment-pattern.md` |
| TS binary concat | MP4 concat with `-c copy` drops frames when all segments share start_time=0. Convert to TS, cat, re-encode. | `references/ffmpeg-video-audio-sync.md` |
| Dark theme PPTX | python-pptx with slate-900 bg, blue/teal accent, card-based layout | `references/pptx-video-workflow.md` |
| Narration-slide alignment | Every spoken number must be visually verifiable on the current slide | `references/per-slide-alignment-pattern.md` |

### Data Integrity Rules

- Every number in narration must trace to a project data file (evolution-state.json, etc.)
- No fabricated market sizes, hardware specs, or performance claims
- If uncertain → use qualitative language, not invented numbers
- Verify all numbers against source project files BEFORE generating any content

### ⚠️ Critical Pitfalls

| Pitfall | Symptom | Fix |
|:--------|:--------|:-----|
| `-shortest` with concat demuxer | Video way longer than audio, silence at end | Use two-pass: create video first, then trim to narration duration with `-t` |
| MP4 concat drops frames | Total video duration shorter than sum of segments | Convert to TS, binary concat, re-encode to MP4 |
| MP4→TS data loss | 25% data drop when using `-preset ultrafast/fast` | Use `-preset medium -crf 18` for source MP4 encoding |
| Narration describes wrong slide | Fixed durations don't match variable TTS pace | Use per-slide audio generation + measurement |
| Efficiency metrics confusion | SEARCH (10x) vs REVIEW (4-6x) mix-up | Verify against actual slide text after PNG export |

### Reference Files

- `references/video-production-ffmpeg.md` — Original FFmpeg + Pillow + edge-tts workflow (basic)
- `references/per-slide-alignment-pattern.md` — Per-slide narration alignment, the key quality pattern
- `references/ffmpeg-video-audio-sync.md` — FFmpeg sync troubleshooting, TS concat, stream trimming
- `references/pptx-video-workflow.md` — PPTX-to-video pipeline with dark theme design language
- `references/mp4-ts-conversion-data-loss.md` — Data loss case study and fix for MP4→TS conversion
- `references/mp4-ts-data-loss-case-study.md` — Full case study with timeline
- `references/gen_professional_video.py` — Reusable professional video generation script
- `references/pptxgenjs-dark-tech.pptx.md` — Dark-tech PPTX design patterns
- `templates/pptx_scene_generator.py` — PPTX scene generation template
- `references/user-context.md` — User-specific video production preferences

## Specialized Sub-Workflows

### 医学装备创新大赛

当竞赛通知为医学装备/医疗器械创新类竞赛时，加载 `references/medical-equipment-competition.md`。

该类竞赛的独特需求：
- PDF通知通常为扫描件，需 OCR 处理
- 评审四维：创新性·实用性·市场潜力·团队实力
- 需提交报名表 + 商业计划书（9章结构）
- 团队信息从论文作者列表中提取
- 可将多个技术模块打包为"完整解决方案"（硬件+算法）
- 定价参考：进口同类30-80万元 → 国产替代<10万元
- 创客组上限7人

#### ⚠️ 输出格式：默认生成 Word (.docx) 而非 Markdown

**核心教训（2026-05-30）**：提交材料（报名表、商业计划书）的最终交付格式应为 **Word (.docx)**，不是 Markdown。用户在提交前会检查 Word 版。不要在 md 阶段等用户问"是不是要形成word的"——直接生成 docx。

**无模板时，用 python-docx 从零创建**：多数医学装备竞赛不提供 docx 模板，需要从零构建。工作流见 `references/medical-equipment-competition.md` 的 Phase F。

#### ⚠️ 创客组人员上限策略

| 情况 | 策略 |
|:-----|:------|
| 用户未提供完整名单 | 预留名额（不填满） |
| 用户主动提供了全部成员 | **直接填满上限**，不替用户做保留决策 |
| 用户询问"还能加人吗" | 报已完成人数和剩余名额 |

不要自作主张留空——等用户指示。如果用户给的信息已达上限，直接写入。

## Support Files
- `references/competition-submission-workflow.md` — End-to-end workflow from PDF extraction through final submission, with competition-specific adaptations (medical education AI contests, general tech innovation, government grants)
- `references/video-production-ffmpeg.md` — FFmpeg + Pillow + edge-tts workflow for producing 6-10 minute MP4 demo videos, with pitfalls and quick reference
- `references/docx-template-modification.md` — Verified patterns for modifying .docx templates (Chinese font setting, cell clearing, table targeting)
- `references/pdf-extraction-tricks.md` — Tips for handling Chinese PDFs, encoding issues, table extraction
- `references/scoring-matrix-template.md` — Template for scoring criterion to capability mapping
- `templates/video-script-6min.md` — Template for 6-minute demo video script with timestamps
- `references/supporting-materials-cn.md` — 证明材料编写指南（测试账号、原创主体、知识产权佐证、双版本管理）
- `templates/recommendation-letter.md` — Template for institutional recommendation letter (Chinese)
- `references/chinese-competition-categories.md` — Mapping of Chinese competition "专业大类" field to correct clinical/academic classifications (临床医学类, 基础医学类, 公共卫生与预防医学类, etc.)
- `references/python-docx-quickref.md` — python-docx API quick reference for DOCX creation and template filling (absorbed from python-docx skill)
- `references/fill_form.py` — reusable template filling script (absorbed from python-docx skill)
- `references/pdf-stamp-replacement.md` — Replace the last PDF page with a scanned/stamped page using ImageMagick + pdftk