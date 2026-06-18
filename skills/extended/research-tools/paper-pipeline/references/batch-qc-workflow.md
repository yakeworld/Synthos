# 批量双质量检查工作流

## 适用场景
43 篇论文统一重新执行双质量检查（编译 + Layer A + 上传 NotebookLM + Layer B）。

## Phase 1: 批量编译 + 上传

脚本：`outputs/papers/batch_qc_phase1.py`

```python
# 核心流程：
for paper in papers:
    # 1. 编译 .tex → .pdf（支持 thebibliography 和 bibtex 两种模式）
    # 2. 上传到对应 NotebookLM 项目
    #   文件名: {paper-dir-name}-v1.pdf
    #   标题: {paper-dir-name}-v1
```

### 论文→NotebookLM 项目映射
```python
PAPER_NB_MAP = {
    # Synthos主项目
    "synthos-system-paper": "b54348f4",
    "pima-crispdm": "b54348f4",
    # Kappa系列
    "kappa-3d-eye-tracking": "571024b4",
    "kappa-angle-calibration": "571024b4",
    # BPPV系列
    "bppv-minimal-stimulus": "95509a49",
    "bppv-otoconia-simulation": "95509a49",
    # VOR系列
    "vor-digital-twin": "c0bba510",
    "vor-3d-eye-tracking": "c0bba510",
    # 更多映射见脚本完整版
}
```

### 注意事项
1. UnicodeDecodeError 处理：pdflatex 输出可能含非 UTF-8 字符（中文日志），需用 `text=False` + `.decode('utf-8', errors='replace')`
2. arXiv key 名：Semantic Scholar 返回 `ArXiv`（大写 A,V），非 `arXiv`
3. Sci-Hub 搜索跳过：所有镜像被 DDoS-Guard 拦截，快检后跳过

## Phase 2: Layer B Gemini 评审

脚本：`outputs/papers/batch_qc_phase2.py`

```python
# 核心流程：
for paper in papers:
    # 1. notebooklm use {project_id}
    # 2. notebooklm ask "7维SCI评审，每维0-1"
    # 3. 解析评分 D1-D7
    # 4. 写入 quality-report.md
    # 5. 每篇间隔10s，避免限流
```

### 状态持久化
- `batch-qc-phase2-state.json`：已完成列表 + 评分数据
- 支持断点续跑（跳过已完成的论文）

## 已知问题
1. scale-space-feature-tensor：中文 UTF-8 在 pdflatex 下 1109 错误，需 xelatex
2. eye-tracking-4d：设计提案阶段，评分 0.68，需补实验
3. lit-reviews：文献归档库（290文件/105M），非论文
4. Shared 笔记本：source delete 不可用 CLI，需网页端
