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

# Prose Cluster Hybrid Citation Fix---





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

