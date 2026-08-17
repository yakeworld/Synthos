---
name: ascii-art
description: ascii-art 金测集 — 工具选择决策流与降级路径的可执行测试
---

# 金测集: ascii-art

> 来源: SKILL.md Genes（ASCI-001~007）与决策流（Decision Flow）。每个 case 验证工具选择与降级行为的正确性（P1 可复现性）。
> 核心约束：字体/角色适配文本长度；远程 API 正确编码；自定义艺术 ≤60 列宽、横幅 ≤15 行；工具缺失时按决策流降级。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 短文本横幅生成（正常路径） | 短文本(1-8字符)→细节字体(doom/block 等)（ASCI-001）；pyfiglet 可用时本地生成，否则降级 asciified API（空格 URL-encode 为 `+`） |
| case_002 | pyfiglet 未安装的降级（错误路径） | 本地工具缺失 → 按决策流降级到 asciified REST API（`curl`），并给出明确提示（ASCI-003 / 验证清单第 6 项） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 短文本必须选细节字体（doom/block/big），不得用 small/mini；输出等宽字体下渲染正确无溢出
- case_002: 必须在 pyfiglet 失败/缺失后降级到 `curl "https://asciified.thelicato.io/api/v2/ascii?text=...&font=..."`（字体名大小写敏感），降级行为有明确提示（Golden Error 路径）；直接放弃或报裸异常判失败

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001/002） |
| high | 0.7 | 重要但不致命（预留扩展 case） |

## 关联

- SKILL.md Genes: ASCI-001~007
- SKILL.md 决策流（Decision Flow）第 1 条与第 9 条（工具未安装 → 降级）
- IO_CONTRACT: `description: str, dimensions: tuple -> ascii_output: str`
