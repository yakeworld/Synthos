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

> 对应原则：P2（机械原子暴露输入输出规范）



# Native Mcp

MCP客户端 — 连接服务器, 注册工具(stdio/HTTP)。

详细内容请加载对应 references/ 目录下的参考文件。
