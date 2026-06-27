# 论文作图完整性审计

## 铁律
1. 每张图必须有对应脚本：05-figures/figN.pdf → 03-code/generate_figN.py
2. 每张图必须在 LaTeX 中引用
3. 副本必须一致（md5 相同）
4. PDF 必须有 matplotlib 标记（strings | grep matplotlib）
5. 无脚本的 PDF = P0 问题，必须通过 PDF 反向工程或 notebook 提取修复

## 审计管线（5 步）
1. 列出 05-figures/ 下所有 .pdf/.png
2. 对每张 fig：在 03-code/ 搜索对应 .py
3. 在 .tex 中搜索 includegraphics(figN)
4. 比较多副本一致性（md5）
5. 对每张 PDF：strings | grep -i matplotlib

## 输出
- 表格报告，标记 P0（缺失脚本/无引用）和 P1（备份/不一致）
- 修复优先级按 P0→P1 排序