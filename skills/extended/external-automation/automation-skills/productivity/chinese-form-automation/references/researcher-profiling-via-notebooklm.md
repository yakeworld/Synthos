# 基于NotebookLM的研究者面貌分析与补充工作流

> 来源：2026-05-30 实战（杨晓凯研究者面貌分析）
> 用途：从公开/本地数据提取研究者完整画像 → NotebookLM审计 → 补全修正

---

## 工作流总览

```
Step 1: 数据采集（网站/本地/会话）
    ↓
Step 2: 生成 V1 研究者面貌文档
    ↓
Step 3: 上传到 NotebookLM 新笔记本
    ↓
Step 4: 逐问法分析（完整性/准确性/亮点/格式/缺失）
    ↓
Step 5: 针对性追问（N轮，每轮一个维度）
    ↓
Step 6: 根据分析结果 patch/major edit 面貌文档
```

---

## Step 1: 数据采集

### 来源优先级

| 来源 | 提取方法 | 能获取的信息 |
|:-----|:---------|:------------|
| 用户个人/团队网站 | `curl` + 去标签文本提取 | 职务/论文/专利/项目/产品/学术兼职 |
| WordPress REST API | `curl /wp-json/wp/v2/pages` | 页面列表、ID、链接 |
| `article_todo/` | `ls ~/桌面/article_todo/` | 人工撰写论文目录 |
| Synthos论文目录 | `ls /media/.../outputs/papers/` | 质量门通过论文 |
| 本地投稿文件包 | `find "投稿*"` | 投稿状态、Cover Letter、目标期刊 |
| 用户 profile/memory | `memory` / `fact_store` | 背景/职务/偏好 |
| 全院信息表 | `*全院信息*.xls` | 出生/电话/学历/毕业学校 |
| 各版本.tex文件 | `grep "journal{" *.tex` | 目标期刊名 |

### 网站提取命令模板

```bash
# 获取网站内容（WordPress典型结构）
curl -sL --connect-timeout 10 --max-time 30 "https://xxx.top/about-page/" | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '\n', text)
text = re.sub(r'\n\s*\n', '\n', text)
text = re.sub(r'&nbsp;', ' ', text)
text = re.sub(r'&amp;', '&', text)
text = re.sub(r'&#8211;', '-', text)
lines = [l.strip() for l in text.split('\n') if l.strip()]
for l in lines:
    print(l)
"

# 提取专利号（ZL/CN开头）
curl -s "https://xxx.top/patents-page/" | grep -oP 'ZL\d{13}\.\d|CN\d{12}\.\d|ZL\d{12}|CN\d{12}'

# 提取DOI
curl -s "https://xxx.top/papers-page/" | grep -oP '10\.\d{4,}/[^\s"<>]+'
```

---

## Step 2: 生成 V1 研究者面貌文档

结构化文档应包含以下板块：

| 板块 | 内容 | 数据来源 |
|:-----|:-----|:---------|
| 身份与职务 | 职称/导师资格/特殊人才/行政职务 | 网站+user profile |
| 学术兼职 | 学会/协会/期刊审稿 | 网站 |
| 教育经历 | 时间段+学校+专业 | 网站+用户提供 |
| 科研项目 | 时间/名称/来源/基金号/角色 | 网站+profile |
| 已发表论文 | 时间/标题/期刊/角色(第一/通讯) | 网站+本地目录 |
| 专利成果 | 名称/授权号/类型/授权日/发明人排序 | 网站（关键字段：ZL/CN/发明/实用新型） |
| 产品转化 | 产品名/开发阶段/定价 | 网站 |
| 继续教育 | 项目名称/级别/角色 | 网站 |
| 平台资源 | 实验室/中心/病区床位 | 网站+profile |
| 研究聚焦领域 | 按主次排列（含支撑数据） | 综合推断 |
| 待补充信息 | 缺失但重要的维度 | NotebookLM分析建议 |

---

## Step 3: 上传到 NotebookLM

```bash
# 创建新笔记本
notebooklm create "研究者姓名 + 研究者面貌分析"

# 上传文档（注意剥离YAML frontmatter）
awk 'BEGIN{n=0} /^---$/{n++;next} n==1{next} n>=2{print}' 研究者面貌.md > /tmp/clean.txt
notebooklm source add "$(cat /tmp/clean.txt)" --type text --title "研究者面貌_姓名" --timeout 120
```

---

## Step 4-5: 逐问法分析

### 第一轮：全维度扫描

```bash
notebooklm clear && notebooklm use <nb_id>
notebooklm ask "请全面分析这份研究者面貌文档，从以下维度逐一评审：
1. 完整性：缺少什么关键信息？哪些板块有待补充？
2. 准确性：是否有逻辑矛盾或数据不匹配？
3. 亮点提取：哪些信息最能体现研究者的学术影响力？
4. 格式优化：结构和表达有什么改进空间？
5. 潜在缺失：作为一个完整的研究者profile，可能还缺少什么重要的数据维度？
请逐条列出发现，不要遗漏。"
```

### 第二轮：针对性追问

基于第一轮分析中的发现，追问具体维度：

```bash
# 例：追问论文数量矛盾
notebooklm ask "文档中标题写着'20+篇'但正文列出了37篇，建议的准确描述是什么？"

# 例：追问研究领域缺失
notebooklm ask "请根据已有数据和项目信息补全'研究聚焦领域'板块，按主次排列"

# 例：追问H-index和引用量估算
notebooklm ask "请根据论文期刊级别和年份分布，估算H-index和总引用量区间"

# 例：追问专利分类错误
notebooklm ask "文档中专利分类是否有错误？同一专利是否出现在多个分类中？"

# 例：追问项目重复
notebooklm ask "科研项目列表是否有教改项目混入？是否有重复计数？"
```

### 常见分析发现类型

| 发现类型 | 典型问题 | 修复方式 |
|:---------|:---------|:---------|
| 论文数量矛盾 | 标题数与正文数不一致 | 统一为准确表述 |
| 板块缺失 | 研究聚焦/奖项/荣誉空白 | 根据已有数据补全 |
| 数据过时 | 临床数据无年份 | 补充统计年份或标注估算 |
| 分类错误 | 专利第一发明人归类到非第一 | 重新分类 |
| 重复统计 | 教改项目混入科研项目 | 拆分到独立板块 |
| 估算不严谨 | H-index等无数据支撑 | 标记为"需独立查询" |

---

## Step 6: 更新研究者面貌文档

```python
# 典型patch操作
# 在技能层面使用 patch 直接修正
# 也可手动编辑 .md 文件后保存
```

### 常用修正操作

| 操作 | 命令 |
|:-----|:-----|
| 修复论文总数标题 | `patch --old "20+篇" --new "40+篇（含非第一/通讯作者）"` |
| 补全空板块 | 用 notebooklm 的回答内容填充 |
| 修复专利分类 | 移动行到正确分类下 |
| 标记估算数据 | 加注"(估算)"或"(需独立核实)" |
| 新增板块 | 追加到文档末尾 |

---

## 已知陷阱

| 陷阱 | 表现 | 解决 |
|:-----|:-----|:-----|
| 网站数据与本地文件不一致 | 网站列出更多论文/专利 | **以网站为准**（通常是更新后的公开版本） |
| NotebookLM 评分偏高 | 分析中可能高估学术影响力 | 参考而非盲从，交叉验证引用量等指标 |
| 专利"双报"（发明+实用新型） | 同一专利名出现在两个分类 | 合并说明，标注"双报策略" |
| 教改项目混入科研项目 | 项目总数虚高 | 分设科研/教改两个板块 |
| 通讯作者标记不一 | 中英文标注混用 | 统一标准（如"通讯"或"*"） |
