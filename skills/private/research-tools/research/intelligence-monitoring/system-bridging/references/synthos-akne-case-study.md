# Synthos-AKNE 桥接案例研究

> 会话日期: 2026-06-07
> 涉及系统: Synthos论文管线 + AKNE知识图谱
> 桥接类型: 双向注入 + 反向查询

## 系统概况

### Synthos (`/media/yakeworld/sda2/Synthos/`)
- 101 篇论文 (outputs/papers/)
- 33 个技能分类 (skills/)，110 个 SKILL.md
- 66 轮进化记录，质量评分 0.99 EXCELLENT
- 126 个节点图谱 (原有 AKNE)

### AKNE (`/media/yakeworld/sda2/academic_writer/yakeworld/`)
- 1,144 篇知识源 (.knowledge/sources/)
- 249 节点图谱 (graph.json)，389 边
- 220K 向量数据库
- 33 Wiki 页面

## 桥接过程

### 1. 摸清结构
```bash
# 统计两个系统的规模
ls -la Synthos/ && find Synthos/skills -name "SKILL.md" | wc -l
ls -la AKNE/ && du -sh AKNE/.knowledge/ && find AKNE/sources -name "*.md" | wc -l
cat AKNE/.knowledge/graph.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'nodes:{len(d[\"nodes\"])}, edges:{len(d[\"edges\"])}')"
```

### 2. 识别重叠领域
```python
DOMAIN_KEYWORDS = {
    "BPPV": ["bppv", "前庭", "耳石", "复位", "眩晕", "dix-hallpike", "epley"],
    "眼动追踪": ["eye", "eyetrack", "kappa", "saccade", "pupil", "iris", "vor"],
    "前庭生理": ["vestibular", "canal", "semicircular", "半规管", "cupula"],
    "ODE/PINN": ["ode", "pinn", "neuralode", "微分"],
    "临床诊断": ["clinical", "diagnos", "screen", "trust", "校准"],
    "深度学习/医学影像": ["segment", "yolo", "unet", "虹膜"],
}
```

### 3. 注入结果
- **98 篇论文** 作为 `synthos_paper` 节点
- **25 个技能分类** 作为 `synthos_skill` 节点
- **252 条边** 连接 Synthos → AKNE 实体
- **126 个 AKNE 实体** 全部被至少一篇论文链接
- **BPPV 域**最密集：37个节点，180条边

### 4. 领域重叠
| 领域 | Synthos论文 | AKNE实体 |
|------|------------|----------|
| BPPV | 15 | 54 |
| 眼动追踪 | 33 | 33 |
| ODE/PINN | 33 | 33 |
| 前庭生理 | 9 | 29 |
| 临床诊断 | 12 | 13 |
| 深度学习/医学影像 | 9 | 9 |

## 关键决策

1. **单向注入**: 只从 Synthos → AKNE，不反向写入（避免循环）
2. **增量安全**: 同名节点不重复创建，边不删除
3. **类型区分**: 注入节点使用 `synthos_paper` / `synthos_skill` 类型，与原有 `entity` / `wiki` / `source` 类型区分
4. **权重阈值**: 最低 0.3 权重，避免盲连
5. **环境变量**: 使用 `SYNTHOS_ROOT` / `AKNE_ROOT` 而非硬编码路径
6. **幂等同步**: 多次运行产生相同结果

## AKNE图谱原有结构

```json
{
  "nodes": [
    {"name": "CATALOG", "type": "entity"},
    {"name": "MOC", "type": "entity"},
    {"name": "concepts/前庭解剖", "type": "entity"},
    {"name": "wiki/entities/bppv", "type": "wiki"},
    {"name": "sources/BPPV/BPPV诊疗规范", "type": "source"},
    ...
  ],
  "edges": [
    {"source": "CATALOG", "target": "concepts/前庭解剖", "relation": "references", "weight": 1.0},
    {"source": "dix-hallpike", "target": "wiki/entities/bppv", "relation": "references", "weight": 1.0},
    ...
  ]
}
```

桥接注入后的新节点类型：
- `synthos_paper` (98个) — 论文目录 → 节点
- `synthos_skill` (25个) — 技能分类 → 节点
- 原有: `entity` (126), `wiki` (已有节点), `source` (已有节点)

新边类型: `bare` (252条，Synthos论文→AKNE实体) + 原有 `references` (137条)

## 常见问题

1. **AKNE graph.json 的 edge 结构不一致**: 有的边用 `relation` 字段，有的没有类型字段。桥接脚本统一使用 `weight` 字段。
2. **AKNE 节点名格式多样**: 有的带 `wiki/` 前缀，有的带 `sources/` 前缀，有的纯名。桥接脚本统一用 `node["name"]` 匹配。
3. **同名但类型不同**: `bppv` (entity) vs `bppv` (synthos_paper) vs `bppv.md` (wiki)。类型前缀区分。
4. **BPPV wiki 文件被占位行污染**: `[创新点, 核心技术, 知识点]::` 重复出现。桥接脚本不读取源文件内容，只读目录名。
5. **edge 数量控制**: 每篇论文连所有126个AKNE实体 → 252条边合理（98×2.6平均）。非全部连全部。

## 后续扩展

- [ ] 将 Synthos 论文摘要注入向量数据库
- [ ] 论文引用关系与 AKNE 源文件双向链接
- [ ] 进化周期触发时自动同步（evolution-state.json 变化检测）
- [ ] AKNE 查询结果直接嵌入论文写作流程
- [ ] 自动检测未分类的 AKNE 源文件，建议关联到 Synthos 论文
