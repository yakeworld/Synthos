# SCC论文引用上下文验证案例（2026-05-30）

> 论文: A 3D Logarithmic Spiral Model for Human SCC Centerline Morphology
> 引用总数: 34篇 | PDF覆盖率: 100%

## 验证流程

### 1. 数值声明提取

从论文正文提取所有`\cite{}`附近的数值/定量声明，分类：

| 声明类型 | 示例 | 验证方法 |
|:---------|:-----|:---------|
| 自有实验值 | RMSE 0.07-0.17mm | 代码输出文件 |
| 文献对比值1 | Bradshaw2010 RMSE=0.08mm | PDF全文搜索"0.08" |
| 文献对比值2 | Ifediba2007 drag 1.4x | PDF全文搜索"1.4" |
| 文献对比值3 | Santina2005 44 labyrinths | PDF全文搜索"44" |
| 文献对比值4 | Manoussaki2008 b=0.02-0.08 | PDF全文搜索"0.02" |

### 2. PDF全文搜索

对声明的关键数值/术语，用pdftotext全文搜索：

```bash
# 验证 Bradshaw2010 的 RMSE=0.08mm 声明
pdftotext Bradshaw2010.pdf - | grep -i "0.08\|RMSE\|subpixel"
# 结果: "root mean squared difference of 0.08 mm" -> PASS

# 验证 Ifediba2007 的 drag 1.4x
pdftotext Ifediba2007.pdf - | grep -i "1.4\|drag\|elliptical"
# 结果: "viscous drag by approximately 1.4" -> PASS

# 验证 Manoussaki2008 的 b=0.02-0.08
pdftotext Manoussaki2008.pdf - | grep -i "0.02\|0.08\|spiral rate\|growth rate"
# 结果: NOT FOUND -> 该论文讨论耳蜗曲率增益，不报告螺旋生长率参数b
```

### 3. 修正

当数值不可追溯时：
- 降级措辞：删除具体数值，改为泛化引用
- 替换引用：从其他已有PDF中找替代
- 标注推算：如果数值是由本实验从文献数据推算，标注"estimated"

### 发现问题的引用

| Ref | 论文中的声明 | PDF验证 | 修正 |
|:----|:------------|:--------|:-----|
| Manoussaki2008 | "b≈0.02-0.08 based on Manoussaki2008" | 未找到该数值 | 改为泛化措辞，引用Manoussaki2008+Manoussaki2006 |

## 工具脚本

```python
# 批量搜索所有PDF中的关键数值
import subprocess, os
pdf_dir = '06-references/pdfs/'
for f in sorted(os.listdir(pdf_dir)):
    if not f.endswith('.pdf'): continue
    text = subprocess.run(['pdftotext', os.path.join(pdf_dir, f), '-'], 
                         capture_output=True, text=True, timeout=30).stdout
    if '0.08' in text:
        print(f'{f}: contains 0.08')
```
