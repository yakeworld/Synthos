# GOLDEN_SET.md — codex-install-guide

> 对应原则：P2（机械原子：给定输入 → 可验证的执行结果 + 状态）
> golden_set_origin: self_defined

## 设计依据

本技能是机械原子（atom_type: mechanical）：输入为安装/共存/profile 请求 + 上下文，
输出为执行计划与验证结果。金标准为自设（self_defined），验证目标：**给定相同的环境描述，
技能能否产出正确的包选择、正确的共存隔离判断、正确的 profile 完整性检查，并在错误路径上
给出正确的根因与修复动作**。

判定的语义化规则（检查项在 expected 中以 `checks` 键给出，逐条布尔判定）：
- 包名必须精确匹配官方包 `@openai/codex`（CODE-001）
- 第三方付费打包器必须被显式拒绝（CODE-002）
- 共存判断必须同时引用二进制名与配置路径隔离（CODE-003）
- profile 缺失类错误必须定位为 HIGH/静默超时根因并给出 profile 文件模板（CODE-005/006）
- status 字段必须与判定一致（success 仅当全部 checks 为 true）

## 测试用例表

| case | 名称 | 类型 | 输入摘要 | 期望要点 | 关联 Genes |
|------|------|------|----------|----------|-----------|
| case_001 | 标准安装 + opencode 共存 | 正常 | 无 codex，已有 opencode，要求安装 Codex CLI | install_package=@openai/codex，共存隔离成立，验证清单全过 | CODE-001/003/004 |
| case_002 | 用户请求旧包名/付费打包器 | 错误 | 请求 `@openai/codexec` 或 `@codexapi/codexclaude` | 拒绝并纠正为 `@openai/codex`，status=error | CODE-001/002 |
| case_003 | cron profile 缺失导致批量超时 | 错误 | cron 引用 profile `amax` 超时，profiles 目录无 amax.config.toml | 根因=profile 缺失，给出 profile 文件模板，验证 codex -p amax | CODE-005/006 |

## 通过标准

- **pass_threshold: 0.80**（3 个 case 至少 2 个通过）
- 每个 case 判定 = 该 case 的 `checks` 全部为 true 且 status 一致
- case_002/003 为错误路径：status 必须为 error 且 rejected_packages / 根因定位必须命中
- 权重区分：case_001 为 critical（主路径），case_002/003 为 high（防错路径），避免全 critical 失区分度

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-27 | 初始自设金标准，3 个 case（1 正常 + 2 错误） | Synthos Agent |
