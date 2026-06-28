---
name: prose-cluster-hybrid-citation-fix
description: "Fix pattern for D10a=0% papers where prose author-year references cluster in one paragraph + remaining bibitems have no prose anchor (hybrid of prose and inline variants)."
version: 1.0.0
signature: "prose-cluster-hybrid-citation-fix -> processed_result"
---

# Clustered Prose + Standalone Bibitems Hybrid Citation Fix

> **Trigger**: D10a=0%, 0 `\cite{}` keys in text, but paper has BOTH prose author-year references (concentrated in 1-2 paragraphs) AND bibitems with no prose mention.
>
> **Not pure prose variant**: Prose refs cluster in one area, not scattered throughout.
> **Not pure inline variant**: Prose refs exist, unlike pure inline where bibitems have no textual anchor at all.

## Detection

```bash
python3 << 'PYEOF'
import re

with open("01-manuscript/paper.tex") as f:
    tex = f.read()

bibitems = re.findall(r'\\bibitem\{([^}]+)\}', tex)
cite_keys = re.findall(r'\\cite\{([^}]+)\}', tex)
prose_refs = re.findall(r'\([A-Z][a-z]+(?:\\s+et\\s+al\\.?)?(?:\\s+\\d{4}(?:;\\s*[A-Z][a-z]+\\s+\\d{4})*)\)', tex)

print(f"Bibitems: {len(bibitems)}")
print(f"Cite keys: {len(cite_keys)}")
print(f"Prose author-year clusters: {len(prose_refs)}")

# Check prose distribution
lines_with_prose = [i+1 for i, line in enumerate(tex.split('\n')) 
                    if re.search(r'\([A-Z][a-z]+\s+\d{4}\)', line)]
if lines_with_prose:
    print(f"Prose refs found on lines: {lines_with_prose[:10]}...")
    print(f"Prose ref span: line {min(lines_with_prose)} to {max(lines_with_prose)}")
    if max(lines_with_prose) - min(lines_with_prose) < 10:
        print("→ CONCENTRATED pattern (all prose refs in 1-2 paragraphs)")
    else:
        print("→ SCATTERED pattern")
else:
    print("→ 0 prose refs — check for pure prose variant (see references/orphan-bibliography-trap.md)")
PYEOF
```

**Detection signal (hybrid)**: `len(prose_refs) > 0` AND `len(cite_keys) == 0` AND prose refs span < 15 lines (clustered).
**Detection signal (pure prose)**: `len(prose_refs) == 0` AND `len(cite_keys) == 0` AND `len(bibitems) > 0`.

## Fix Strategy (2-phase)

### Phase 1: Convert clustered prose refs to `\cite{}`

Prose refs often cluster in a clinical calibration paragraph:

```latex
% Before (line ~167):
Normal endolymph pressure: 0--5 mmH$_2$O (Streeten 1998; Horix 2016).
Hydropic pressure: 15--30+ mmH$_2$O (Lanzieri 2011; Excoffon 2019).
Symptom threshold: 6--12 mmH$_2$O (Nakashima 2004; Kim 2023).

% After:
Normal endolymph pressure: 0--5 mmH$_2$O (\cite{streeten98}; \cite{horix16}).
Hydropic pressure: 15--30+ mmH$_2$O (\cite{lanzieri11}; \cite{excoffon19}).
Symptom threshold: 6--12 mmH$_2$O (\cite{nakashima04}; \cite{kim23}).
```

**Batch replacements** — replace the full prose block as one operation:

```python
python3 -c "
path = '01-manuscript/paper.tex'
with open(path) as f:
    tex = f.read()

# Replace all prose clusters at once
replacements = [
    ('(Streeten 1998; Horix 2016)',
     '(\\\\cite{streeten98}; \\\\cite{horix16})'),
    ('(Lanzieri 2011; Excoffon 2019)',
     '(\\\\cite{lanzieri11}; \\\\cite{excoffon19})'),
    ('(Nakashima 2004; Kim 2023)',
     '(\\\\cite{nakashima04}; \\\\cite{kim23})'),
    ('Streeten et al. (1998)',
     'Streeten et al.~\\\\cite{streeten98} (1998)'),
]
for old, new in replacements:
    tex = tex.replace(old, new)

with open(path, 'w') as f:
    f.write(tex)
"
```

### Phase 2: Add section-grouped new anchor points for remaining bibitems

Remaining bibitems (those NOT matched in Phase 1) need new `\cite{}` anchors. Map each to its natural section:

| Bibitem | Topic | Section | Add after |
|:--------|:------|:--------|:----------|
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
- **Pure inline variant** (0 prose refs, bibitems have no anchor): see `references/orphan-bibliography-inline-manual-fix.md`

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

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
