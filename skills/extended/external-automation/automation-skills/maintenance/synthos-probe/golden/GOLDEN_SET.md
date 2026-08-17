# Golden Set — synthos-probe

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 本集合覆盖：正常路径（全量 Probe）与错误路径（路径陷阱 / 缺失原子）。
> 每个 case 对应 `cases/case_XXX.json`（输入）与 `expected/case_XXX.json`（预期输出/错误契约）。

## 测试用例表

| Case | 类型 | 输入摘要 | 预期 |
|------|------|----------|------|
| case_001 | 正常路径 · 全量 Probe | `probe_target="full"`，对 7 核心原子做 has_version / has_signature / has_io_contract 检查，再对全量 SKILL.md 做 benchmark | structural=5/7（research-ideation 缺失），benchmark 全量计数来自 `os.walk`，输出 `SYNTHOS PROBE: structural=0.71, benchmark=1.00, drift=green` |
| case_002 | 错误路径 · 路径陷阱 + 缺失原子 | 对不存在路径 `skills/research-ideation/SKILL.md` 做单原子检查 | `os.path.exists()` 判定文件缺失 → 该原子 has_version=has_signature=has_io_contract=false，错误信息含上下文与恢复建议（正确路径应在 `skills/research/` 层级下且需 `os.path.exists()` 确认） |

## 通过标准

- **case_001**
  - [ ] 7 原子逐一输出 `has_version` / `has_signature` / `has_io_contract`（布尔）
  - [ ] `research-ideation` 三项均为 `false`（实测：`skills/research/research-ideation/SKILL.md` 不存在于当前仓库）
  - [ ] 结构分 = 完全通过数 / 7 = 5/7 ≈ 0.71（非 7/7，防 cycle68 乐观偏差）
  - [ ] benchmark：SKILL.md 计数用 `os.walk` + `"SKILL.md" in fn` 实际遍历（实测 157），不信任 spec 声称数字
  - [ ] git 比较前将绝对路径转为仓库根相对路径（实测全部 tracked）
  - [ ] 根目录 `evolution-state.json` 存在且 `json.load` 可解析
  - [ ] 输出行严格匹配 `SYNTHOS PROBE: structural=X.XX, benchmark=X.XX, drift=green|yellow|red | cycle=N`
  - [ ] signature 判定遵守 SYNT-003：仅 `name:` 不算 signature，需独立 `signature:` 声明
  - [ ] version 判定遵守 SYNT-002：顶层与 `metadata.synthos.version` 嵌套均需检查
- **case_002**
  - [ ] 不抛出未捕获异常；以结构化错误返回
  - [ ] 错误信息包含上下文（实际检查的路径）与恢复建议（确认实际层级路径 / 该原子可能尚未创建）
  - [ ] 不静默跳过，也不把"文件缺失"误报为"结构完整"

## 复现命令

```bash
python3 -c "import json; json.load(open('golden/cases/case_001.json')); json.load(open('golden/expected/case_001.json'))"
python3 -c "import json; json.load(open('golden/cases/case_002.json')); json.load(open('golden/expected/case_002.json'))"
# benchmark 实际计数（凡数必源）：
python3 -c "import os; print(sum(1 for d,_,f in os.walk('skills') for x in f if 'SKILL.md' in x))"
# evolution-state 可解析性：
python3 -c "import json; json.load(open('evolution-state.json')); print('STATE_OK')"
```

> 注：expected 数值为 **2026-06 实测快照**（P0 凡数必源）。后续仓库演化会使 7 原子集合 / 计数变化，
> 验证时应以重新执行的独立计数为准（SYNT-007：不信任上一周期记录）。
