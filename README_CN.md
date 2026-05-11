
<p align="center">
  <img src="docs/Synthos_封面_1920x1080.png" alt="Synthos Banner" width="700"/>
</p>

<h1 align="center">Synthos — 自主进化学术科研认知操作系统</h1>

<p align="center">
  <em>碳硅共生的开源实现 · 让每个研究者成为超级个体</em>
</p>

<p align="center">
  <a href="https://github.com/yakeworld/Synthos/stargazers"><img src="https://img.shields.io/github/stars/yakeworld/Synthos?style=flat&logo=github" alt="Stars"/></a>
  <a href="https://github.com/yakeworld/Synthos/actions/workflows/agent-pr-verify.yml"><img src="https://github.com/yakeworld/Synthos/actions/workflows/agent-pr-verify.yml/badge.svg" alt="CI"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/></a>
  <a href="https://github.com/yakeworld/Synthos/discussions"><img src="https://img.shields.io/badge/社区-Discussions-blueviolet" alt="Discussions"/></a>
  <img src="https://img.shields.io/badge/进化-20%20轮-success" alt="Evolution"/>
  <img src="https://img.shields.io/badge/版本-v4.2.0-blue" alt="Version"/>
</p>

<p align="center">
  <a href="#-设计哲学">设计哲学</a> •
  <a href="#-系统架构">系统架构</a> •
  <a href="#-7大认知原子">7大认知原子</a> •
  <a href="#-自进化引擎">自进化引擎</a> •
  <a href="#-评估体系">评估体系</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-给AI智能体">🤖 智能体贡献</a>
</p>

---

## 一句话

> **Synthos** 是一个纯技能驱动、会自我进化的科研认知操作系统。它将科研全流程分解为 7 个认知原子，每个原子是一份 SKILL.md，由 Agent 原生执行。配合自进化引擎，每天自动检查健康、跑测试、吸收外部知识，持续自我增强。

[🌐 English Version](README.md)

---

## 🧠 设计哲学

Synthos 基于 **碳硅共生（Carbon-Silicon Symbiosis）** 理念构建：

- **碳基**（人类）负责：直觉判断、伦理决策、方向选择
- **硅基**（AI）负责：海量检索、模式识别、自动化执行
- **共生**：人在回路（Human-in-the-Loop），互相增强

### 四项宪法原则

| 原则 | 含义 |
|:----|:------|
| P0 证据可溯性 | 每个输出可追溯来源 |
| P1 原子可复现性 | 每个原子独立可测 |
| P2 稳定下沉/演化上浮 | 好的变技能，坏的被淘汰 |
| P3 人机分层 | 路由器路由，人类决策，原子执行 |

---

## 🏗 系统架构

```text
                     ┌──────────────┐
                     │   任务路由器   │  ← 人在回路
                     │ 路由→原子→评估│
                     └──────┬───────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
 ┌────────────┐    ┌────────────┐    ┌────────────┐
 │  ACQ       │    │  COD       │    │  ASC       │
 │  知识获取  │    │  同行编码  │    │  论证表达  │
 │  检索文献  │    │  编码实现  │    │  论文写作  │
 └────────────┘    └────────────┘    └────────────┘
 ┌────────────┐    ┌────────────┐    ┌────────────┐
 │  EXT       │    │  EVA       │    │  AVA       │
 │  外部吸收  │    │  质量评估  │    │  认知吸收  │
 │  吸收项目  │    │  7维评分   │    │  经验编码  │
 └────────────┘    └────────────┘    └────────────┘
                            │
                     ┌──────┴──────┐
                     │  自进化引擎  │
                     │  每日自动循环 │
                     └─────────────┘
```

---

## 🧬 7大认知原子

| 原子 | 名称 | 功能 |
|:----|:-----|:-----|
| **ACQ** | 知识获取 | Semantic Scholar、OpenAlex、bioRxiv、PubMed 自动检索 |
| **COD** | 同行编码 | 将认知需求转化为可执行代码 |
| **ASC** | 论证表达 | 结构化推理、论文框架生成 |
| **EXT** | 外部吸收 | 从开源项目吸收优质模式 |
| **ROU** | 任务路由 | "人在回路"核心设计 |
| **EVA** | 质量评估 | 7维度客观评估体系 |
| **AVA** | 认知吸收 | 硅基发现→碳基知识编码 |

---

## 🔄 自进化引擎

每天自动运行一次进化循环：

```
LOAD_STATE → LESSONS → PROBE → BENCHMARK → EXTERNAL → DIAGNOSE → RECORD
     ↑                                                              │
     └──────────────────── 进化循环 ────────────────────────────────┘
```

**进化成果**（截至 2026-05）：

| 指标 | 数值 |
|:----|:------|
| 总进化轮数 | 20 轮 |
| 连续 EXCELLENT | 9 次 |
| Golden Test 通过率 | 100%（8/8） |
| 原子测试分 | 1.0（7/7 满分） |
| 质量评分 | 0.95 EXCELLENT |
| 外部来源吸收 | 8 个 |

---

## 📊 评估体系

7 维度加权评分：

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

## 🚀 快速开始

```bash
git clone https://github.com/yakeworld/Synthos.git
cd Synthos
ls -la skills/       # 查看技能结构
cat skills/task-router/SKILL.md  # 路由器入口
```

---

## 🤖 给AI智能体

**Synthos 欢迎 AI 智能体贡献！**

我们设计了完整的 Agent 贡献协议：

| 文档 | 说明 |
|:----|:------|
| [AGENTS_CONTRIBUTING.md](AGENTS_CONTRIBUTING.md) | 智能体贡献指南（含 AGENT_MANIFEST.yaml） |
| [VERIFICATION_GATES.md](VERIFICATION_GATES.md) | 6 道验证门流程 |
| [CI Workflow](.github/workflows/agent-pr-verify.yml) | 自动 CI 验证 |

**流程**：`Fork → 添加 AGENT_MANIFEST.yaml → PR 标题加 [agent] → 6道CI验证 → 人类审核 → Merge`

[💬 加入讨论](https://github.com/yakeworld/Synthos/discussions) • [🐛 提交 Issue](https://github.com/yakeworld/Synthos/issues)

---

## 📄 开源协议

MIT License

---

## 📚 相关文档

| 文档 | 说明 |
|:----|:------|
| [技术路线图](docs/%E6%8A%80%E6%9C%AF%E8%B7%AF%E7%BA%BF%E5%9B%BE.md) | 完整架构设计 |
| [智能体建设说明书](docs/%E6%99%BA%E8%83%BD%E4%BD%93%E5%BB%BA%E8%AE%BE%E8%AF%B4%E6%98%8E%E6%98%8E.md) | 超级个体方法论 |
| [社区推广策略](docs/community-promotion-strategy.md) | 推广与社区建设 |

---

**Synthos — 碳硅共生，从哲学到代码。**
