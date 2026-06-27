# 作图技能测试计划

## 测试目标
验证 figure-generation 技能体系各模式是否可用、正确、符合质量要求。

## 测试用例

### 测试1: 模式A — 科学数据图
**输入**: 用matplotlib画一个包含4个方法的柱状图，比较Accuracy/F1/Recall/AUC
**预期**: PNG(300DPI) + PDF + 色盲安全、标签正确

### 测试2: 模式B — 架构图
**输入**: 画一个CNN架构流程图：Input → Conv → ReLU → Pool → Flatten → FC → Output
**预期**: 框+箭头，箭头终点在框内，无重叠

### 测试3: 模式C — Excalidraw手绘
**输入**: 生成一个科研流程图（excalidraw JSON格式）
**预期**: .excalidraw JSON文件，可直接拖到 excalidraw.com 打开

### 测试4: 模式D — 数据卡片封面
**输入**: 生成一个深色科技风的数据结果展示卡片
**预期**: 1080x1080 PNG，深蓝黑背景，白字，蓝金点缀

### 测试5: QA自动化
**输入**: 检查测试2的架构图是否存在框重叠或箭头越界
**预期**: PASS/FAIL报告
