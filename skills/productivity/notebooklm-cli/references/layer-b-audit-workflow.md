# Layer B Paper Quality Audit — Workflow

> **触发场景**: paper-queue.json 中 issue=layer_b 的任务。

## 完整流程

1. **确认论文就绪**
   - `paper.tex` 存在且 ≥5000 字（检查 `wc -l`）
   - `references.bib` 存在且非空
   - PDF 可提取文本层 (`pdftotext file.pdf - | wc -c` > 0)

2. **创建 NotebookLM 项目**
   ```
   notebooklm create "PaperName — Layer B Quality Check"
   ```

**关键：每次 Layer B 必须创建全新项目！**

⚠️ **项目污染陷阱**：NotebookLM 项目可能残留之前 session 的 sources（error 状态的源不会自动清除）。如果复用旧项目，旧 source 会被 NotebookLM 作为上下文参与评估，导致审计报告分析的是错误的论文。

⚠️ **Source ID 残留 / 幽灵源（v0.4.x CLI 已知问题）**：`notebooklm source delete <id> -y` 返回 "Deleted" 但 `source list` 仍显示相同 ID（内容可能不同，来自之前 session）。删除操作不可靠，不可信赖。

**正确操作模式**（session 2026-06-07 验证）：
1. **直接创建全新项目**：`notebooklm create "fresh-name-$(date +%s)"` — 不要试图清理旧项目
2. 新 notebook 的 `source list` 保证为空
3. 在所有新 notebook 上传源
4. 如果 `source list` 显示任何非当前 session 创建的源 → 丢弃该 notebook，从头再创建一个
5. **永远不要依赖 `source delete` 来清理污染**

**session 2026-06-07 案例**：首次创建项目后 PDF 源报错，但项目已被之前 session 的 sources 污染，第一次 ask 返回的是 semicircular canal morphology 论文的报告（不是 crispdm-wdbc）。删除源后 `source list` 仍显示旧 ID。创建全新 notebook 并只上传 crispdm-wdbc 相关源后，审计报告正确。

**session 2026-06-07 案例**：首次创建项目后 PDF 源报错，但项目已被之前 session 的 sources 污染，第一次 ask 返回的是 semicircular canal morphology 论文的报告（不是 crispdm-wdbc）。创建全新项目并只上传 crispdm-wdbc 相关源后，审计报告正确。

3. **上传源文件**（按优先级，用全新项目）
   a. PDF 正文 — 先检查 `pdftotext file.pdf - | wc -c` 确认有文本层
      - 若 `source add paper.pdf` 返回 `status: error` → 立即 `notebooklm source delete <id> -y`，回退到 `pdftotext paper.pdf - > /tmp/paper-text.txt` + `source add --type text "$(cat /tmp/paper-text.txt)"`
   b. references.bib — `cat references.bib | notebooklm source add --type text "$(cat references.bib)"`
   c. 已有质量报告 — `notebooklm source add quality-report.md`

4. **验证源状态**
   ```
   notebooklm source list
   # 所有关键源 status 应为 "ready"
   # 若有 "error" 源 → notebooklm source delete <id> -y
   ```

5. **发送 Layer B 评估请求（纯英文 ASCII）**
   ```
   notebooklm ask "As Layer B quality audit, conduct a comprehensive second quality review of this paper. Evaluate: 1) Originality/importance of scientific contribution; 2) Methodological rigor; 3) Credibility/reproducibility of results; 4) Literature reference quality; 5) Writing/logical structure; 6) Top 3-5 improvement suggestions; 7) Overall quality score 0-1."
   ```
   ⚠️ 必须使用纯英文，中文 Prompt 会触发 security scan 拦截

6. **保存报告**
   - 将回答写入 `<paper-dir>/07-quality/layer-b-report.md`
   - 记录质量评分和 verdict

7. **清理**
   - 删除 error 状态的源
   - 可选：删除整个 notebook 释放资源

## 决策阈值

| 质量分数 | 判定 |
|---------|------|
| ≥0.85 | T1 通过，可进入校准分计算 |
| 0.75-0.84 | T2 临界，需改进后复检 |
| <0.75 | 不通过，退回写作阶段 |

## 注意事项

- NotebookLM 回答需 30-60 秒，timeout 至少 90 秒
- 同一项目禁止并行 ask（会串话）
- 上传大文件（>80KB）时 `$(cat ...)` 会失败，需用 Python subprocess
- 每次 run 只处理一个 paper 的 Layer B
