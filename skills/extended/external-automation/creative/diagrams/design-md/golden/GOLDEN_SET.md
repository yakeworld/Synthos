# GOLDEN_SET.md — design-md

> 对应原则：P1（认知原子语义可复现：同一输入 → 等价产物结构通过金标准测试）
> golden_set_origin: self_defined
> skill_role: external-automation 叶子技能 / DESIGN.md 规范编写与校验

## 设计依据

本技能基于 Google 开放规范（`google-labs-code/design.md`, Apache-2.0），将视觉识别描述
为「YAML front matter（设计令牌）+ Markdown 正文（规范章节）」的单一文件，并用 CLI
`npx -y @google/design.md lint` 做结构与 WCAG 对比度校验。金标准验证目标：

1. **结构正确性**：front matter 含必需的 `name:` 与 `colors:`；正文 `##` 章节按
   Overview→Colors→Typography→Layout→Elevation→Shapes→Components→Do's/Don'ts 顺序且无重复标题
2. **令牌合法性**：颜色为带引号 hex 字符串、负维度（如 `-0.02em`）加引号，YAML 可解析
3. **组件约定**：`components:` 用 `{token.path}` 引用而非硬编码 hex；hover/active 变体
   为同级键（`button-primary-hover`）而非嵌套属性
4. **校验可达性**：`npx -y @google/design.md lint DESIGN.md` 退出码 0，无 broken-ref / invalid-* 错误

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 正常路径 | 1 case | 合法 DESIGN.md 模板（starter.md 派生），lint 通过 |
| 错误路径 | 1 case | 非法 DESIGN.md（broken-ref + 未引号负维度 + 嵌套变体 + 重复标题），lint 应报错 |

## 测试用例 (cases/)

### case_001: 正常路径 — 合法 DESIGN.md 生成与校验
- **输入**: 请求"为一个极简学术品牌生成 DESIGN.md，主色 #0F172A，强调色 #2563EB，Inter 字体"
- **期望**: 生成的 DESIGN.md 通过 lint（exit 0）；front matter 含 name+colors；章节有序；
  组件用 token 引用；变体为同级键；lint 报告无 error（WCAG 对比度结论被汇报）

### case_002: 错误路径 — 非法 DESIGN.md（多类违规）
- **输入**: 请求"校验这份 DESIGN.md"，内容含：`components` 指向不存在的 `{colors.missing}`、
  未引号负维度 `letterSpacing: -0.02em`、嵌套变体 `button-primary: {hover: ...}`、重复 `## Colors` 标题
- **期望**: lint 返回非零退出码，错误分类命中 broken-ref / invalid-dimension（或 YAML 解析失败）/
  duplicate-section；结果不崩溃，返回结构化 error 列表与逐条恢复建议

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。

期望输出采用**语义等价判定**：
- `lint.exit_code` 必须精确匹配（0 / 非0）
- 错误路径：`errors` 列表必须覆盖期望违规类别（broken-ref、duplicate-section、YAML/invalid-dimension）
- 正常路径：`frontmatter_required_present` 为 true、`section_order_valid` 为 true、`yaml_parses` 为 true
- 所有 case：`wcag_findings_reported` 为 true（对比度结论须显式汇报）
- 错误路径：`recovery_advice` 列表非空，错误信息含上下文

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过（lint 退出码判定、YAML 可解析、不崩溃）
- expected 与 cases 数量、命名一一对应

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | lint 退出码判定 / YAML 可解析 / 错误路径不崩溃 |
| high | 0.7 | 章节顺序 / 变体同级键 / token 引用 |
| medium | 0.4 | WCAG 对比度汇报 / 恢复建议完备 |

## 验证命令

```bash
# JSON 有效性
for f in golden/cases/*.json golden/expected/*.json; do
  python3 -c "import json; json.load(open('$f'))" || echo "FAIL: $f"
done

# 数量配对
test "$(ls golden/cases/*.json | wc -l)" -eq "$(ls golden/expected/*.json | wc -l)"

# 令牌文件 lint（如环境允许联网）
npx -y @google/design.md lint <case_001 产物>.md && echo "PASS"
```
