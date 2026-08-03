# VERIFICATION_GATES — Synthos 质量闸门

> 守门如守城。门不破，城不陷。

## 门级架构

```
L0  动灵层          — 意图→输出对齐检查
L0.5 数据诚实门       — 所有数值可追溯至原始数据
G1  结构完整性门      — SKILL.md frontmatter 合规
G2  契约完备门        — IO_CONTRACT 覆盖率 ≥90%
G3  依赖可达门        — 引用的脚本/工具/API在运行环境中存在
G4  编译通过门        — Rust/Python 项目零 error 编译
G5  安全审计门        — 无敏感信息泄露、无越权文件操作
G6  回归防护门        — 核心原子 golden test 全通过
G7  自进化闭环门      — 有定期自我评估与改进机制
```

## 当前通过状态

| 门 | 状态 | 说明 |
|----|:----:|------|
| L0 动灵层 | ✅ 默认通过 | 每次对话自动对齐 |
| L0.5 数据诚实 | ✅ | 论文管线已验证 |
| G1 结构完整性 | ✅ | 157 skills, 96.8% IO_CONTRACT |
| G2 契约完备 | 🟡 待提升 | knowledge-acquisition 已修复，目标 100% |
| G3 依赖可达 | 🟡 需定期验证 | 依赖外部API(jabkit, doi-fetch, S2) |
| G4 编译通过 | ✅ | rproxy/doi-fetch/jabkit-rs 均零警告 |
| G5 安全审计 | 🟡 待执行 | 需定期扫描 .env/.secret 泄露 |
| G6 回归防护 | 🟡 待创建 | 本文件定义 golden test 框架 |
| G7 自进化闭环 | 🔴 待部署 | cron 调度未激活 |

## Golden Test 框架

每核⼼原子至少覆盖：

1. **SKILL.md 结构** — version + signature + IO_CONTRACT 存在
2. **引用完整性** — 引用的依赖工具/脚本在 PATH 中
3. **输出样例** — 至少一个已知可复现的输入→输出对

## 检查周期

| 门 | 周期 | 执行方式 |
|----|:----:|----------|
| G1-G2 | 每周 | `synthos-probe` 自动扫描 |
| G3 | 每月 | 手动或cron检查工具链 |
| G4 | 每次修改后 | `cargo build --release` |
| G6 | 每次修改前 | 本地运行 golden test |
| G7 | 每日 | 自进化 cron |
