# Skill System Refactoring Protocol

> 2026-05-31 实战提炼：143→121个技能的系统级清理

## 触发条件

- 技能数量膨胀到难以管理（>100）
- 用户反馈"技能太乱"、"需要统一哲学"
- 技能目录有大量无SKILL.md的空分类目录
- 不同Agent间技能位置需要统一（.hermes/ vs 独立仓库）

## 五步流程

### Step 1: 全量审计

```bash
# 遍历所有SKILL.md，收集元数据
find skills/ -name "SKILL.md" | while read f; do
  rel=$(echo $f | sed 's|/SKILL.md||')
  size=$(wc -c < "$f")
  has_refs=$(test -d "$(dirname $f)/references" && echo "📁refs" || echo "")
  echo "$rel | ${size}K | $has_refs"
done
```

需要审计的维度：

| 维度 | 检查方法 |
|:-----|:---------|
| 完整性 | 是否有SKILL.md + references/ |
| 重叠 | 同一主题是否有多个技能（如evolution + devops/evolution） |
| 碎片 | 技能<5KB且无refs → 候选吸收 |
| 哲学 | 是否有文言原理层 |
| 安全 | 是否含硬编码凭证 |
| 归属 | 属于Synthos核心还是通用Hermes技能 |

### Step 2: 分析问题

**重复检测**：同名技能在不同分类下同时存在（如 `evolution` + `devops/evolution`）
→ 保留主版本，删除冗余

**重叠检测**：不同名的技能覆盖同一领域（如 `bppv-expert` + `scc-bppv-kinematics`）
→ 若功能互补，保持分离+文档化边界
→ 若功能重叠，合并为一个（name原则：保留domain名更广的）

**碎片检测**：<3KB且无refs的技能（如 `nano-pdf`, `plan`, `codex`）
→ 吸收进父类别作为参考，不保留独立skill

### Step 3: 执行清理

```bash
# 合并
cp -r devops/evolution/* evolution/
rm -rf devops/evolution

# 吸收哲学框架到引用
cp -r research/research-platform-philosophy cognitive-atom-architecture/references/
rm -rf research/research-platform-philosophy

# 迁出非核心到通用目录
for sk in ascii-art ascii-video claude-design openhue; do
  mv skills/creative/$sk ~/.hermes/skills/creative/
done

# 添加文言原理
# 在SKILL.md的YAML frontmatter后插入
echo -e "\n## 原理层·文言\n\n> 四字格言，压缩40-60%的思路\n" >> skills/<name>/SKILL.md
```

### Step 4: 安全审计

```bash
# 扫描硬编码凭证
grep -rnP '(api_key|password|token|secret)\s*[=:]\s*["'"'"'][A-Za-z0-9_\-]{8,}["'"'"']' skills/ \
  | grep -vP '(os\.environ|\$\{|xxx|\*\*\*|placeholder|your_|example\.)' || echo "✅ 干净"
```

### Step 5: 验证 + commit

```bash
# 完整性检查
find skills/ -name "SKILL.md" | wc -l   # 记录总数变化

# 核心原子必须全部存在
for atom in knowledge-acquisition knowledge-extraction association-discovery \
  hypothesis-generation argument-expression viewpoint-verification; do
  test -f skills/$atom/SKILL.md && echo "✅ $atom" || echo "❌ $atom"
done

# git commit
git add skills/
git commit -m "arch: 技能系统重构—合并/吸收/迁出/文言化"
```

## 决策矩阵

| 情况 | 操作 |
|:-----|:-----|
| 完全重复（同名同内容） | 删冗余 |
| 功能重叠（不同名同主题） | 合并或文档化边界 |
| 函数级碎片（<3KB） | 吸收进父类别 |
| 非核心（与系统研究方向无关） | 迁出到通用技能目录 |
| 缺乏哲学层 | 注入文言原理 |
| 含硬编码凭证 | 替换为环境变量或[REDACTED] |

## 实战数据（2026-05-31）

| 指标 | 前 | 后 |
|:-----|:--:|:--:|
| Synthos技能数 | 143 | 121 |
| 迁出到通用 | — | 22 |
| 合并 | 0 | 1 (evolution) |
| 吸收 | 0 | 1 (research-platform-philosophy) |
| 涉及路径迁移 | 0 | 1 (scc-bppv-kinematics → Synthos) |
| 文言注入 | 0 | 6 |
| 安全修复 | 0 | 1 (密码脱敏) |
| 总耗时 | — | ~30分钟 |

## 与hermes-agent-skill-authoring的关系

本protocol是该skill的实战操作指南。SKILL.md定义**原则**（三语层级、层级分离、源一不二），本protocol定义**怎么做**（审计→分析→执行→验证）。
