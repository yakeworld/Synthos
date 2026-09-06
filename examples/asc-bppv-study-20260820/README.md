# 完整案例: ASC-BPPV 文献研究 (2026-08-20)

> 这是 Synthos 第一个公开、可追溯的端到端科研工作流案例。
> **它同时展示系统的成功和失败** — ACQ 降级、PDF 获取失败、质量门 G3 未通过,
> 全部按原样保留, 未做修饰。选它而非成功案例, 是有意为之: 复现的价值在于
> 第三方能看到真实边界, 而不是只能看到成功路径。

## 输入

- **研究问题** (pipeline_trace.json → query):
  「上半规管 (ASC) 诊断和治疗方法研究, Synthos 全流程验证」
- **执行模式**: research_twoloop (完整 7 原子链)
- **执行日期**: 2026-08-20 (文件 mtime: ACQ 11:20 → 稿件 11:31, 同日完成)
- **费用**: 未单独计量 (2026-08 时点无 per-run 成本记录; 该能力已列入
  独立度量体系 TODO)。检索走 S2 单 key (免费档), 无付费接口。

## 执行链与产物 (逐文件可核)

| 步骤 | 原子 | 产物 | 实测结果 |
|------|------|------|---------|
| 1 | knowledge-acquisition | `acq/acq_result.json` | 60 篇, **metadata-only** (见下) |
| 1b | — | `acq/merged.bib`, `acq/d1-d5.txt` | 34/60 DOI 覆盖, 21/34 OA 链接 |
| 2 | knowledge-extraction | `ext_result.json` | 60 条 knowledge items |
| 3 | association-discovery | `asc_result.json` | 4 relations, 2 gaps |
| 4 | hypothesis-generation | `hyp_result.json` | 2 个假设 (H1/H2), 各带可证伪条件 |
| 5 | argument-expression | `paper.tex` (+ `paper.pdf`) | 1371 词, IMRaD 完整, 8 个 section |
| 6 | viewpoint-verification | `ver_result.json` | H1/H2 反方观点 + falsification condition + robustness |
| 7 | quality-gate | `final.json` | **overall_pass: false** (见下) |

## 系统自己记录的失败 (凡数必源, 原样引用 pipeline_trace.json)

**ACQ 降级** — `atoms.knowledge-acquisition.honesty_notes` (原文):
```
检索步完成: 60 篇 (S2 精确匹配, BibTeX 元数据完整)
DOI 覆盖: 34/60 (S2 单 key 降速)
OA 链接: 21/34 (OpenAlex oa_url, 但 PMC 反爬)
PDF 下载: 0 篇 (PMC 反爬 + Sci-Hub Cloudflare + bban.top 404 + 无代理)
根因: 当前环境无有效代理
论文是元数据级 ACQ (非全文级), 凡数必源数字来自标题/摘要推断
```
→ 状态字段如实标为 `completed_metadata_only`, 不是 `completed`。

**质量门未通过** — `final.json`:
```
overall_pass: false
overall_score: 0.8574
G1_identity: pass (1.0)
G2_compile:   pass (1.0)
G3_citation:  FAIL (0.2593) — 10 个孤儿引用 (tex 键与 bib 键不匹配):
              ._lorin2005 (bib 中为 p._lorin2005), a._vats2021, d._yacovino2009, ...
```
根因已定位 (2026-09-06 复核): 论文集群的引用键带源前缀 (`p._lorin2005`),
ARG 步生成的 .tex 用了不一致的前缀 (`.tex` 27 个 \cite 键 vs
`merged.bib` 57 个键, 键名对不上的有 10 个)。这是**未修复的真实缺陷**,
保留在此作为复现基线: 任何人重跑 ACQ→ARG 链, G3 分数就是对照值。

## 人工修订记录

无。本案例为单次会话自动完成, 之后未经人工修改 (文件 mtime 均在同一天,
无后续 edit 痕迹)。这本身也是一个局限: 案例覆盖的是
「机器草稿」阶段, 不含「人工修订 / 专家审核 / 投稿」阶段 — 那些阶段的
样本在仓库论文集群中, 未打包进本案例 (含更敏感的机构信息)。

## 如何复现

1. `git clone` 仓库, `./install.sh` (见根目录脚本)
2. 配置 `SEMANTIC_SCHOLAR_API_KEY` (免费档即可, 但会降速)
3. 在 Hermes/Codex/dsh 会话中加载 `core/task-router`, 输入:
   「上半规管 (ASC) 诊断和治疗方法研究」
4. 预期: 7 原子链自动调度, 产物落 `outputs/{session_id}/`
5. **不承诺逐字节一致** — LLM 输出有随机性; 应核对的是: 链完整性
   (pipeline_trace.json 各原子 status)、ACQ 篇数量级、G3 未通过的复现。

## 目录结构

```
examples/asc-bppv-study-20260820/
├── pipeline_trace.json   # 全程追踪 (含 honesty_notes 失败记录)
├── acq/                  # 步骤1: 检索记录 + 5 源原始返回 + merged.bib
├── ext_result.json       # 步骤2: 60 条结构化知识
├── asc_result.json       # 步骤3: 4 关联 + 2 空白
├── hyp_result.json       # 步骤4: H1/H2 假设
├── paper.tex / paper.pdf # 步骤5: 稿件 (IMRaD, 1371 词)
├── ver_result.json       # 步骤6: 反方论证 + 证伪条件
└── final.json            # 步骤7: 质量门 (pass=false, G3 失败明细)
```

## 隐私声明

案例打包前已做 PII 扫描 (邮箱正则 + 手机号 + 已知泄露凭证清单): 0 命中。
原始目录 `outputs/asc-bppv-study-20260820/` 含编译日志和 PDF, 未打包
(二进制文件中的噪声匹配无法逐一定性, 保守处理)。
