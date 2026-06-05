# 同类手稿合并策略

## 适用场景
当work目录中有多篇手稿内容重叠时（同一主题的不同版本/不同详略程度），需合并为一篇论文。

## 实战案例
bppv-mss-lsc-bppv：两篇外半规管BPPV最小刺激策略手稿合并：
- 源文件1（810行）：综合临床讨论版，含中文注释
- 源文件2（555行）：结构化版，含完整Abstract/IMRaD
- 策略：以源文件2结构化版为主框架，融合源文件1的讨论内容

## 合并步骤
1. 识别重复：比较标题、Abstract、核心结论
2. 选择主框架：选结构化更完整、参考文献更全面的版本
3. 内容融合：Introduction合并/重叠保留独特/取更详细Methods
4. 去重引用：两篇手稿的引用标记合并为统一bib条目

## 中文注释过滤
```python
lines = content.split('\n')
english = [l for l in lines if not any('\u4e00'<=c<='\u9fff' for c in l)]
```
