# NotebookLM 全面审计工作流

> 适用于：定期审计所有笔记本、竞赛前材料检查、跨项目知识管理

## 触发条件
- 用户说"审计我的NotebookLM"或"管理NotebookLM"
- 需要知道笔记本总数、分类、来源质量
- 竞赛前检查材料完整性

## 审计步骤

### 1. 获取完整列表
```bash
notebooklm list --json     # 获取全部笔记本的JSON（含ID/标题/创建时间/是否所有者）
```

### 2. 主题分类（按关键词自动归类）
```python
categories = {
    "ADHD/眼动追踪": ["ADHD", "眼动", "eye tracking"],
    "前庭/VOR/BPPV": ["VOR", "前庭", "BPPV", "眩晕", "耳石", "vestibular"],
    "眼科/虹膜/3D眼球": ["眼", "虹膜", "iris", "瞳孔", "pupil", "眼球", "eyeball", "ocul"],
    "AI/ML/编程": ["AI", "ML", "机器学习", "深度", "神经网", "智能体", "agent"],
    "NSFC/基金/项目申报": ["NSFC", "国自然", "基金", "标书", "申报"],
    "教学/课程": ["教学", "课程", "教案", "培养"],
    "科研方法论/论文写作": ["CRISP", "TRIPOD", "论文写作"],
    "医院管理/报告": ["医院", "报告", "绩效"],
    "专利/知识产权": ["专利", "知识产权"],
}
# 未匹配的归入"其他"（通常占20-35%）
```

### 3. 关键笔记本来源计数
```bash
# 对每个关键笔记本：
notebooklm use <ID_prefix>
notebooklm source list   # 看来源数量和质量
```

### 4. 质量评估（每笔记本）
| 维度 | 检查点 |
|:-----|:-------|
| 来源数量 | 总量 + PDF/MD比例 |
| 年代跨度 | 最早/最新来源 |
| 类型分布 | PDF/MD/Pasted Text/Web Page |
| 时效性 | 是否有2025年以前未更新的来源 |
| 异常命名 | 无意义文件名（如 201806596.pdf） |

### 5. 跨笔记本关联图谱
识别不同类别笔记本之间的连接点（如 ADHD × VOR × 3D眼动），标记：
- ✅ 已有人工连接（共享来源/交叉引用）
- ⚠️ 知识空白（有交叉可能但无连接）

### 6. 输出报告格式
```markdown
# NotebookLM 审计报告

## 总体概况
- 总数: 71
- 所有者: 47 / 共享: 24
- 时间跨度: ~8.5个月

## 主题分类（条形图）
ADHD/眼动追踪    ████████░░░░░░░░  7

## 关键笔记本质量
| 笔记本 | 来源数 | 质量评分 | 问题 |
|:-------|:-------|:---------|:-----|

## 跨笔记本关联图谱
```
                    ┌──────────────┐
                    │  ADHD项目     │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐  ┌────────┐  ┌────────┐
        │ VOR/BPPV │  │ 3D眼   │  │ AI/ML  │
        └──────────┘  └────────┘  └────────┘
```
```

### 7. 行动建议优先级
| 优先级 | 内容 |
|:-------|:-----|
| P0 | 核心笔记本来源不足（Synthos/NSFC仅1源） |
| P1 | 不规范命名、重复笔记本 |
| P2 | 分类"其他"笔记本、旧笔记本时效性 |

## 关键命令速查

```bash
notebooklm list --json                                               # JSON格式列表
notebooklm metadata                                                  # 当前笔记本元数据
notebooklm use <ID_prefix>                                           # 切换笔记本
notebooklm source list                                               # 来源列表
notebooklm source list 2>&1 | grep -c '│'                           # 来源数量
notebooklm summary                                                   # AI摘要
notebooklm source rename "<UUID_12chars>" "新名称"                   # 重命名（用UUID前缀）
echo "y" | notebooklm source rename "<UUID_12chars>" "新名称"       # 非交互式重命名
notebooklm source add /path/to/file                                  # 添加来源
```

## 陷阱
- `notebooklm source list` 在120+来源笔记本上会超时（30s+），先用 `| head -30` 限制输出
- `notebooklm metadata` 只显示当前笔记本，不是全部
- 中文来源rename需要使用UUID前缀（12字符），不能直接用中文标题匹配
- 来源计数用 `grep -c '│'` 不可靠，因为表格边框也含 `│`。更准确：`notebooklm source list 2>&1 | grep -E '^│ [a-f0-9]' | wc -l`
- 来源添加后需要几秒processing状态才能变为ready
