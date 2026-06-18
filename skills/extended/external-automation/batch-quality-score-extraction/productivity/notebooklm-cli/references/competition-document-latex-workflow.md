# 竞赛佐证材料 LaTeX 文档工作流

## 何时使用

当需要为竞赛（如"厚道泛雅"医学教育智能体大赛）生成高质量 PDF 证明材料时，使用 LaTeX + ctex + TikZ 替代 pandoc/markdown 转 PDF。

## 为什么不用 pandoc

| 方案 | 中文渲染 | 技术路线图 | 表格美观度 | 编译时间 |
|:-----|:---------|:-----------|:----------|:--------|
| pandoc + xelatex | ✅ 主体OK，代码块缺CJK字体 | ❌ box-drawing字符全丢失 | ⚠️ 一般 | 快 |
| 纯 LaTeX + ctex | ✅ 完美 | ✅ TikZ 矢量图 | ✅ 专业 | 需两次编译 |

pandoc 的核心问题：monospace 字体不支持 CJK 字符，导致代码块中的中文和 ASCII art 图表中的 box-drawing 字符（`┌─┐│└┘`）全部丢失。

## 设计模板

### 页面基调
- 字号：11pt，A4，2.5cm 页边距
- 标题：蓝色 `#1A73E8`，粗体
- 子标题：深蓝 `#0D47A1`
- 表格：`booktabs` 风格（`\toprule`/`\midrule`/`\bottomrule`）
- 代码块：深色背景 `#1A1A2E` + 浅色文字 `#E0E0E0`

### TikZ 技术路线图模板

使用多层堆叠结构，每层分"标题"和"内容"两层节点：

```latex
% 颜色按层区分
% Layer 1 哲学层: purple
% Layer 2 宪法层: blue  
% Layer 3 架构层: teal
% Layer 4 原子层: orange
% Layer 5 进化层: green
% Layer 6 产出层: red

% 节点样式定义
layer/.style={
    rectangle, rounded corners=3pt,
    minimum width=14cm, minimum height=1.2em,
    fill=#1!15, draw=#1, font=\small\bfseries\sffamily
},
content/.style={
    rectangle, rounded corners=3pt,
    minimum width=14cm, minimum height=1.8em,
    fill=#1!8, draw=#1!40, font=\small\sffamily
}
```

关键技术点：
- `minimum width=14cm` 保证 A4 页面不超宽
- 两层之间用 `below=2pt of` 紧密贴合
- 层间用 `\draw[arrow]` 连接：`(c.south) -- ++(0,-0.4)`

### 匿名版本处理

需要同时生成两个版本时，维护两个 `.tex` 文件：
- `项目名_原始版.tex` — 含团队成员姓名、机构名称、审核栏
- `项目名_匿名版.tex` — 隐去姓名/机构，去掉审核栏

差异点：

| 节 | 原始版 | 匿名版 |
|:---|:-------|:-------|
| 研发单位 | 机构名 + 负责人 + 方向 | 仅方向 |
| 团队贡献 | 姓名 + 角色 + 贡献 | 角色 + 贡献（无姓名） |
| 审核栏 | 保留（含公章位） | 整节删除 |
| 脚注 | "原始版本" | "匿名版本，已隐去个人信息" |

## 编译命令

```bash
xelatex -interaction=nonstopmode 文件名.tex
# 需要两次编译以确保目录/书签正确
xelatex -interaction=nonstopmode 文件名.tex
```

## 已知陷阱

1. **Overfull hbox** — 技术路线图的内容行如果太长（超过 14cm 节点宽度），会出现 overfull。缩短内容或增加节点宽度。
2. **ctex 与 fontspec 冲突** — 使用 `ctex` 包后会加载 fontspec，不要在 preamble 中额外调用 fontspec。
3. **GitHub 链接换行** — `\href{...}{...}` 在表格中可能被自动换行破坏。如果链接在表格中，确保表格列宽足够。
4. **`\textasciitilde` vs `~`** — TikZ 节点文本中需要用 `~·~` 实现间隔符，但 LaTeX 中的 `~` 是 hard space。在 `\node{...}` 中用 `~·~` 是安全的。
