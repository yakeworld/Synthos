
<p align="center">
  <img src="docs/Synthos_封面_1920x1080.png" alt="Synthos Banner" width="700"/>
</p>

<h1 align="center">Synthos — 自主进化学术科研平台</h1>

<p align="center">
  <em>A Computable, Collaborative, and Evolving Cognitive Operating System for Science</em>
</p>

<p align="center">
  <a href="https://github.com/yakeworld/Synthos/stargazers"><img src="https://img.shields.io/github/stars/yakeworld/Synthos?style=flat&logo=github" alt="Stars"/></a>
  <a href="https://github.com/yakeworld/Synthos/actions/workflows/agent-pr-verify.yml"><img src="https://github.com/yakeworld/Synthos/actions/workflows/agent-pr-verify.yml/badge.svg" alt="CI"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/></a>
  <a href="https://github.com/yakeworld/Synthos/discussions"><img src="https://img.shields.io/badge/Community-Discussions-blueviolet" alt="Discussions"/></a>
  <img src="https://img.shields.io/badge/Evolution-20%20cycles-success" alt="Evolution"/>
  <img src="https://img.shields.io/badge/Version-v4.2.0-blue" alt="Version"/>
</p>

<p align="center">
  <a href="#-philosophy">Philosophy</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-cognitive-atoms">Atoms</a> •
  <a href="#-self-evolution">Evolution</a> •
  <a href="#-evaluation">Evaluation</a> •
  <a href="#-getting-started">Setup</a> •
  <a href="#-for-ai-agents">🤖 Contribute</a>
</p>

---

**Synthos** 是一个 **纯技能（SKILL.md）驱动** 的认知操作系统，用于科学研究。它将科研全流程分解为 **7 个认知原子**，每个原子由 Agent 原生执行的 SKILL.md 定义——不产生 Python 脚本，纯粹通过 Agent 的推理能力完成认知任务。

从文献检索到论文输出，Synthos 完整覆盖科研的认知闭环。配合 **自进化引擎**，系统每天自动检查健康状况、执行功能测试、从外部项目吸收养分，持续自我增强。

> **当前版本**: v4.2.0 · 进化引擎 v2.3 · 综合评分: 95/100 · 进化循环: 20轮 · Agent PR 验证: ✅

[🇨🇳 中文版](README_CN.md)

---

## 🧠 Philosophy

Synthos 基于 **八维认知框架** 构建：

| # | 维度 | 核心思想 | 覆盖原子 | 实现度 |
|:-:|------|---------|:--------:|:-----:|
| 1 | **第一性原理** | 从原始事实逐层构建 | 1,2,4,5 | 95% |
| 2 | **系统思维** | 整体视角理解知识关系 | 1,3,5 | 95% |
| 3 | **贝叶斯思维** | 基于证据更新信念 | 4,6 | 90% |
| 4 | **类比思维** | 跨领域知识迁移 | 4 | 80% |
| 5 | **奥卡姆剃刀** | 最短路径优先 | 0,2,5 | 80% |
| 6 | **证伪主义** | 主动寻找反证 | 6,1 | 80% |
| 7 | **模型依赖实在论** | 多视角、多源交叉验证 | 3 | 60% |
| 8 | **自由能原理** | 自我进化、最小化预测误差 | 6, meta | 55% |

**综合实现度**: 85%（基于内置审计框架）

核心原则：**宪法 → 架构 → Schema → 实现**，逐层定稿不回溯。每层产出形式化定义（非重叠性证明、I/O 契约、追溯矩阵）。

---

## 🏗 Architecture

> **设计理念**: 宪法驱动（Constitutional Design），人机分层（Human-in-the-Loop），从哲学到代码逐层落地。

```text
                     ┌──────────────────────┐
                     │    任务路由器（ROU）   │  ← 人在回路
                     │   [路由 → 原子 → 评估] │
                     └────────┬─────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
 ┌───────────────┐  ┌────────────────┐  ┌────────────────┐
 │  ACQ          │  │  COD           │  │  ASC           │
 │  知识获取     │  │  同行编码      │  │  论证表达      │
 │  S2/OpenAlex  │  │  可执行思维    │  │  结构化推理    │
 └───────────────┘  └────────────────┘  └────────────────┘
 ┌───────────────┐  ┌────────────────┐  ┌────────────────┐
 │  EXT          │  │  EVA           │  │  AVA           │
 │  外部吸收     │  │  质量评估      │  │  认知吸收      │
 │  GitHub/Paper │  │  7维评分体系   │  │  经验→技能     │
 └───────────────┘  └────────────────┘  └────────────────┘
                              │
                     ┌────────┴────────┐
                     │  自进化引擎      │
                     │  每日自动循环    │
                     └─────────────────┘
```

---

## 🧬 Cognitive Atoms

| 原子 | 名称 | 功能 | 状态 |
|:----|:-----|:-----|:-----|
| **ACQ** | 知识获取 | 从 Semantic Scholar、OpenAlex、bioRxiv、PubMed 检索文献 | ✅ v4.2 |
| **COD** | 同行编码 | 将认知需求转化为可执行代码 | ✅ v4.2 |
| **ASC** | 论证表达 | 推进结构化推理，生成论文框架 | ✅ v4.2 |
| **EXT** | 外部吸收 | 从开源社区吸收优质模式 | ✅ v4.2 |
| **ROU** | 任务路由 | "人在回路"核心：路由常规任务，上报异常 | ✅ v4.2 |
| **EVA** | 质量评估 | 客观可度量的进化指标（7维度） | ✅ v4.2 |
| **AVA** | 认知吸收 | 将硅基发现编码为碳基可理解的知识 | ✅ v4.2 |

---

## 🔄 Self-Evolution

Synthos 配备 **自进化引擎**，每天自动运行：

```
LOAD_STATE → LESSONS → PROBE → BENCHMARK → EXTERNAL → DIAGNOSE → RECORD
     ↑                                                              │
     └──────────────────────── 进化循环 ────────────────────────────┘
```

| 指标 | 值 |
|:----|:----|
| 进化循环 | 20 轮（截至 2026-05） |
| 连续 EXCELLENT | 9 次 |
| Golden Test 通过率 | 100% |
| 原子测试分 | 1.0（满分） |
| 综合评分 | 0.95（EXCELLENT） |
| 外部吸收来源 | 8 个开源项目 |

---

## 📊 Evaluation

内置 7 维度评估框架：

| 维度 | 权重 | 评分 |
|:-----|:-----|:----|
| 完整性 | 20% | 96% |
| 准确性 | 20% | 94% |
| 可复现性 | 15% | 92% |
| 自洽性 | 15% | 95% |
| 可扩展性 | 10% | 90% |
| 效率 | 10% | 88% |
| 透明度 | 10% | 93% |

---

## 🚀 Getting Started

```bash
# 克隆仓库
git clone https://github.com/yakeworld/Synthos.git
cd Synthos

# 查看技能结构
ls -la skills/

# 以路由器为入口
cat skills/task-router/SKILL.md
```

详细文档：`docs/` 目录

---

## 🤖 For AI Agents

**Synthos 欢迎 AI 智能体贡献！**

本项目设计了完整的 **Agent 贡献协议**：

| 文档 | 说明 |
|:----|:------|
| [AGENTS_CONTRIBUTING.md](AGENTS_CONTRIBUTING.md) | AI 智能体贡献指南（含 AGENT_MANIFEST.yaml 规范） |
| [VERIFICATION_GATES.md](VERIFICATION_GATES.md) | 6 道验证门流水线 |
| [GitHub Actions](.github/workflows/agent-pr-verify.yml) | 自动 CI 验证 |

**贡献流程**：
```
Fork → 添加 AGENT_MANIFEST.yaml → PR 标题加 [agent] 前缀
                                       ↓
                              6 Gates CI 自动验证
                                       ↓
                              人类审核 → Merge
```

[💬 加入讨论](https://github.com/yakeworld/Synthos/discussions) • [🐛 提交 Issue](https://github.com/yakeworld/Synthos/issues)

---

## 📄 License

MIT License — 自由使用、修改、分发。

---

## 📚 Reference

| 文档 | 说明 |
|:----|:------|
| [技术路线图](docs/%E6%8A%80%E6%9C%AF%E8%B7%AF%E7%BA%BF%E5%9B%BE.md) | 系统完整架构设计 |
| [智能体建设说明书](docs/%E6%99%BA%E8%83%BD%E4%BD%93%E5%BB%BA%E8%AE%BE%E8%AF%B4%E6%98%8E%E6%98%8E.md) | 超级个体方法论与实现 |
| [社区推广策略](docs/community-promotion-strategy.md) | 项目推广与社区建设 |
