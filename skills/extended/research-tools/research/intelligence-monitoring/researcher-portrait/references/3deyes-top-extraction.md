# 3deyes.top 数据提取案例

> 2026-05-30 实战：从眩晕病实验室官网提取杨晓凯完整信息

## 页面结构

WordPress 站点，页面通过 REST API 和 curl 直接提取。

## 关键命令

### 获取页面列表
```bash
curl -s "https://www.3deyes.top/wp-json/wp/v2/pages?per_page=50" | python3 -m json.tool
```

### 提取"关于我们"页面内容和"成果转化"页面内容
```bash
curl -sL --connect-timeout 10 --max-time 30 "https://www.3deyes.top/关于我们页面/" 2>/dev/null
```

### HTML表格提取（专利/论文表）

**错误做法（漏了2/3的数据）**：
```python
# 只匹配ZL/CN号 → 28行中只抓到9行
for m in re.finditer(r'(ZL\d{13,}|CN\d{12,}\.\d)', html):
    ...
```

**正确做法（捕获全部）**：
```python
section = re.search(r'专利成果.*?软件著作权', html, re.DOTALL)
if section:
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', section.group(), re.DOTALL)
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        texts = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
```

## 提取成果

| 数据类别 | 数量 | 关键字段 |
|:---------|:----:|:---------|
| 发明专利（已授权） | 6项 | 名称/ZL号/授权日/排序 |
| 发明专利（实审中） | 10项 | 名称/CN号/排序 |
| 实用新型 | 10项 | 名称/ZL号/授权日 |
| 软件著作权 | 2项 | 名称/登记号 |
| SCI论文（第一/通讯） | 22篇 | 标题/期刊/年份 |
| 中文核心论文 | 14篇 | 标题/期刊 |
| 科研项目 | 14项 | 名称/基金号/时间/角色 |
| 量产产品 | 2款 | 名称/定价/购买渠道 |

## 相关文件

- 完整profile: `研究者面貌_杨晓凯.md`（11章）
- 原始提取数据: `3deyes_top_原始数据.md`
- 专利/产品摘要: `专利与产品摘要.md`
