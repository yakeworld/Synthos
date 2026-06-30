---
name: infrastructure-as-code
description: "基础设施即代码 — 配置管理、环境一致性、版本控制、自动化部署。为Synthos系统实现IaC实践。"
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
    description: "基础设施即代码 — 配置管理、环境一致性、版本控制、自动化部署"
    signature: 'iac -> config + consistency + version + deploy'
    related_skills: ["continuous-delivery-pipeline", "system-reliability-engineering", "cron-system-maintenance"]
triggers:
  - 需要配置管理或环境一致性
  - 需要版本控制或自动化部署
  - 系统配置变更需要验证
  - 需要环境重建或故障恢复
  - 用户要求IaC实践

---

# infrastructure-as-code

> 基础设施即代码方法论，为Synthos系统实现配置管理、环境一致性、版本控制和自动化部署。

## 触发条件

- 需要配置管理或环境一致性
- 需要版本控制或自动化部署
- 系统配置变更需要验证
- 需要环境重建或故障恢复
- 用户要求IaC实践

## 执行步骤

1. **配置管理** — 所有配置纳入版本控制:
   - Hermes配置: `~/.hermes/config.yaml` (agent/models/tools/skills/cron)
   - 技能配置: `~/.hermes/skills/*/SKILL.md` (metadata/triggers/steps)
   - Cron配置: `~/.hermes/cron/jobs.json` (schedule/prompt/dependencies)
   - 论文配置: `outputs/papers/*/paper.tex` (模板/引用/质量门)

2. **配置验证** — 变更前验证:
   - YAML语法: `python3 -c "import yaml; yaml.safe_load(open(f))"`
   - SKILL.md结构: name/description/version/metadata.synthos/triggers/steps
   - Cron job: prompt语法正确、依赖存在、schedule有效
   - 任何配置变更必须通过验证才能部署

3. **环境一致性** — 开发/测试/生产环境统一:
   - 环境配置文件: `environments/{dev,staging,prod}.yaml`
   - 环境差异通过配置管理，不是硬编码
   - 环境重建通过代码实现: `git checkout env-config && apply`
   - 每次环境变更后运行健康检查验证一致性

4. **版本控制** — Git工作流:
   - 配置分支: `git checkout -b feature/config-update`
   - 变更PR: 代码审查→自动验证→合并
   - 版本标签: `git tag -a config/v1.0.0 -m "Config v1.0.0"`
   - 回滚: `git checkout config/v0.9.0 -- configs/ && git commit`

5. **自动化部署** — 安全部署流程:
   - 备份当前配置: `cp config.yaml config.yaml.backup`
   - 验证新配置: 语法+结构+依赖检查
   - 部署: 复制新配置到目标位置
   - 重启服务: `systemctl restart hermes-agent` (或等价操作)
   - 健康检查: 验证服务恢复正常
   - 失败回滚: 如果健康检查失败，恢复备份

6. **故障恢复** — 自动/手动恢复:
   - 配置恢复: `cp config.yaml.backup config.yaml && restart`
   - 技能恢复: 从Git回滚到上一个稳定版本
   - 数据恢复: 从备份恢复知识图谱/论文/技能

## Pitfalls

- **配置漂移**: 生产环境手动修改配置是最常见的IaC破坏者。所有配置变更必须通过代码(配置文件+Git)进行，禁止手动编辑生产配置。
- **备份不测试**: 备份必须经过恢复测试。备份文件存在不代表可恢复。每次重大变更后验证备份可恢复。
- **环境差异累积**: 开发/测试/生产环境的差异会随时间累积，导致"在我机器上是好的"问题。所有环境差异必须在配置文件中明确管理，不是通过环境特有的补丁。
- **过度抽象**: IaC不是越抽象越好。对于简单的配置管理，YAML文件足够。不要为简单场景引入Terraform/Helm等重型工具。工具复杂度应与问题规模匹配。

## 参考

- Terraform: https://www.terraform.io/docs/
- Ansible: https://docs.ansible.com/
- Git Best Practices: https://git-scm.com/book/en/v2

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

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


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。



# Infrastructure As Code

