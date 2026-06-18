# Source-to-Methods Section Extraction

> Extracting mathematical derivations and algorithm details from NotebookLM or other knowledge sources for the Methods section of a paper.

## When to use

The user has algorithm code, mathematical derivations, or experimental protocols stored in NotebookLM (as pasted text, Markdown, or PDF sources) and wants to write a paper Methods section from it. The key challenge: NotebookLM's `notebooklm ask` command is the only way to retrieve source content, but it times out on long content.

## Workflow

### 1. Inventory the sources

```bash
notebooklm use <notebook_id>
notebooklm source list
```

Identify which source contains the algorithm/math content. Look for "Pasted text" or Markdown sources — these are the most extractable. PDF sources are indexed but raw text extraction via `notebooklm ask` is unreliable.

### 2. Targeted extraction (avoid timeout)

Do NOT ask for "all content" — it will time out (120s+). Instead, extract in this order with focused queries:

| Query | What it returns | Typical time |
|-------|----------------|--------------|
| "输出Pasted Text源中包含的坐标系定义、符号系统和向量变量定义" | Notation, coordinate frames, variable definitions | 10-20s |
| "输出关于[核心公式名称]的完整数学推导过程" | Mathematical derivation with equations | 10-30s |
| "输出[核心函数名称]的完整代码和参数说明" | Algorithm implementation code | 15-30s |
| "输出从输入到输出的完整算法Pipeline/工作流" | Step-by-step workflow | 10-20s |
| "输出硬件系统/实验设备的描述" | Hardware/setup details | 10-20s |

**Key insight:** The multi-turn conversation preserves context across fragments. Each query builds on the previous ones. You can assemble the full picture from 3-6 focused queries.

### 3. Assimilate into LaTeX Methods section

Map extracted content to IMRaD sections:

| NotebookLM content → | Paper section |
|----------------------|---------------|
| Coordinate systems, notation | Methods 2.x — Coordinate system definition |
| Mathematical derivation | Methods 2.x — Mathematical framework |
| Algorithm code | Methods 2.x — Algorithm pipeline |
| Hardware description | Methods 2.x — System setup / Equipment |
| Experimental protocol | Methods 2.x — Experimental protocol |

### 4. Validation

- Every equation in the paper must match the source — trace each `\begin{equation}` back to a specific line in the extracted content.
- If code defines intermediate variables (e.g., `K_x`, `K_y`), the paper must define them first before the solution equation.
- Check that the paper's notation matches the source code's notation (same variable names, same units).

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| NotebookLM truncates code in `notebooklm ask` responses | Re-query with narrower scope: "输出[函数名]完整的函数签名和前10行代码" then "继续输出[函数名]的剩余代码" |
| Extracting code BEFORE math derivation causes timeout on math | **Always extract math first** — mathematical derivations are more compressible in NotebookLM responses (they use LaTeX notation which fits in shorter text). Code tends to be longer and triggers timeout. Order: math derivation → coordinate systems → algorithm pipeline → code snippets |
| `notebooklm ask` times out on "全部内容" requests | Never request "全部内容" or "all content". Use fragmented queries that each target one conceptual chunk. The multi-turn conversation preserves context across queries — you can rebuild the full picture from 3-6 focused answers |
| Pasted text source has inline tabs/spaces not visible | Use `print(repr(text))` when processing extracted code to detect hidden characters |
| Source uses different variable names than paper needs | Define aliases in the paper: `Let {x_i} denote ... (equivalent to variable v_x in the implementation)` |
| Mathematical derivation spread across multiple source files | Extract each source separately, then merge into a single logical derivation flow in the paper |
