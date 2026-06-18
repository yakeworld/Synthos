# OA Frontiers Download Reference (2026-06-18)

## 已知成功的 Frontiers OA 论文

### Ling2020 Barany Society
- **标题**: Clinical Characteristics of Patients With Benign Paroxysmal Positional Vertigo and Recurrent Falls
- **DOI**: `10.3389/fneur.2020.00602`
- **来源**: Frontiers in Neurology (OA)
- **下载URL**: `https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2020.00602/pdf`
- **文件大小**: 663,417 bytes (663KB)
- **MD5**: `c42bfb3cdb3a9751f99dd7d8dea5bb50`
- **保存位置**: `pima-crispdm/06-references/Ling2020BaranySociety.pdf`
- **状态**: ✅ 真实全文，非占位PDF
- **注意**: MedData 中同为占位PDF（MD5=`fd469bd7...`），OA直连是唯一有效路径

## 判定逻辑

```
下载 Frontiers 论文
  ↓
MD5 = c42bfb3cdb3a9751f99dd7d8dea5bb50? → ✅ 真实PDF
MD5 = fd469bd7cd29446f2800f099e3b71457? → ❌ 占位PDF（不应出现在OA直连中）
```

**关键规则**: OA 直连不应返回占位PDF。如果返回占位指纹，说明URL构造有误或DOI不正确。

## 通用模式

所有 `10.3389/` 开头的 DOI 都属于 Frontiers，均应该能直接下载：

```bash
curl -s -L "https://www.frontiersin.org/journals/{journal}/articles/{DOI}/pdf" -o output.pdf
# 例如: 10.3389/fneur.2020.00602 → https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2020.00602/pdf
```

URL 构造：`https://www.frontiersin.org/journals/{journal_name}/articles/{DOI}/pdf`

`journal_name` 从 DOI 中提取：`10.3389/{journal}` → `fneur` → `neurology`
