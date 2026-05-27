# Synthos 核心规则 — OpenCode 自动加载

> 本文件被 OpenCode 在 Synthos 项目目录中启动时自动读取。
> 所有代码/脚本/文档产出必须遵循以下标准。

## 1️⃣ 技能发现路径

所有 Synthos 技能在 `skills/` 目录下：
- `skills/quality/` — 质量门相关
- `skills/research/` — 研究管线
- `skills/evolution/` — 自进化引擎
- `skills/task-router/` — 任务路由
- 其他：argument-expression, hypothesis-generation, figure-generation 等

执行学术任务前先 `ls skills/research/ skills/quality/` 查看可用技能。

## 2️⃣ 论文命名规范（强制）

```
格式: {论文目录名}-v{版本号}.pdf
示例: pd-dysphagia-2026-v1.pdf
禁止: paper.pdf
```

## 3️⃣ D1-D10 十维质量门

| 维度 | 标准 | 检查方式 |
|------|------|----------|
| D1-D7 | Gemini 评审 ≥0.85 | `notebooklm ask` |
| D8 | 参考文献 ≥30 篇 | .bib + .tex 计数 |
| D9 | 全文覆盖率 ≥0.80 | 已下载PDF / .bib中DOI数 |
| D10 | 引用质量 | .tex \cite vs .bib 条目匹配 |
| **Final** | avg(D1-D10) | ≥0.85=T1, ≥0.80=T2, ≥0.75=T3 |

详细标准：`skills/quality/dual-quality-check-v2/SKILL.md`

## 4️⃣ PDF 下载验证

所有下载的 PDF 必须通过三级验证：
1. Content-Type 不是 text/html
2. 文件头 %PDF-（前5字节）
3. 文件尾 %%EOF（倒数100字节内）
4. 文件大小 ≥1000 字节

工具：`tools/paper-manager/download_one.py`

## 5️⃣ 参考文献管线

流程：NotebookLM筛选 → 生成BibTeX → 本地增强(SS元数据) → PDF全文获取 → 回传NotebookLM

下载源优先级：
1. OpenAccess / arXiv（最快）
2. Sci-Hub（curl_cffi TLS指纹绕过）
3. LibGen（5镜像轮换）
4. MedData（中国医学数据, 需 MEDDATA_USERNAME+PASSWORD）

详见：`skills/research/paper-reference-pipeline/SKILL.md`
     `skills/research/pdf-download-racing/SKILL.md`

## 6️⃣ 凭据管理

禁止硬编码。从环境变量读取：
```
SEMANTIC_SCHOLAR_API_KEY  — SS API密钥
MEDDATA_USERNAME          — 医学数据平台账号
MEDDATA_PASSWORD          — 医学数据平台密码
```

## 7️⃣ 进化日志

每次质量检查结果写入 `outputs/papers/qc-evolution.json`

## 8️⃣ Synthos 哲学

```
动灵在内，不假外求    — 主动发现，不等人说
宪临万法，一维一修    — 标准先行，逐一修复
先立后动，凡数必源    — 建标准再行动，每个数字可追溯
凡作必省，去形留神    — 每次行动后反思，重实质轻形式
熵减生生，格物通理    — 每次操作减少混乱
闲则整之，不待问      — 空闲时主动清理优化
```
