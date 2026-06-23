# ❌ 已废弃（2026-06-23）

本文档描述已被 `meddata-download` 技能和 `meddata-download-core-rules.md` 取代。

**请勿参考本文档**。核心规律已改写为：

```
① full_look(abstractId=随机11位号, pmid=真实PMID, doi=真实DOI)
② 等待10s → viewtext(fileName=abstractId) → PDF
```

详见：
- `meddata-download` 技能
- `references/meddata-download-core-rules.md`
- `tools/paper-manager/src/sources/meddata.py`
