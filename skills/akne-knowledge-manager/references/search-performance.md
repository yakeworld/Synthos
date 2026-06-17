# AKNE 搜索功能测试报告

**日期**: 2026-06-18
**脚本**: `/home/yakeworld/.hermes/scripts/akne-enhanced-search.py`

## 测试查询结果

| 查询 | Entity解析 | Graph邻居 | Text结果 | 评估 |
|------|-----------|-----------|----------|------|
| `前庭性偏头痛` | NONE | 0 | 5条 | 相关度好 — BPPV讨论会、前庭功能检测、眩晕中心 |
| `vestibular migraine` | `vestibular-adaptation-PINN`(0.6) | 20 | 5条 | Graph邻居过泛（全指向sources/编程），Text更精准 |
| `眼动追踪` | 精确匹配(0.2) | 0 | 5条 | 精准命中眼动仪器、VR眼震、生物标志物文档 |
| `BPPV 半规管` | `bppv`(1.0) | 5 | 5条 | BPPV诊疗规范、Dix-Hallpike、后半规管结石症 |
| `Synthos 技能` | `synthos`(1.0) | 20 | 5条 | 命中synthos/skills-index.md，Graph邻居过泛 |
| 虚构`xyz` | NONE | 0 | 3条 | 相关度低但合理，未产生错误匹配 |

## 性能基准

- 单次 full-mode 搜索：约 **22 秒**
- 原因：TF-IDF 索引每次重建（读取 1118 个源文件，构建 40615 词汇表）
- 建议：增量索引更新或预构建缓存

## Bug 修复

**2026-06-18**: `fuzzy_node_search` 在 `best=None` 时返回 `(None, 0.0)` 嵌套 tuple，
导致 `confidence:.3f` 格式化崩溃。

修复前：
```python
return best, min(0.8, best_score / 5.0) if best else (None, 0.0)
```

修复后：
```python
return (best, min(0.8, best_score / 5.0)) if best else (None, 0.0)
```

## 向量嵌入状态

| 类型 | 总数 | 已嵌入 | 覆盖率 |
|------|------|--------|--------|
| 源文件 | 1167 | 1134 | 97.2% |
| 论文 | 171 | 134 | 78.4% |
| 技能 | 63 | 63 | 100% |
| 实体 | 126 | 126 | 100% |
| 分类 | 23 | 23 | 100% |
| **合计** | **1550** | **1480** | **95.5%** |

- 模型：`all-MiniLM-L6-v2`（本地缓存，384 维）
- 数据库：`/media/yakeworld/sda2/academic_writer/yakeworld/.knowledge/vectors.db`
- 脚本：`/home/yakeworld/.hermes/scripts/akne-vectorize.py`

## 局限性

1. **Graph 邻居过泛**：多数节点连接在 `sources/科研` 或 `sources/编程` 大类下
2. **实体解析依赖节点名**：中文节点名包含大量中文词汇时解析效果尚可，但英文混合节点名（如 `vestibular-adaptation-PINN`）解析不够精准
3. **TF-IDF 索引不完整**：37 篇论文因缺失文件或空 state.json 未嵌入
4. **无向量相似度搜索**：`vectors.db` 已生成但未集成到搜索流程
