# NotebookLM 文件上传限制与变通

## 已知限制

| 文件类型 | 问题 | 变通方法 |
|:---------|:-----|:---------|
| `.py` | 400 Bad Request 上传失败 | 重命名为 `.txt` 后上传（内容不变） |
| 大文件 (>100KB) | 可能超时或400 | 拆分为小节作为 Notes 上传 |
| `config.json` | 有时标记为 Unknown type | 先用 `note create` 保存内容，或用 `.txt` 扩展名 |

## 从 k230_main.py 实践（2026-05-20）

```bash
# ❌ 失败
notebooklm source add k230_main.py    # → 400 Bad Request

# ✅ 成功
cp k230_main.py k230_main.txt
notebooklm source add k230_main.txt   # → ready
rm k230_main.txt
```

## Note create 注意事项

`notebooklm note create` 通过 stdin pipe 传入内容时，标题参数会被子进程捕获为标题，而非内容。正确做法：

```bash
# ❌ 内容通过 pipe 可能不生效
cat file.txt | notebooklm note create "标题"

# ✅ 改用 source add 直接上传
notebooklm source add file.txt
```

## 研究导入超时处理

`notebooklm research wait --import-all` 对50+源结果容易超时。超时后：
1. 研究结果**仍在系统中**
2. 直接用 `notebooklm ask "...查询..."` 分析已发现的结果
3. 不需重新导入
