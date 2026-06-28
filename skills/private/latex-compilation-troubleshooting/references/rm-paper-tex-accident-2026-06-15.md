# rm -f paper.* 事故报告

## 事故概述
**日期**：2026-06-15  
**影响**：完整论文源文件 `paper.tex` 被永久删除  
**严重性**：🔴 CRITICAL — 数据丢失

## 事故经过
```bash
cd /home/yakeworld/Synthos/outputs/papers/3d-eyeball-iris-segmentation
rm -f paper.*   # 意图：删除编译产物
# 结果：paper.tex 也被删除！
```

## 根因分析
`paper.*` 通配符匹配所有以 `paper.` 开头的文件：
- `paper.aux` ✓（预期）
- `paper.log` ✓（预期）
- `paper.pdf` ✓（预期）
- **`paper.tex` ✗（灾难性）**

glob 扩展：`paper.*` → `paper.aux paper.bbl paper.bak.pre-improve paper.blg paper.improved paper.log paper.out paper.pdf paper.spl paper.tex`

## 铁律
**绝对禁止在任何情况下使用 `rm -f paper.*`**。

### 安全替代
```bash
# 只删除编译产物（不包含 .tex）
rm -f paper.aux paper.log paper.out paper.blg paper.bbl paper.pdf paper.spl

# 删除前确认
ls paper.*          # 检查列表
grep -v '.tex' paper.*   # 过滤掉 .tex
```

### 安全守则
1. 任何包含 `*` 的通配符删除前，先运行 `echo rm -f <pattern>` 预览
2. 永远只删除已知后缀的文件
3. 任何涉及 `rm` 的操作前，先确认 `paper.tex` 存在且有备份
4. 修改文件前必须先创建 `.bak` 备份

## 后续防护
- latex-compilation-troubleshooting 技能已更新，加入 🔴 标记
- paper-pipeline 技能已在 Common auto-assembly traps 中记录备份要求
- 未来所有涉及 `rm` 的操作必须在回复中明确列出删除的文件清单