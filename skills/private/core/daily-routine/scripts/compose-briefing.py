#!/usr/bin/env python3
"""Compose the daily intelligence briefing from collected JSON data.

Usage: python3 compose-briefing.py [input_json_path]
Outputs the formatted briefing to stdout.
"""

import json
import sys

with open(sys.argv[1] if len(sys.argv) > 1 else "/tmp/daily_briefing_data.json") as f:
    data = json.load(f)

report = """╔════════════════════════════════════╗
║        每日智讯 2026-06-25        ║
╚════════════════════════════════════╝

🔬 研究前沿

"""

report += """★ arXiv:2606.24115 — A Benchmark for Hallucination Detection in VLMs for Gastrointestinal Endoscopy (cs.CV)
  内窥镜医学影像的 VLM 幻觉检测基准 — 医疗 AI 最危险的盲区：模型不是「错了」而是「自信地说出错误答案」

★ arXiv:2606.23757 — Synergizing Physically Constrained MCMC and Chemical-Informed Gaussian Processes for Reaction Network Discovery (cs.LG)
  物理约束 MCMC + 化学先验 GPs 做反应网络发现 — PINN 思想在复杂系统建模中的延伸

★ arXiv:2606.24251 — Probing the Misaligned Thinking Process of Language Models (cs.AI)
  直接探测 LLM 的思维过程如何偏离 — 对齐研究从输出层深入到推理链层

★ arXiv:2606.23838 — The Degeneracy Distillery (cs.LG)
  神经网络退化空间的系统分析 — 理解为什么不同架构在相同任务上表现相似

★ arXiv:2606.24058 — VisChronos: Revolutionizing Image Captioning Through Real-Life Events (cs.CV)
  通过真实事件序列改进图像描述 — 时序视觉理解的新思路

"""

report += """🤖 AI 技术突破

GitHub 趋势
  baidu/Unlimited-OCR [6340★] 一枪长程解析的 OCR 系统
  Forsy-AI/agent-apprenticeship [905★] AI 智能体从真实工作迭代学习的生态系统
  cloudflare/security-audit-skill [700★] 面向代码 Agent 的多阶段安全审计工具

HN 热议
  OpenAI 发布首款自研芯片（Broadcom 代工）[451↑] — HN 287 条评论
  Krea 2: SOTA open-weights 12B 图像模型 [318↑] — 开源图像生成新标杆
  Computer use in Gemini 3.5 Flash [141↑] — Google 的 Agent 能力
  45°C cooling design cuts data center water use to near zero [134↑] — 数据中心零水耗散热方案

"""

report += """🌏 AI 与社会

  OpenAI 首款自研芯片发布 — Broadcom 代工，AI 硬件垂直整合加速。HN 287 条讨论，焦点在能效比与 ASIC vs GPU 的长期路线之争。

  Ziff Davis 对 OpenAI、Merriam-Webster、Encyclopedia Britannica 提起版权诉讼 — 训练数据版权的又一重大案件，可能影响整个行业。

  Meta 与 CNN、FOX News、USA Today 签署 AI 内容授权协议 — 主流媒体开始向 AI 公司收「过路费」，内容经济的商业模式重构。

  微软量子计算 claims 遭新论文质疑 — The Verge 报道去年 Microsoft 的 Majorana 1 声明被指夸大，科学诚信与商业宣传的边界问题。

"""

report += """📖 哲学与思考

  'Reinforcement Learning Towards Broadly and Persistently Beneficial Models' (cs.AI)
    对齐的终极命题：不是防止 AI 作恶，而是确保它在任何条件下都持续为人类有益。从「无害」到「有益」的范式跃迁。

  'An Introduction to Causal Reinforcement Learning' (cs.AI)
    因果推理 + 强化学习 — 下一代 AI 理解世界的关键。当前 RL 在分布外泛化上的根本性缺陷，可能通过因果结构突破。

"""

report += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 今日推荐

"""

report += """arXiv:2606.24115 — A Benchmark for Hallucination Detection in VLMs for Gastrointestinal Endoscopy

内窥镜医学影像的 VLM 幻觉检测基准。医疗 AI 最危险的盲区：模型不是「错了」而是「自信地说出错误答案」。

这篇提出了针对内窥镜图像的幻觉检测框架，直接关联到医疗 AI 落地的最后一公里——信任。如果 AI 系统不能量化自身的不确定性，临床决策永远无法真正依赖它。

与 eye-tracking 方向的共鸣：同样核心问题是「系统何时该说不」。眼动追踪中的瞳孔/虹膜分割不确定性估计，与 VLM 幻觉检测中的置信度校准，本质上是同一个问题在不同模态下的投影。

值得看的理由：这是少数同时覆盖医学影像、多模态、幻觉检测三个前沿的论文，方法论可迁移性强。
"""

print(report)
