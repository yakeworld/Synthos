# nature-paper2ppt Golden Set

## 目的
验证 nature-paper2ppt 技能的正确性和鲁棒性。

## 测试用例

| ID | 输入 | 场景 | 关键检查 |
|:---|:-----|:-----|:---------|
| test01_basic | 标准英文论文元数据+摘要 | 常规转换 | 12-16帧，中文内容，结论式标题 |
| test02_chinese_medical | 中文临床论文+图描述 | 含图的中文医学论文 | Design-to-Inference逻辑，≥2图，局限性帧 |
| test03_minimal | 仅标题+摘要 | 极限降级 | PPTX生成成功，不虚构，缺失信息标注 |

## 通过标准
- 每个测试用例的 check 加权总分 ≥ 0.80
- critical 检查项必须全部通过
