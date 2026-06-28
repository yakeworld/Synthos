# 小红书内容包模板

## 内容包结构

每个小红书内容包应包含以下文件：

```
<content-name>/
├── index.md              ← 内容包索引（必须）
├── 正文.md               ← 完整帖子正文
└── images/               ← 配图素材（可选）
    ├── cover.svg         ← 封面图
    ├── figure1.svg       ← 图1
    └── figure2.svg       ← 图2
```

## index.md 模板

```markdown
# <内容名称> — 小红书内容包

## 文章
- 正文: [正文.md](../正文.md)

## 配图清单

| # | 文件名 | 用途 | 说明 |
|---|--------|------|------|
| 1 | [cover.svg](images/cover.svg) | 封面图 | 描述 |
| 2 | [figure1.svg](images/figure1.svg) | 图1 | 描述 |

## 发布建议

1. **封面**: cover.svg
2. **图2**: figure1.svg
3. 正文：分段发

## 脱敏检查

- [ ] IP地址已替换
- [ ] 真实路径已泛化
- [ ] 敏感信息已移除
```
