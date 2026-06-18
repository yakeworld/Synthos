# NotebookLM 生成类型实战参考（Pima糖尿病预测项目）

实战来源：`Process-Driven Credibility: A CRISP-DM Helix Framework for Robust Pima Diabetes Prediction` 项目（59源文件）

## 📄 Report（报告）

| 属性 | 值 |
|:-----|:----|
| 子格式 | study-guide（默认简报、blog-post、custom） |
| 输出格式 | Markdown |
| 生成时间 | ~30秒 |
| 下载方式 | `notebooklm download report <filename.md>` |
| 文件大小 | ~7KB（83行中文学习指南） |
| 典型内容 | 核心概念复习、数据预处理、模型评估指标、关键特征 |
| 输出质量 | 结构清晰，适合作为论文引言或教材附录 |

**命令模板：**
```bash
notebooklm generate report                                    # 简报
notebooklm generate report --format study-guide               # 学习指南
notebooklm generate report --format blog-post                 # 博客
```

## 🧠 Mind Map（思维导图）

| 属性 | 值 |
|:-----|:----|
| 输出格式 | JSON（Note形式存储） |
| 生成时间 | ~15秒 |
| 获取方式 | `notebooklm note get <note_id>` |
| 典型内容 | 5-6节点知识树（概念→数据→预处理→模型→评估→应用） |
| **注意** | artifact list可见但不可直接下载；必须用note get获取JSON |

**命令：**
```bash
notebooklm generate mind-map
# 输出 → "Note ID: xxxx, Root: ..., Children: N nodes"
# 获取 → notebooklm note get <note_id>
```

## 🖼️ Infographic（信息图）

| 属性 | 值 |
|:-----|:----|
| 输出格式 | PNG（高分辨率，可印刷） |
| 生成时间 | ~2-5分钟 |
| 下载方式 | `notebooklm download infographic <filename.png>` |
| 文件大小 | ~4.3MB（2752×1536像素典型尺寸） |
| 典型内容 | 数据流程+模型对比+指标可视化，自动排版 |

**下载注意：** 直接`notebooklm download infographic <filename>`即可；`--artifact`参数可能失败。

## 📈 Data Table（数据表）

| 属性 | 值 |
|:-----|:----|
| 输出格式 | CSV格式Markdown |
| 生成时间 | ~1-3分钟 |
| 下载方式 | `notebooklm download data-table <filename.md>` |
| 文件大小 | ~3.9KB（34行模型对比） |
| **命令注意** | **必须提供DESCRIPTION参数** |

**命令：**
```bash
notebooklm generate data-table "描述表格目的和内容"
```

## 📝 Quiz（测验题）

| 属性 | 值 |
|:-----|:----|
| 输出格式 | JSON（含question/answerOptions/rationale结构） |
| 生成时间 | ~1-3分钟 |
| 下载方式 | `notebooklm download quiz <filename.md>` |
| 文件大小 | ~21KB（10+道题每道含4选项+解析） |
| 典型内容 | 多选、判断、含提示和错误选项解析 |

## 🃏 Flashcards（闪卡）

| 属性 | 值 |
|:-----|:----|
| 输出格式 | Markdown |
| 生成时间 | ~1-3分钟 |
| 下载方式 | `notebooklm download flashcards <filename.md>` |
| 文件大小 | ~19KB |

## 🎧 Audio / Podcast（音频）

| 属性 | 值 |
|:-----|:----|
| 子格式 | deep-dive（默认）、debate、critique、brief |
| 长度控制 | short / default / long |
| 生成时间 | ~5-15分钟（后台运行） |
| 下载方式 | `notebooklm download audio <filename.mp3>` |
| **坑** | 辩论格式可能失败；先尝试默认deep-dive |

**命令：**
```bash
notebooklm generate audio                                    # 默认deep-dive
notebooklm generate audio --format debate "辩论主题"          # 双人辩论
```

## 📊 Slide Deck（幻灯片）

| 属性 | 值 |
|:-----|:----|
| 输出格式 | PPTX |
| 生成时间 | ~5-20分钟（后台运行） |
| 下载方式 | `notebooklm download slide-deck <filename.pptx>` |
| 特色 | 支持单页修订：`notebooklm generate revise-slide <id> <n> "新内容"` |

## 🎬 Video（视频）

| 属性 | 值 |
|:-----|:----|
| 风格 | auto / classic / whiteboard / kawaii / anime / watercolor / retro-print / heritage / paper-craft |
| 格式 | cinematic → Veo 3 AI纪录片（需AI Ultra） |
| 生成时间 | **最长** — 普通风格5-15分钟，cinematic格式30-40分钟 |
| 状态监控 | `notebooklm artifact list` / `notebooklm artifact wait` |

## 生成时间总结

| 类型 | 典型时间 | 建议策略 |
|:-----|:--------|:---------|
| Report / Mind Map | <1分钟 | 直接等待 |
| Infographic / Quiz / Flashcards / Data Table | 1-5分钟 | 直接等待 |
| Audio / Slide Deck | 5-20分钟 | 后台并行 |
| Video（普通风格） | 5-15分钟 | 后台并行 |
| Video（cinematic格式） | 30-40分钟 | 后台并行，最后检查 |

## 并行启动模式

```bash
# 一次性启动多个后台任务
notebooklm generate report "主题"
notebooklm generate infographic
notebooklm generate audio --format debate "主题"
notebooklm generate slide-deck "主题"
notebooklm generate video "主题"

# 统一监控
notebooklm artifact list

# 逐个下载（需轮询直到completed）
notebooklm download report <filename.md>
notebooklm download infographic <filename.png>
```
