---
name: prose-cluster-hybrid-citation-fix
description: '**Python batch for section-grouped anchors**:'
signature: 'prose-cluster-hybrid-citation-fix -> private: synthetic skill for prose cluster hybrid citation fix'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: '**Python batch for section-grouped anchors**:'
    signature: 'prose-cluster-hybrid-citation-fix -> private: synthetic skill for prose cluster hybrid citation fix'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---

|
| `halmagyi02` | vHIT / vestibular testing | Introduction → Background | "video head impulse testing (vHIT)" |
| `curthoys09` | Semicircular canal anatomy | Introduction → Background | "vestibular testing including caloric irrigation" |
| `parnes99` | Endolymphatic sac treatment | Introduction → Background | "endolymphatic sac and stria vascularis" |
| `iahn17` | Meniere's classification | Introduction → Background | "chronic vestibular disorder characterized by" |
| `headimpulse` | Head impulse modeling | Introduction → Gap | "The head impulse test computational modeling" |
| `raissi19` | PINN framework | Methods → PINN Architecture | "\\subsection{PINN Architecture}" |
| `chen18` | Neural ODE | Methods → PINN Architecture | "\\subsection{PINN Architecture}" |
| `sanchez22` | Biochemically informed NeuralODE | Methods → PINN Architecture | "\\subsection{PINN Architecture}" |
| `jagtap22` | Conservative PINNs | Methods → PINN Architecture | "\\subsection{PINN Architecture}" |

**Python batch for section-grouped anchors**:

```python
additions = [
    # Group: vestibular testing → Introduction
    ("video head impulse testing (vHIT); and (c) audiometric assessment",
     "video head impulse testing (vHIT)\\cite{halmagyi02,curthoys09}; and (c) audiometric assessment"),
    # Group: endolymphatic sac → Background
    ("within the endolymphatic sac and stria vascularis, with a baseline production rate",
     "within the endolymphatic sac and stria vascularis\\cite{parnes99}, with a baseline production rate"),
    # Group: Meniere's → Background
    ("a chronic vestibular disorder characterized by episodic vertigo",
     "a chronic vestibular disorder\\cite{iahn17} characterized by episodic vertigo"),
    # Group: head impulse → Gap
    ("The head impulse test computational modeling represents the only existing",
     "The head impulse test computational modeling\\cite{headimpulse} represents the only existing"),
    # Group: PINN methods → PINN Architecture
    ("\\subsection{PINN Architecture}",
     "\\subsection{PINN Architecture}\n\nWe follow the physics-informed neural network framework\\cite{raissi19,chen18, sanchez22, jagtap22} for solving the inverse ODE problem."),
]
for anchor, new_text in additions:
    tex = tex.replace(anchor, new_text)
```

## Verification

```bash
python3 -c "
import re
with open('01-manuscript/paper.tex') as f: tex = f.read()
bibitems = set(re.findall(r'\\\\bibitem\{([^}]+)\}', tex))
cite_keys = re.findall(r'\\\\cite\{([^}]+)\}', tex)
cites = set()
for ck in cite_keys:
    for k in ck.split(','): cites.add(k.strip())
orphans = bibitems - cites
print(f'D10a: {len(cites & bibitems)}/{len(bibitems)} = {(len(cites & bibitems)/len(bibitems))*100:.0f}%')
print(f'Orphans: {len(orphans)}' + ('' if not orphans else ': ' + ', '.join(sorted(orphans))))
"
```

## Compile Verification

```bash
cd 01-manuscript/
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex  # second pass for cross-refs
grep -c "undefined" paper.log  # should be 0 (or just cross-ref warnings)
grep -oP "Output written on paper\.pdf \(\d+ pages" paper.log
```

## When This Pattern Occurs

This pattern is most common in papers where:
1. The clinical/domain calibration paragraph is a single paragraph with dense prose author-year references (pressure ranges, clinical thresholds)
2. The remaining bibitems cover foundational literature (methodology, anatomy, clinical tests, classification systems) that the LLM generated as a reference block but never anchored in text
3. The paper has a standard IMRaD structure but the Introduction/Methods sections contain mostly domain description without formal citations

## Related Patterns

- **Pure prose variant** (0 `\cite{}`, bibitems present, no prose author-year refs): see `references/orphan-bibliography-trap.md` — map each bibitem to its contextual location in the paper
- **Pure inline variant** (0 prose refs, bibitems have no anchor): see `ref/orphan-bibliography-inline-manual-fix.md`

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

- [ ] 已建立"引用键-主题-章节-文本锚点"映射表，每个 bibitem 都有明确的章节归属与锚点（PROS-001）
- [ ] 同一主题/方法簇的多个 bibitem 在单一锚点合并为一条 `\cite{a,b,c}`，未逐句重复插入（PROS-002）
- [ ] 密集散文段落的引用插入使用了精确短语 anchor 做字符串替换，替换后上下文完整未断裂（PROS-003）
- [ ] 方法论框架类引用插入在对应 `\subsection` 标题后并附解释性句子（PROS-004）
- [ ] 批量替换后运行 Python 脚本，`\cite` 键与 `\bibitem` 键集合交集覆盖率（D10a）已报告且 Orphans 为 0（PROS-005）
- [ ] 执行了双次 `pdflatex` 编译，`paper.log` 中 `grep -c "undefined"` 为 0，页码正常输出（PROS-006）

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

<!-- 以下重复块已去重合并（与上方 24-141 行相同），仅保留首个"验证清单 · VERIFICATION" -->

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[PROS-001]** 当存在未引用的参考文献 (bibitems) 时 → 建立“引用键-主题-章节-文本锚点”映射表以定位插入位置
- **[PROS-002]** 当多个参考文献属于同一主题或方法簇时 → 在单一文本锚点处合并插入多个 `\cite` 键以减少冗余
- **[PROS-003]** 当需要在密集散文段落中插入引用时 → 使用精确的短语匹配 (anchor) 进行字符串替换以保留上下文完整性
- **[PROS-004]** 当引用涉及方法论框架时 → 在对应的 `\subsection` 标题后插入解释性句子并附带引用以增强逻辑连贯性
- **[PROS-005]** 当执行批量引用修复后 → 运行脚本验证 `\cite` 键与 `\bibitem` 键的集合交集以检测孤儿引用
- **[PROS-006]** 当验证引用完整性时 → 执行双次 `pdflatex` 编译并检查日志中无 "undefined" 错误以确保交叉引用解析正确
