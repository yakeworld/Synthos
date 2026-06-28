# LaTeX 引用替换回退方案 — patch 失败时用 sed

> 2026-06-25 HCS-3WT 实战：7篇虚构引用需替换时，patch 工具因 Unicode 字符(Demšar中的š)和精确空格匹配失败，改用 sed 一行搞定。

## 问题

`patch` 工具依赖精确字符串匹配。在 LaTeX 文件中替换 `\cite{...}` 引用时可能失败的原因：

| 失败原因 | 示例 | 
|:---------|:-----|
| Unicode 字符 | Demšar (š) 在 patch 中不匹配 |
| 隐藏空格/tab | 源文件可能用不同空格 |
| LaTeX 转义 | `~` 在字符串边界处理不同 |
| 超长字符串 | 多引用并排 `\cite{A,B,C,D}` 超过模糊匹配能力 |

## 回退方案

当 patch 在 LaTeX 引用替换上失败时，立即用 `sed` 替代：

```bash
# 基本替换：替换一个引用键
sed -i 's/\\cite{OldKey}/\\cite{NewKey}/g' paper.tex

# 删除一个引用（从多引中移除）
sed -i 's/\\cite{Keep1,Remove1,Keep2}/\\cite{Keep1,Keep2}/g' paper.tex

# 替换多引用为单引用
sed -i 's/\\cite{Fake1,Fake2,Fake3}/\\cite{Real1}/g' paper.tex

# 替换多引用中的部分引用
sed -i 's/\\cite{A,Unwanted,B}/\\cite{A,B}/g' paper.tex
```

## 安全操作流程

```bash
# 1. 先备份
cp paper.tex paper.tex.bak

# 2. 预览改动（不加 -i）
sed 's/\\cite{OldKey}/\\cite{NewKey}/g' paper.tex | grep -n 'cite{' | head -20

# 3. 确认无误后执行
sed -i 's/\\cite{OldKey}/\\cite{NewKey}/g' paper.tex

# 4. 验证改动
grep -n 'OldKey\|NewKey' paper.tex

# 5. 删备份或保留
# rm paper.tex.bak  # 确认无误后
```

## 多引用替换陷阱

sed 不支持 `\n` 跨行匹配。下列模式需用不同方法：

```bash
# ✅ 单行引用替换（sed 适合）
sed -i 's/\\cite{A,B,C}/\\cite{D}/g' paper.tex

# ❌ 跨行引用（使用 patch 的 context-aware 模式）
# 或先合并行再操作
```

## 验证

替换后必须：
1. grep 确认旧键不再出现
2. grep 确认新键已出现
3. 运行 `pdflatex` 编译验证
4. 检查 `paper.log` 中 `undefined` 为零
