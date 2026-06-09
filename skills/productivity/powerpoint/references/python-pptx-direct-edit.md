# python-pptx 直接编辑陷阱与修复

## 核心问题（2026-06-09 确认）

python-pptx 维护 **两套 sldIdLst 引用**，修改任何一套都不影响最终保存：

| 引用 | 类型 | 影响保存 |
|------|------|---------|
| `prs.slides._sldIdLst` | lxml Element | ❌ 否 |
| `prs.part._element` | CT_Presentation（非lxml） | ✅ 是 |
| `prs.slides._sldIdLst.sldId_lst` | property (list) | ❌ 否 |

### 验证

```python
from pptx import Presentation
prs = Presentation(src)

# prs.slides._sldIdLst 是 lxml Element
# prs.part._element 是 CT_Presentation（非标准lxml）
# 两者的parent关系：prs.slides._sldIdLst.getparent() is prs.part._element
# 但修改 children 不影响保存结果
```

## 可靠方案：zip直接修改XML

PPTX本质是ZIP压缩包。`ppt/presentation.xml` 包含sldIdLst。用zip读写即可。

### 关键细节

1. **sldIdLst tag 是 `sldIdLst` 不是 `slideIdLst`**
2. **新页面索引**：`add_slide()` 追加到最后，新页面索引 = 原页数 和 原页数+1
3. **CT_Presentation 的 `__iter__`**：不是标准lxml Element，迭代行为可能不稳定
4. **sldId_lst 是 property**：无setter，`del lst[:]` + `extend()` 不生效

### 参考脚本：`scripts/reorder_pptx.py`

见 `scripts/reorder_pptx.py` 获取完整可执行脚本。

## 相关命令速查

```python
# 查找sldIdLst
for child in list(prs.part._element):
    if 'sldIdLst' in child.tag:  # 注意：不是 'slideIdLst'
        sldIdLst = child
        break

# 提取所有sldId（zip方案前验证用）
import re
pres_xml = zin.read('ppt/presentation.xml')
all_sldIds = re.findall(r'<p:sldId id="(\d+)" r:id="(rId\d+)"/>', pres_xml)
```
