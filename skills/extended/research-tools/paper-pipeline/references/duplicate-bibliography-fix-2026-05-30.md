# 重复 bibliography 修复实战（2026-05-30 3d-sobel-edge-detection）

## 问题

论文 `article.tex` 中包含两对 `\bibliography{references}` 命令：

```
Line 658: \bibliographystyle{IEEEtran}
Line 659: \bibliography{references}     ← 第一组（附录前）
...
Line 793: \bibliographystyle{IEEEtran}  
Line 794: \bibliography{references}     ← 第二组（end{document}前）
Line 796: \end{document}
```

## 根因

跨 cron 周期编辑的累积效应：
1. 前一轮在附录前插入了 `\bibliography{references}`（在论文主结构修改时加入）
2. 后一轮又在 `\end{document}` 前追加了另一组 `\bibliography{references}`
3. 两轮之间无人检查 `grep -c '\\bibliography{'` → 重复未发现

## 检测

```bash
# 快速检测
grep -c '\\bibliography{' article.tex
# 若返回 ≥2 → 重复

# 定位
grep -n 'bibliography' article.tex
```

## 修复

保留最后一组（紧邻 `\end{document}` 前），删除靠前的：

```bash
# 方法A: 删除靠前的重复（利用唯一上下文定位）
# 第一组前有 \balance 行，后跟 % APPENDIX
# 删除 3 行：\bibliographystyle{...} + \bibliography{...} + 空白行
sed -i '/\\bibliographystyle{IEEEtran}/,/\\bibliography{references}/{ //!d; /\\bibliography{references}/d; }' article.tex
# 更安全的方案：明确指定上下文
```

```python
# 方法B: Python 精确操作
with open('article.tex') as f:
    content = f.read()

# 找到第一个 \bibliography{references} 前的上下文
# 它后面跟着 % ===== APPENDIX
first_bib = content.find('\\bibliographystyle{IEEEtran}\n\\bibliography{references}\n')
appendix = content.find('% ===== APPENDIX')
if first_bib > 0 and appendix > first_bib:
    # 确认这确实是第一组（在附录前）
    if appendix - first_bib < 200:
        # 删除第一组（\bibliographystyle + \bibliography + 后面的空行）
        end_first = content.find('\n\n', first_bib)
        content = content[:first_bib] + content[end_first:]
        
        # 验证
        assert '\\end{document}' in content
        assert content.count('\\bibliography{') == 1
        
        with open('article.tex', 'w') as f:
            f.write(content)
```

## 编译验证（关键！）

删除组后不能只跑一遍 pdflatex——必须先清除 .aux 和 .bbl 文件，否则残留的交叉引用会印出 old bibliography 内容：

```bash
cd paper-dir
rm -f article.aux article.bbl article.blg
pdflatex -interaction=nonstopmode article.tex
bibtex article
pdflatex -interaction=nonstopmode article.tex
pdflatex -interaction=nonstopmode article.tex

# 验证
grep -i 'undefined' article.log          # 0 undefined citations
grep -i 'error' article.log | head -3     # 0 errors
```

## 效果

| 指标 | 修复前（有重复） | 修复后 | 
|:-----|:---------------:|:------:|
| 编译页数 | 11 页（第2次打印中断） | 12 页（完整） |
| 文件大小 | ~347KB | ~370KB |
| 参考文献 | 列表中断在第7页 | 完整 32 条目 |
| undefined citations | 0 | 0 |

## 预防

在每次编译前自动检查：

```bash
if [ $(grep -c '\\\\bibliography{' article.tex) -ge 2 ]; then
    echo "⚠️ DUPLICATE BIBLIOGRAPHY DETECTED"
fi
```

将此检查加入 `post-compile-dual-quality-check` 的预检阶段。
