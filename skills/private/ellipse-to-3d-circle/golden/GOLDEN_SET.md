---
name: ellipse-to-3d-circle
description: GOLDEN_SET.md
---

# 金测集: ellipse-to-3d-circle

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试：正交投影下瞳孔椭圆逆投影为 3D 圆（含深度模糊标注） | 见 expected/case_001.json |
| case_002 | 错误路径测试：b/a 越界（b > a）应报错；a = b 正对相机应提示单帧无法确定旋转 | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
