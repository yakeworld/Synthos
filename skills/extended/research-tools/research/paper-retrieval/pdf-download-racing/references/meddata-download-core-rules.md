# MedData 下载核心规律（2026-06-23 最终确认）

> 本文档取代以下旧文件中的所有相关描述：
> - `meddata-pmid-construction-2026-06-23.md`（已过时）
> - `meddata-internal-id-format.md`（已过时）
> - `meddata-fulllook-patterns-2026-06-19.md`（已过时）
> - `meddata-access-absorbed.md`（已过时）
> - `meddata-api-details.md`（已过时）
> - `meddata-browser-vs-cli.md`（已过时）
> - `2026-06-23-exitnode-test.md`（已过时）
> - 技能中所有关于 MedData 的描述

## 核心流程（两步，不可省略）

```
① full_look(abstractId=随机11位号, pmid=真实PMID, doi=真实DOI)
   → 系统将全文复制到 abstractId 名下
② 等待 10 秒（系统准备全文）
③ viewtext(fileName=abstractId)
   → 取回全文PDF
```

## 参数规则

| 参数 | 值 | 说明 |
|:-----|:----|:------|
| **abstractId** | 11位随机整数 | **必须唯一**，每次请求生成新号。不能用固定值`1`、不能用DOI_NO_SLASH。防与其他请求混淆 |
| **pmid** | 论文**真实PMID** | 告诉系统要哪篇论文。不可用固定`'1'` |
| **doi** | 论文**真实DOI** | 辅助定位 |

## 前置快速尝试（不保证成功）

在核心流程之前，可快速尝试两种直接 viewtext：

1. **PMID 直接作为 fileName** — MedData 索引中有PMID映射时可用
2. **DOI_NO_SLASH 直接作为 fileName** — 部分出版社有效（Frontiers, BMJ 等）

## 占位 PDF 识别

- MD5: `fd469bd7cd29446f2800f099e3b71457`
- 大小: 606841 bytes
- 标题: 1975年甲醇中毒论文（与请求的论文完全无关）
- 返回占位 = 论文不在 MedData 全文库中，**不是IP限制**

## 频次限制

- 单 token 连续多请求后 MedData 返回空响应
- 需要间隔数秒再试（等待冷却）
- 每次获取新 token 可以减少频率问题

## 错误记录（已废弃，勿参考）

以下文件中的 MedData 描述已废弃，不使用：
- `meddata-access-absorbed.md` — 旧版内部ID格式、modifyPass描述
- `2026-06-23-exitnode-test.md` — 错误地将占位归因于IP限制
- `meddata-browser-vs-cli.md` — 旧版CLI/浏览器差异
- 其他旧参考文件
