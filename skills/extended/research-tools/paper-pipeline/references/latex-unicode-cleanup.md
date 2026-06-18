# LaTeX 中文字符/Unicode 字符检测与清理

## 问题

LaTeX（非 XeLaTeX）无法处理中文/Unicode字符。中文字符（如"从"、U+4ECE）或排版符号（如em-dash — U+2014、smart quotes ' U+2019）会触发编译错误。

## 快速检测

```bash
python3 -c "
import sys
with open('paper.tex', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    for ch in line:
        if ord(ch) > 127 and ch not in '{}[]()<>+-*/%=.,;:!?@#\$^&|~\"\\\' \\t\\n\\r':
            print(f'Line {i}, pos {line.find(ch)}: U+{ord(ch):04X} {ch}')
            break
"
```

## 常见违规字符

| 字符 | Unicode | 来源 | 修复 |
|:-----|:--------|:-----|:-----|
| 从 | U+4ECE | 中英文混排残留 | 删除 |
| — | U+2014 | 从Word/浏览器复制，em-dash | 替换为 `---` |
| ' | U+2019 | smart/curly quote | 替换为 `'` |
| " | U+201C/U+201D | smart double quotes | 替换为 `"` |
| · | U+00B7 | 中圆点（常见于公式） | `\cdot` |
| 篇 | U+7BC7 | 文件名混入中文 | 删除 |

## 预防

- 不要在终端粘贴编辑LaTeX文件时引入中文注释
- 不要在文件名中使用中文，包括图片文件名
- 编译前运行上述Python检测脚本
- 模板文件中的中文注释也应全部删除或改为英文
