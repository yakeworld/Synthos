# source add RPC 失败诊断记录（2026-05-23）

> 记录 `notebooklm source add` 返回 "Invalid argument" 时的完整排查链。
> 根源：Google NotebookLM 后端 API 参数格式变更。

## 症状

```
notebooklm source add file.md
Error: Failed to register file source for file.md: RPC o4cbdc returned null
result with status code 3 (Invalid argument).
```

## 排查路径

```
1. 确认版本: notebooklm --version → 0.3.4
2. 升级: pipx upgrade notebooklm-py → 0.4.1 → 仍失败
3. 安装 main 分支: pipx inject notebooklm-py notebooklm-py@https://
   github.com/teng-lin/notebooklm-py/archive/refs/heads/main.tar.gz → 0.5.0-dev
   → 错误信息改善（泛化 → 具体 status code），根因未修
4. 查 GitHub: github.com/teng-lin/notebooklm-py/issues/474（open）
   → 确认是已知上游问题，Google 改了 ADD_SOURCE_FILE / ADD_SOURCE RPC 参数
5. 尝试 Python API: client.sources.add_text() 同样失败
6. 确认 note create 正常工作: notebooklm note create "..." 可被 Gemini 索引
```

## 涉及的 RPC 端点

| RPC | 用途 | 状态 |
|:----|:-----|:-----|
| ADD_SOURCE_FILE (o4cbdc) | 文件类型 source 注册 | ❌ status 3 |
| ADD_SOURCE (izAoDd) | 文本类型 source 注册 | ❌ status 9 / 泛化错误 |

## 已测试的通路

| 通路 | 结果 | 说明 |
|:-----|:-----|:------|
| `source add file.md` | ❌ | 文件注册 RPC 参数不兼容 |
| Python API `add_text()` | ❌ | 底层 RPC 相同 |
| Python API `add_file()` | ❌ | 注册步骤失败 |
| `note create` | ✅ | 使用不同 RPC 端点，正常索引 |
| `ask` | ✅ | 可检索 note 内容 |
| `source list` | ✅ | 查询类 RPC 正常 |

## 当前方案

使用 `note create` 作为文件上传的降级通路。Note 的文本内容被 Gemini 以同等深度索引，`ask` 可以正常检索和引用。验证方法：上传后运行 `notebooklm ask "根据刚才上传的文件，..."`，确认能正确回答。
