# NotebookLM Layer B — Project Isolation Pitfalls

> **记录**: NotebookLM 项目间 source 污染导致审计报告错误的案例。

## 2026-06-07 crispdm-wdbc 案例

### 问题
第一次创建项目后，PDF 源返回 `status: error`，但未删除。项目被之前 session 的 sources（scc-mathematical-morphology 论文）污染。`notebooklm ask` 返回的是 semicircular canal morphology 论文的报告，而非 crispdm-wdbc。

### 根因
NotebookLM 的 `source add` 即使返回 "Added source:" 也可能在后台标记为 error。旧项目的 sources 不会自动清除。

### 修复步骤
1. 立即执行 `notebooklm source list` 检查所有源状态
2. 删除任何 `error` 状态的源：`notebooklm source delete <id> -y`
3. **最佳实践**：Layer B 审计始终创建全新项目 `notebooklm create "name-$(date +%Y%m%d)"`
4. 新项目中只上传当前论文相关文件（PDF→text fallback + bib + quality report）
5. 确认所有 source status 为 `ready` 后再执行 `notebooklm ask`

### 验证清单
- [ ] 项目是本次 session 全新创建的
- [ ] 无 error 状态的 source
- [ ] source list 中仅包含当前论文相关文件
- [ ] PDF 已转为 text 上传（避免 PDF 直接上传 error）
