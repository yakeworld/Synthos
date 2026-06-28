---
name: continuous-delivery-pipeline
description: "持续交付管道 — CI/CD、自动化测试、版本管理、发布策略。为Synthos系统实现自动化测试和交付流程。"
version: 1.0.0
allowed-tools:
- terminal
- execute_code
- browser
- skill_manage
- read_file
- write_file
- send_message
metadata:
  synthos:
    version: 1.0.0
    priority: P1
    atom_type: skill
    author: Synthos
    description: "持续交付管道 — CI/CD、自动化测试、版本管理、发布策略"
    signature: 'pipeline -> test + version + release + review'
    related_skills: ["software-development", "github", "quality-gate", "system-reliability-engineering"]
triggers:
  - 需要验证新技能可用性
  - 论文管线G1-G7质量门需要执行
  - 需要版本管理或发布策略
  - Cron任务脚本需要语法验证
  - 代码/配置变更需要测试验证

---

# continuous-delivery-pipeline

> 持续交付管道设计，为Synthos系统实现自动化测试、版本管理、发布流程和质量门控。

## 触发条件

- 需要验证新技能可用性
- 论文管线G1-G7质量门需要执行
- 需要版本管理或发布策略
- Cron任务脚本需要语法验证
- 代码/配置变更需要测试验证

## 执行步骤

1. **技能验证** — 新技能入库前自动检查:
   - 语法检查: `python3 -m py_compile` (Python)、`bash -n` (Shell)
   - SKILL.md结构: YAML头完整、name/description/version存在、metadata.synthos完整
   - 门控条件: BOUNDARY存在、IO_CONTRACT存在、EVIDENCE_SCHEMA存在
   - 依赖检查: `allowed-tools`中列出的工具是否存在

2. **论文质量门控** — G1-G7质量门自动化:
   - G1: LaTeX语法检查 → `pdflatex -interaction=nonstop-mode paper.tex`
   - G2: 引用完整性 → 检查`cite{}`与`.bib`条目匹配
   - G3: 引用真实性 → Crossref/PubMed验证DOI
   - G4: 格式合规 → 检查模板一致性、章节结构
   - G5: 数据可复现 → 检查是否有生成脚本
   - G6: 质量评分 → 多维度评分(0-1)
   - G7: 最终审核 → 综合通过才发布

3. **版本管理** — 语义化版本策略:
   - MAJOR.MINOR.PATCH: 不兼容修改/功能新增/问题修正
   - 技能版本: v1.0.0 → v1.1.0(新功能) → v1.1.1(修复)
   - 论文版本: v1.0.0-draft → v1.0.0-revised → v1.0.0-final
   - Git标签: `git tag -a skill/v1.0.0 -m "Skill v1.0.0 release"`

4. **渐进式发布** — 金丝雀发布流程:
   - Step1: 测试环境验证 → 功能正确性
   - Step2: 小范围使用 → 10%流量/用户
   - Step3: 监控1-2小时 → 观察指标
   - Step4: 如果健康 → 全量推广
   - Step5: 如果异常 → 立即回滚

5. **回滚机制** — 一键回滚能力:
   - 技能回滚: `git checkout skill/v0.9.0 -- skills/`
   - 论文回滚: `git checkout paper/v0.9.0 -- outputs/papers/`
   - 配置回滚: 备份当前配置，失败时恢复备份

6. **质量报告** — 每次发布后生成:
   - 测试通过率、构建时长、部署时长
   - 错误数、回滚次数、用户反馈
   - 改进建议

## Pitfalls

- **版本标签污染**: Git标签必须语义化。不要用`latest`、`final`这类无意义标签。每个标签对应一个明确的版本号。
- **回滚不测试**: 回滚机制必须经过测试。每次重大变更前先验证回滚流程是否可行。没测试过的回滚等于没有回滚。
- **金丝雀监控不足**: 金丝雀环境不是"随便用用"。必须有明确的监控指标(错误率、延迟、成功率)和明确的阈值(错误率>5%就回滚)。
- **质量门控漏项**: G1-G7不是摆设。每个门必须有明确的通过/失败标准。通过标准必须可自动化验证，不是人工判断。
- **发布频率失衡**: 太频繁(每天多次)→不稳定；太稀疏(每月一次)→迭代慢。建议: 日常小变更(每周)、功能发布(每2周)、重大版本(每月)。

## 参考

- Git Semantic Versioning: https://semver.org/
- Jenkins Pipeline: https://www.jenkins.io/doc/book/pipeline/
- GitHub Actions: https://docs.github.com/en/actions

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
