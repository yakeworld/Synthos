# 轨道制双轨论文管线协议

> 2026-06-18 确立。Synthos论文管线结构性故障修复：101篇论文 0 篇有 status.json。

## 核心问题

- 管线只做"生产"不做"验证"——所有论文都没有质量门禁记录
- cron的autonomous-core-researcher产出"研究空白"，但这些不应进入论文管线
- 92篇无paper.tex的论文被"丢失"——没有完成/未完成/草稿的状态区分

## 双轨架构

### 轨道A：高质量论文管线

```
新建目录(有.tex) → 补status.json → paper-repair → quality-review → 修订循环 → G7通过
```

规则：
- 每篇论文必须有 `07-quality/status.json`
- 无status.json = 未完成，不计入"有效产出"
- paper-repair 和 quality-review 只处理有低分status.json的论文
- G7通过才算一条完整产出

### 轨道B：研究空白/假设 → 知识库

```
cron产出 (autonomous-core-researcher, literature-monitor) → AKNE图谱 + outputs/knowledge/
```

规则：
- 不生成.tex，不跑编译，不占论文目录配额
- 产出直接写入知识库
- 积累到一定量后，择优选一篇进入轨道A

## 状态机

```
空目录 → 轨道B(有内容无.tex) → 补全.tex → 轨道A(有.tex无status.json)
                                                    ↓
                                              paper-repair / quality-review
                                                    ↓
                                              有status.json(低分)
                                                    ↓
                                              修订循环 → status.json(高分)
                                                    ↓
                                              G7通过 → 完整产出 ✅
```

## 清理协议

| 操作 | 条件 | 去向 |
|:-----|:----:|:-----|
| 删除 | 内容<3个文件 | 直接删除 |
| 归档 | 无内容但有目录结构 | `_drafts_archive/` |
| 知识库 | 有内容但无.tex | `_knowledge_only/` |
| 论文管线 | 有.tex无status.json | 补入status.json后走轨道A |
| 完成 | 有.tex有status.json且通过G7 | 保留原位 |

## 实战数据（2026-06-18）

- 总目录: 149（101活跃 + 48归档 + 空壳删除3）
- 有paper.tex: 66篇
- 无paper.tex但有内容: 35篇（进入轨道B或归档）
- 空壳（直接删除）: 3篇
- 已归档: 48篇（空壳）

## Cron改造要点

1. `autonomous-core-researcher` → 输出改为知识库条目（轨道B）
2. `literature-monitor` → 输出改为知识库条目（轨道B）
3. `paper-repair` → 只处理有低分status.json的论文（轨道A）
4. `paper-quality-review` → 只处理有低分status.json的论文（轨道A）

## 状态定义

| 状态 | status.json | paper.tex | 说明 |
|:-----|:-----------|:----------|:-----|
| 空目录 | ❌ | ❌ | 直接删除或归档 |
| 草稿 | ❌ | ❌ | 有部分内容，进入轨道B |
| 进行中 | ❌ | ✅ | 有.tex但无质量门禁，走paper-repair |
| 修订中 | ✅(低分) | ✅ | 已有低分门禁，进入修订循环 |
| 完成 | ✅(高分) | ✅ | G7通过，完整产出 |