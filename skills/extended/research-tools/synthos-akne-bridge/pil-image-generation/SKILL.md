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

## 坑点

| # | 坑 | 对策 |
|:-:|:---|:-----|
| 1 | HTML→Chromium 渲染路径在很多环境失效（chromium snap 无 snapd / 无 GUI 服务器） | 直接 Pillow，不要先试 HTML。技法#8 是最后手段，不是首选 |
| 2 | CJK 字体暗底上笔画偏淡 | **必须双描**：`draw.text((x,y)); draw.text((x+1,y))` |
| 3 | Linux 系统字体不渲染 emoji（豆腐块） | 正文用文字替代 emoji：🔬→"研究"，✅→"通过"，📄→"文档" |
| 4 | 正方形 1080×1080 用于质检报告/数据卡片，竖版 1080×1920 用于轮播帖 | 根据用途选尺寸：单图→方形，小红书轮播→竖版 |
| 5 | 多面板科学图（雷达/进度条/轨迹）代码量大且易出错 | 参考 figure-generation 的 `references/matplotlib-fallback.md`，使用已验证的原语。不要每次从头写。 |

---

## 视觉质量标准

| 要素 | 要求 |
|:-----|:-----|
| 对比度 | 白字在暗底上必须清晰可读（L* ≥ 50） |
| 字体分级 | 标题 36-44pt，核心指标 32-40pt，正文 20-24pt，小字 14-18pt |
| 留白 | 卡片内边距 ≥20px，元素间距 ≥16px |
| 颜色 | 通过/成功=绿色(0,221,170)，警告=橙色(255,169,77)，错误=红色(255,107,107) |
| 渲染 | 必须用 `ImageFont.truetype(NotoSansCJK*)`，fallback `ImageFont.load_default()` 不可接受 |

---

## 迭代模式

质检报告/数据可视化类图像典型迭代 2-3 轮：
1. **v1**: 基础布局，文字可能过小或对比不足
2. **v2**: 增大字号，调整间距
3. **v3**: 严格遵循视觉质量标准，双描 CJK，颜色语义化

**关键决策点**：用户说"图质量有问题"时，优先检查：①字号是否够大 ②CJK是否双描 ③颜色对比是否足够 ④布局是否过密。

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
| figure-generation | 科研图表（雷达图/进度条/轨迹图）共享 Pillow 原语。当用户要求"科研作图"时，用 figure-generation；当要求"宣传图/封面/海报"时，用 pil-image-generation。执行失败时互相回退。 |

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