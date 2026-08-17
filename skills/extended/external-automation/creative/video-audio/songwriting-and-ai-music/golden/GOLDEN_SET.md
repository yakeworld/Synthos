# GOLDEN_SET.md — songwriting-and-ai-music

> 对应原则：P1（认知原子语义可复现：同一输入 → 等价创作决策通过金标准测试）
> golden_set_origin: self_defined
> skill_role: external-automation 叶子技能 / Suno AI 音乐生成与歌词创作

## 设计依据

本技能是 Suno AI 音乐生成的创作指导原子，核心职责是从情感核出发产出：歌曲结构、歌词、Suno Style 字段、元标签。金标准验证目标：

1. **结构正确性**：给定情感核与主题，能否选择合理骨架（ABABCB/AABA 等）
2. **公式合规**：Suno Style 字段是否遵循"流派+情绪+时代+乐器+人声+制作"公式且描述动态旅程；无艺术家名/商标
3. **元标签纪律**：每节 5-8 个不冲突标签，关键标签在 Style 与 Lyrics 双处强化
4. **音韵处理**：专有名词/数字/缩写是否做音韵改拼与试发音
5. **错误路径**：输入缺失（无情感核/主题）时的降级行为（不硬造、给出补全建议）

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 正常路径 | 2 类 | cinematic ballad（whisper→roar）、戏仿改编（结构映射） |
| 错误路径 | 2 类 | 缺失情感核/主题、Style 字段含艺术家名（需拒绝+合规替代） |
| 契约完整性 | 所有 case | 检查输出字段完备性（structure/style/metatags/phonetics） |

## 测试用例 (cases/)

### case_001: 正常路径 — cinematic ballad（whisper→roar，Suno Custom Mode）
- **输入**: 情感核 = 失去后的释然；主题 = 雨夜告别；结构偏好 = ABABCB
- **期望**: 结构=ABABCB；Style 遵循公式且含动态旅程描述（如 "sparse piano…builds from whisper to full orchestra"）；无艺术家名；结构标签 [Verse]/[Chorus]/[Bridge] 存在；每节 5-8 个不冲突标签；关键标签 Style/Lyrics 双处出现

### case_002: 正常路径 — 戏仿改编
- **输入**: 原曲结构信息（每行音节数、韵式、重音位）+ 新主题概念（crime→code 单音节替换）
- **期望**: 输出含原曲骨架映射（syllables/rhyme scheme/stressed positions）；新词重音对齐原节拍；长延音处匹配原元音；单音节替换示例（Crime→Code）；保留 ≥2 句原词

### case_003: 错误路径 — 缺失情感核/主题
- **输入**: 用户请求"写首歌"但未给情感核、主题、风格
- **期望**: 不硬造歌词；返回 error 非空（缺失字段列表），suggestions 非空（询问情感核/主题/结构偏好），lyrics 为 null

### case_004: 错误路径 — Style 字段含艺术家名/商标
- **输入**: Style 字段草稿 = "Nirvana-style grunge, sad rock song"
- **期望**: 拒绝并指出违规条款（NO artist names or trademarks）；提供合规替代（描述声音而非指名："90s grunge, distorted guitar, raw male vocals, minor key"）；error 非空

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。

期望输出采用**语义等价判定**：
- `structure` 必须精确匹配（case_001=ABABCB）
- `style_field` 必须包含公式各要素（genre/mood/era/instruments/vocal/production），且 `has_dynamic_arc=true`、`has_artist_name=false`
- `metatags`：每节 5-8 个、无同节冲突（`contradictions=[]`）
- 错误路径：`error` 非空、`suggestions` 非空、`lyrics` 为 null

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过（结构正确、无艺术家名、错误路径不硬造）
- expected 与 cases 数量、命名一一对应

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 结构正确 / 无艺术家名商标 / 错误路径不硬造歌词 |
| high | 0.7 | Style 公式完整、动态旅程描述、元标签 5-8 不冲突 |
| medium | 0.4 | 音韵处理、双处强化、保留原句数 |

## 验证命令

```bash
# JSON 有效性
for f in golden/cases/*.json golden/expected/*.json; do
  python3 -c "import json; json.load(open('$f'))" || echo "FAIL: $f"
done

# 数量配对
test "$(ls golden/cases/*.json | wc -l)" -eq "$(ls golden/expected/*.json | wc -l)"
```
