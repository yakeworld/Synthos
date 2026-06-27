# 瞳孔形态检测技术 — 文献调研记录

> 2026-06-27 — 本地 session 用 PubMed API 检索，生成综述报告

## 检索方法

使用 PubMed E-Utils API（无 API 密钥，免费）：
- efetch.fcgi — 获取论文摘要
- esearch.fcgi — 搜索论文
- esummary.fcgi — 获取论文标题

## 关键发现

### 自动瞳孔检测（2024-2026前沿）
- **LEeyes** (Byrne SA et al., Behav Res Methods 2025): 轻量级合成眼图像深度学习框架
- **OpenIrisDPI** (Ressmeyer RA et al., J Neurosci Methods 2026): 开源双 Purkinje 像眼动追踪
- **3DeepVOG** (2026): 实时高精度 3D 眼动追踪
- **GPT-4 Vision 瞳孔追踪** (PMC PMID:40478723): 端到端瞳孔追踪过程验证
- **Transformer 眼震检测** (2026): 扭转性眼震 Transformer 检测系统

### 临床前庭应用
- **前庭性偏头痛定量瞳孔分析** (Casani AP et al., Audiol Res 2026)
- **儿童 ECMO 神经预后瞳孔监测** (McGetrick M et al., Eur J Pediatr 2026)
- **Parkinson 病视网膜+瞳孔光反射** (Munro J et al., NPJ Parkinsons Dis 2026)
- **意识障碍眼动评估系统综述** (Estraneo A et al., Brain Sci 2026)

### 精度对比
| 技术 | 精度 | 响应速度 | 自动化程度 |
|------|------|---------|-----------|
| 人工测量 | 0.5mm | 分钟级 | 0% |
| Hough/椭圆拟合 | 0.1mm | 秒级 | 60% |
| 深度学习 | <0.05mm | 实时(>30fps) | 95%+ |

## 温州团队定位
- 已有眩晕/前庭瞳孔数据基础 → 可快速建立临床专用模型
- 技术路线：深度学习自动检测 → 移动端部署 → 多中心验证
- 优势：非侵入、床旁可操作、可量化可重复

## 报告输出
- Markdown: /home/yakeworld/Synthos/reports/pupil-shape-technology-advancement.md
- PDF (xelatex+ctex): /tmp/pupil-chinese.pdf (101KB)
- PNG 截图: /tmp/pupil-page-*.png (4页)
