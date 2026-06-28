---



name: native-mcp
description: "Directory index for native-mcp: native-mcp"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "tool_request: dict -> native_result: dict (output, error_handling, integration_notes)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `mcp_config: str` — 用户请求描述、上下文信息
- **output**: `result: dict — MCP原生配置`


## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

> 对应原则：P2（机械原子暴露输入输出规范）



# Native Mcp

MCP客户端 — 连接服务器, 注册工具(stdio/HTTP)。

详细内容请加载对应 references/ 目录下的参考文件。
