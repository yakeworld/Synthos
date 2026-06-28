# @openai/codexec@0.141.0 NPM Registry 状态记录

## 时间线

- **2026-06-19**: `@openai/codexec@0.141.0` 从 npm registry 完全移除（E404）
- **2026-06-19 同日**: `@openai/codex`（新包名）恢复，仍为 v0.141.0

## 当前状态

**已恢复**。`npm install -g @openai/codex` 获取 v0.141.0，`codex doctor` 全绿。

## 历史排查记录

`@codexapi/codexclaude`（第三方打包器）内部嵌套 `@openai/codexec@0.141.0`，但该包嵌套的二进制在部分系统上会被 npm 安装为**损坏目录**——`os.listdir` 显示子条目但实际文件不存在（inodes 丢失）。安装后必须验证：
```bash
codex --version  # 如失败 = 损坏
```
验证失败时删除并重装：
```bash
npm rm -g @codexapi/codexclaude
rm -rf ~/.nvm/versions/node/v*/lib/node_modules/@openai
npm install -g @codexapi/codexclaude@2.0.12
```

## 根因

`@openai/codexec@0.141.0` 从 npmjs.org registry 被完全移除（OpenAI 侧操作）。`@openai/codex` 是新包名，功能等同。
