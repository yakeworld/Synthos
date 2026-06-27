# Quality Gate — CHANGE_LOG

## v2.40.0 (2026-06-27)
## v2.9.4 (2026-06-18)
- 三项铁律 + Codex-tmux调度协议

## v2.9.5 (2026-06-23)
- 多源交叉验证、消融值检测、政府申报方案

## v2.13.0 (2026-06-24)
- state.json内部不一致检测、多JSON源ensemble

## v2.40.0 (2026-06-27)
- cross_dataset_consistency陷阱检测

## v2.9.2 (2026-06-18)

### Added
- 完整结构文件: BOUNDARY.md, IO_CONTRACT.md, EVIDENCE_SCHEMA.md
- L0.5 数据诚实门：论文中可验证数据声明的源文件支撑验证
- G5 引用质量两层次检查法：形式检查 + 实质检查
- 与 paperjury 的协作关系定义
- 提交材料准备清单 (Cover Letter, Highlights, Graphical Abstract, Author Info, Submission Checklist)
- 引用恰当性检查创建新技能 `citation-appropriateness-verification`
- PDF文件错误陷阱文档：DOI相似性导致的下载错误

### Changed
- G5引用质量评估：新增DOI覆盖率统计分析（86.8%论文bib无DOI）
- L4内容级评审：G7通过后自动触发sci-paper-quality-review
- 质量门通过阈值统一为 0.85

## v2.9.0 (2026-06-13)

### Added
- 四层质量架构：L1响应级、L2项目级、L3管线级、L4内容级
- G1-G7原子闸门定义
- 通用铁律：无录不过、引质为要、一维一渡、向不正则功废、凡数必源

### Changed
- 从单道检查升级为分层质量门体系

## v2.0.0 (2026-06-01)

### Added
- 初始质量门框架
- 基础检查项定义
