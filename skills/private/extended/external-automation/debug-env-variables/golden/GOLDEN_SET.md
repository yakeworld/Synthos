---
name: debug-env-variables
description: debug-env-variables 金测集 — 环境变量消失点定位与修复（机械原子）可执行测试
---

# 金测集: debug-env-variables

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (DEBU-001~006)。
> 本技能为机械原子（atom_type: mechanical），输入/输出契约：
> `missing_var: str, shell_context: enum(interactive|bash -c|Python subprocess) -> diagnosis: str, fix: config`。
> 每个 case 验证变量消失点定位的逐层验证法（DEBU-006）与修复可靠性排序（修复有序原则），
> 期望输出采用语义等价判定（diagnosis 定位点 + fix 排序校验）。

## 核心能力

| # | 能力 | 关键约束 |
|---|------|---------|
| 1 | 逐层验证定位消失点 | 父进程 → `bash -c` → Python 子层，用 `os.environ` / `echo` 对比（DEBU-006） |
| 2 | `.bashrc` 守卫诊断 | 交互有 / 非交互无 → `case $- in *i*)` 守卫是嫌疑（DEBU-001） |
| 3 | 引号/subprocess 边界诊断 | `bash -c` 有但 Python 无 → 引号嵌套被外层 shell 消费（DEBU-005） |
| 4 | 修复可靠性排序 | export 前移 → `BASH_ENV` → `.api_key` 文件回退 → `/etc/environment`，勿倒置 |
| 5 | 自动化不倚 `.bashrc` | CI/cron/subprocess 场景必须用 `/etc/environment` 或文件回退；密钥不入 `.bashrc`（DEBU-003/004） |

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路径：`.bashrc` 守卫导致变量在非交互 shell 丢失 | diagnosis 精确定位 `case $- in *i*)` 守卫；fix 按可靠性排序给出（export 前移/BASH_ENV/文件回退）；区分交互 vs 非交互边界 |
| case_002 | 正常路径：`subprocess.run(shell=True)` 引号嵌套边界导致 Python 层丢失 | diagnosis 定位引号/subprocess 边界（bash -c 有 / Python 无）；fix 首推文件回退，含 `&&` 链接/heredoc 替代方案（DEBU-005/004） |
| case_003 | 错误路径：输入参数不完整/非法（missing_var 为空 + shell_context 非合法枚举） | 必须拒绝执行 —— 错误含上下文（哪个参数缺失/非法）+ 恢复建议（合法枚举清单），不凭记忆断言 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: `diagnosis` 必须命中 `.bashrc` 的 `case $- in *i*)` 守卫这一消失点；`fix` 列表按可靠性有序（export 前移 < BASH_ENV < .api_key 文件回退 < /etc/environment），且输出同时含 `diagnosis` 与 `fix` 两段
- case_002: `diagnosis` 必须定位到引号/subprocess 边界（而非 `.bashrc` 守卫）；`fix` 首推文件回退（`.api_key`），并含 `&&` 链接或 heredoc 的替代写法；不硬编码密钥
- case_003: 必须拒绝并返回 Golden Error 路径 —— 错误信息含"请求回声 + 具体缺失/非法参数名 + 合法 shell_context 枚举（interactive / bash -c / Python subprocess）+ ≥2 条恢复建议"，禁止在输入无效时输出 diagnosis/fix 结论

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: diagnosis 定位 + fix 有序配置
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- `diagnosis` 必须是三个消失点之一（.bashrc 守卫 / 引号与 subprocess 边界 / 从未设置），不可模糊
- `fix` 必须是按可靠性排序的列表，顺序不得倒置（修复有序原则）
- 错误路径必须同时含 `context` 与 `recovery` 两个字段
- 任何修复建议不得将敏感凭证写入 `.bashrc`（DEBU-004 安全约束）

## 关联

- SKILL.md Genes: DEBU-001~006
- SKILL.md 验证清单: 5 项（消失点定位 / fix 排序 / 区分非交互与 subprocess 边界 / 修复后可用 / 输出含 diagnosis+fix 无凭记忆断言）
- SKILL.md IO_CONTRACT: `missing_var: str, shell_context: enum -> diagnosis: str, fix: config`
