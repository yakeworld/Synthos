# paper.tex 双位置问题（v50）

## 现象

论文目录中 `paper.tex` 可能同时存在于两个位置：
1. 根目录：`paper-name/paper.tex`（完整编译输出）
2. 子目录：`paper-name/01-manuscript/paper.tex`（step 副本或历史残留）

## 影响

使用 `find paper-name -name "paper.tex"` 无深度限制时，会返回**两个结果**，导致计数虚高。例如：
- 根目录 paper.tex = 47 个
- 子目录 paper.tex = 64 个（01-manuscript 中的副本）
- 总计 = 111（远大于实际论文数）

## 修复

- 根目录统计：`find -maxdepth 2 -name "paper.tex"` （只匹配根级别）
- 子目录统计：`find -mindepth 3 -name "paper.tex"` （只匹配子级别）
- 或使用 `ls */paper.tex` 仅匹配根目录

## 规则

disk_sync 时只统计根级别 `paper.tex`。子目录中的副本不计入完成计数。