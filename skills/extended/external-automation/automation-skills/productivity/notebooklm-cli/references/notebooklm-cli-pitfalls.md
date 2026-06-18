# NotebookLM CLI 陷阱

## 1. Source ID 残留 / 幽灵源 (CLI v0.4.x)
- `notebooklm source delete <id> -y` 返回 "Deleted" 但 `source list` 仍显示该 ID（可能内容已变，来自之前 session）
- **修复**：不要删除，直接 `notebooklm create` 全新 notebook。新 notebook 的 source list 保证为空。
- 如果 `source list` 显示任何非当前 session 创建的源 → 丢弃该 notebook 重新创建。
- **记录**：session 2026-06-07 验证，4 次 delete 后旧 ID 仍出现在 source list。

## 2. PDF 源静默失败
- `notebooklm source add file.pdf` 返回 `status: error` 无 stderr
- **修复**：`pdftotext file.pdf - > /tmp/paper-text.txt` + `source add --type text "$(cat /tmp/paper-text.txt)"`

## 3. 安全扫描拦截中文字符
- `notebooklm ask` 含中文触发 `confusable_text` HIGH 安全扫描
- **修复**：纯英文 ASCII Prompt

## 4. 同一项目并行 ask 串话
- **修复**：串行执行，每次只问一个问题

## 5. Shell 参数限制 (>80KB)
- `$(cat bigfile)` 超过 80KB 报错
- **修复**：Python subprocess 读取

## 6. YAML frontmatter 解析错误
- `---` frontmatter 导致 click 解析错误
- **修复**：上传前剥离 frontmatter

## 7. .ipynb 文件 400 错误
- NotebookLM 不支持 ipynb 上传
- **修复**：提取代码 cell 为文本

## 8. Source 状态缓存延迟
- 刚上传 source 可能 `list` 返回空列表
- **修复**：重试 2-3 次

## 9. Shared 项目 source delete 伪成功
- 仅 Owner 有效
- **修复**：用 Owner 身份操作

## 10. 未知源类型警告
- `UnknownTypeWarning: Unknown source type code 0`
- **修复**：忽略警告，不影响功能
