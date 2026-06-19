---
name: pil-image-generation
description: "Python Pillow生成科技风格图像。无matplotlib依赖，适合封面/卡片/原子图。"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: []

---




## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）


# PIL Image Generation

## 原理层·文言

> 以像素为笔，以算法为墨。
> 不画无主之图，不展无据之像。
> 封面者，首因也。一图定乾坤，一色分高下。
> 深色科技风为本，蓝金配色为用。

## 方法层·白话

Python Pillow生成科技风格图像。无matplotlib依赖，适合封面/卡片/原子图。

### 触发条件

- 需要非科学插图（封面/卡片/宣传图）
- matplotlib不适合的场景
- 需要快速生成社交推广图

---

## 核心技法

| # | 技法 | 一句话用法 |
|:-:|:-----|:----------|
| 1 | 渐变背景 | `ImageDraw.rectangle + for y in range(h): fill(y)` — 线性/径向渐变 |
| 2 | 六边形绘制 | `polygon(hex_points(cx,cy,r))` — 原子节点/网络图 |
| 3 | 节点布局 | 按层级/环形排列原子位置，连线+标注 |
| 4 | 封面模板 | 深色底(#0F172A) + 渐变 + 标题(白) + 蓝金点缀(#3B82F6/#F59E0B) |
| 5 | 粗体双描 | 先描黑边再写白字，模拟粗体效果 |
| 6 | 双语标注 | 英文缩写在上+中文全称在下，`bbox`分离 |
| 7 | 半透明面板 | `Image.new('RGBA', size, color)` 叠加 `paste(panel, mask=panel)` |
| 8 | HTML+Chromium | 复杂布局用HTML渲染 → `playwright.screenshot()` |
| 9 | 封面修复 | 标题截断→缩小字号/换行；颜色冲突→调暗背景/增对比 |

---

## 设计原则

| 原则 | 说明 |
|:-----|:------|
| 深色科技风 | 背景 #0F172A，文本 white/#CBD5E1 |
| 蓝金配色 | 主蓝 #3B82F6，强调金 #F59E0B |
| 留白优先 | 不塞满，留呼吸空间 |
| 字体分级 | 标题 48-60px，副标题 28-36px，正文 16-20px |
| 卡片布局 | 圆角12px，内边距24px，阴影自动 |

---

## 关联

| 关联skill | 关系 |
|:---------|:-----|
| nature-paper2ppt | 从论文生成PPTX（含图像+排版） |
| powerpoint | python-pptx底层编辑（表格/单元格/模板） |

---

## 脚本

| 路径 | 用途 |
|:-----|:-----|
| scripts/generate-cover.py | 标准封面图生成 |
| scripts/xiaohongshu-card.py | 小红书推广卡片 |

---

## 验证清单

- [ ] 颜色对比充足（白字在浅底不可读→加深底/加阴影）
- [ ] 字体不截断（长标题自动换行）
- [ ] 输出格式 PNG，dpi≥150
- [ ] 标题+副标题+核心视觉三个层级清晰
- [ ] 无未授权字体/图片