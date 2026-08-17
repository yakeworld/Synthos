# GOLDEN_SET.md — baoyu-comic

> 对应原则：P1（认知原子语义可复现：同一输入 → 等价工作流决策、产物结构与安全校验通过金标准测试）
> golden_set_origin: self_defined
> skill_role: external-automation 叶子技能 / 知识漫画创作（分析→分镜→提示词→出图→下载→报告）

## 设计依据

本技能将用户提供的内容（文本/文件/URL/主题）转化为原创知识漫画，核心约束：
- `image_generate` 为 **prompt-only**（仅接受 prompt + aspect_ratio，返回 URL），角色一致性靠
  `characters/characters.md` 的**文本描述内联嵌入**每一页提示词，而非参考图
- 每页出图前必须先把最终提示词写入 `prompts/NN-{cover|page}-[slug].md`（可复现性记录）
- 每个返回 URL 必须用**绝对路径** `curl -fsSL` 下载到 `comic/{topic-slug}/` 并验证非空
- 输出目录结构固定；参考图拷贝到 `refs/` 并记录 usage/traits；源内容须先扫描剔除凭据
- Step 2 风格确认不可跳过；clarify 超时导致的默认须逐条显式展示，不得折叠为全默认

金标准验证目标：

1. **工作流完整性**：正常多页漫画走完 分析→(确认)→分镜+角色→提示词→出图(角色表+各页)→下载→报告
2. **产物结构正确性**：目录名/文件名符合约定；每页提示词先于出图存在；角色文本嵌入每页
3. **安全约束**：敏感公众人物风格化替代；源内容剔除 API key/token 后才写盘
4. **错误处理**：出图失败/下载失败/输入缺失时的降级与恢复建议（不崩溃、给出上下文）

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 正常路径 | 1 case | 10 页 ohmsha 预设漫画，完整工作流 + 产物结构 + 绝对路径下载 |
| 错误路径 | 1 case | 出图 URL 下载失败（文件为空/缺失）→ 自动重试一次 + 报恢复建议 |

## 测试用例 (cases/)

### case_001: 正常路径 — 多页 ohmsha 知识漫画完整生成
- **输入**: 主题"艾伦·图灵的传记"，指定 preset=ohmsha、pages=10、aspect=3:4、language=zh、含一张风格参考图
- **期望**: 输出目录 `comic/alan-turing-bio/` 结构完整（source/analysis/storyboard/characters/prompts/各页 PNG）；
  Step 2 确认完成；每页提示词先写入 `prompts/`；角色描述内联每页；参考图拷至 `refs/` 且 frontmatter 记录 usage/traits；
  3:4 → `image_generate` 的 `portrait`；所有 PNG 用绝对路径下载且非空

### case_002: 错误路径 — 出图 URL 下载失败（文件为空）
- **输入**: 与 case_001 同类，但第 6 页 `image_generate` 返回的 URL 下载后文件为空
- **期望**: 不崩溃；检测到目标路径文件缺失/为空；自动重试一次；仍失败则记录该页失败，
  报告含失败页码、上下文（绝对路径 + URL）与恢复建议（重试/换比例/人工复核），并提示已存在页的 `-backup` 命名约定

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。

期望输出采用**语义等价判定**：
- 正常路径：`output_dir` 命名正确；`required_files` 全部存在；`prompt_written_before_image` 为 true；
  `character_desc_embedded_in_every_prompt` 为 true；`aspect_map["3:4"] == "portrait"`；
  `downloads` 全部 `verified_non_empty == true` 且 `path_is_absolute == true`
- 错误路径：`does_not_crash` 为 true；`failure_detected` 为 true（file empty/missing）；
  `retried_once` 为 true；`report` 含 failed_page / context / recovery_advice 非空
- 所有 case：`source_scanned_for_secrets` 为 true；敏感公众人物 `stylized_alternative` 为 true
- expected 与 cases 数量、命名一一对应

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过（Step 2 未跳过、提示词先于出图、下载绝对路径且非空、错误路径不崩溃）
- expected 与 cases 数量、命名一一对应

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | Step 2 确认 / 提示词先写 / 下载非空绝对路径 / 错误不崩溃 |
| high | 0.7 | 产物结构完整 / 角色文本嵌入 / aspect 映射 / 凭据剔除 |
| medium | 0.4 | 参考图 refs 记录 / 敏感人物风格化 / 恢复建议完备 |

## 验证命令

```bash
# JSON 有效性
for f in golden/cases/*.json golden/expected/*.json; do
  python3 -c "import json; json.load(open('$f'))" || echo "FAIL: $f"
done

# 数量配对
test "$(ls golden/cases/*.json | wc -l)" -eq "$(ls golden/expected/*.json | wc -l)"

# 产物结构抽检（对实际 comic/{slug}/ 目录）
test -f comic/<slug>/storyboard.md && test -d comic/<slug>/prompts
for f in comic/<slug>/prompts/*.md; do test -s "$f"; done
```
