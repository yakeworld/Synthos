# 技能吸收策略

## 核心原则

1. **奥卡姆剃刀**: 优先最简技能链，拒绝冗余
2. **类比思维**: 通过语义匹配发现跨领域技能复用
3. **持续进化**: 定期扫描外部技能源，吸收新能力

## 扫描来源

### 1. Anthropic 官方技能
- URL: https://github.com/anthropics/skills
- 包含: 17 个官方技能
- 类型: pdf, docx, xlsx, skill-creator, mcp-builder, claude-api 等

### 2. agentskills.io 生态
- URL: https://agentskills.io
- 包含: 多个兼容 Agent Skills 规范的技能和客户端
- 类型: 各种专业领域技能

### 3. 其他来源
- GitHub 搜索: "Agent Skills" + 关键词
- 社区贡献: 用户提交的技能
- 自建技能: 内部专用技能

## 语义匹配算法

### 当前实现
```python
# 简单关键词匹配
our_keywords = set(our['description'].lower().split())
ext_keywords = set(external['description'].lower().split())
similarity = len(intersection) / len(union)
```

### 改进方向
1. **上下文感知**: 考虑词语的上下文关系
2. **领域知识**: 引入领域特定的关键词权重
3. **Embedding**: 使用更高级的语义嵌入技术

## 吸收优先级

### P1 (高优先级)
- **pdf → knowledge-extraction**: 增强PDF解析能力
- **docx → argument-expression**: 增强文档格式化

### P2 (中优先级)
- **doc-coauthoring → argument-expression**: 增强协作编辑
- **skill-creator → task-router**: 增强技能优化

### P3 (低优先级)
- **pptx → argument-expression**: 未来扩展PPT输出

## 执行流程

1. **扫描**: 运行 `skill_absorber.py`
2. **匹配**: 分析语义相似性
3. **计划**: 生成吸收计划
4. **执行**: 下载、分析、修改、测试
5. **验证**: 确保符合规范和预期效果

## 注意事项

- 不是所有外部技能都适合吸收
- 确保吸收的技能与当前任务相关
- 吸收后的技能必须仍然符合 Agent Skills 规范
- 定期更新吸收报告
