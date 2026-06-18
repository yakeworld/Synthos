# 本地资产审计工作流

> 用于 P-1.0 阶段的标准化审计流程。2026-05-22 由用户纠正确立。

## 核心原则

**先本地后外搜**：互联网搜索之前，必须先盘点本地已有资产。本地资产包括：
- 项目内部的吸收记录（absorption-*.md）
- 已有论文（.tex + .bib + .pdf）
- 进化日志中的吸收记录（evolution-log.md）
- 每个子技能的 references/ 目录
- 已有的文献综述文档（*literature*.md）

## 标准审计脚本

```bash
# 设置项目根目录
PROJ="/media/yakeworld/sda2/Synthos"

# 1. 吸收记录（最优先）
echo "=== 吸收记录 ==="
find "$PROJ" -name "*absorb*" -o -name "*absorption*" 2>/dev/null | grep -v ".git"

# 2. 已有论文
echo "=== 已有论文 LaTeX ==="
find "$PROJ" -name "*.tex" -not -path "*/.git/*" | head -20
echo "=== 参考文献库 ==="
find "$PROJ" -name "*.bib" -not -path "*/.git/*"
echo "=== 文献综述文档 ==="
find "$PROJ" -name "*literature*" -type f 2>/dev/null | head -10

# 3. 进化日志吸收记录
echo "=== 进化日志 - 吸收记录 ==="
grep "吸收" "$PROJ/evolution-log.md" 2>/dev/null | tail -20

# 4. 技能references
echo "=== 各子技能references ==="
find "$PROJ/skills" -type d -name "references" -exec sh -c 'echo "$1:"; ls "$1"' _ {} \; 2>/dev/null
```

## 审计输出结构

审计结束后，构建以下领域地图骨架：

```
## 本地已知的工作（无需外搜）
| # | 系统/工作 | 来源 | 核心特征 | 已知局限 |
|:-:|:---------|:-----|:---------|:---------|
| 1 | xxx | 吸收记录/论文 | ... | ... |
| 2 | yyy | ... | ... | ... |

## 需要外搜补充的缺失系统
- 缺失系统A（关键词）
- 缺失系统B（关键词）
```
