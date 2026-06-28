# 每日智讯 — 数据源使用指南

## 四大维度对应数据源

### 维度一：研究前沿（科技）
| 来源 | URL | 格式 | 可靠性 | 备注 |
|------|-----|------|--------|------|
| arXiv cs.AI | `https://arxiv.org/list/cs.AI/recent` | HTML | ⭐⭐⭐⭐⭐ | 最新论文，每篇有ID+标题+作者 |
| arXiv cs.CV | `https://arxiv.org/list/cs.CV/recent` | HTML | ⭐⭐⭐⭐⭐ | 计算机视觉/医学影像 |
| arXiv cs.LG | `https://arxiv.org/list/cs.LG/recent` | HTML | ⭐⭐⭐⭐⭐ | 机器学习理论 |
| arXiv cs.RO | `https://arxiv.org/list/cs.RO/recent` | HTML | ⭐⭐⭐ | 机器人学 |
| HN | `https://hnrss.org/frontpage?points=20` | RSS XML | ⭐⭐⭐⭐ | 筛选科研相关的讨论 |

### 维度二：AI 技术突破
| 来源 | URL | 格式 | 可靠性 | 备注 |
|------|-----|------|--------|------|
| HN RSS | `https://hnrss.org/frontpage?points=30` | RSS XML | ⭐⭐⭐⭐⭐ | 首选，稳定可靠 |
| HN Algolia | `https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=20&numericFilters=points>30` | JSON | ⭐⭐⭐⭐⭐ | 结构化查询，支持过滤 |
| GitHub | 跳过或通过搜索API | - | ⭐⭐ | 搜索API有速率限制 |

### 维度三：AI 与社会
| 来源 | URL | 格式 | 可靠性 | 备注 |
|------|-----|------|--------|------|
| EFF | `https://www.eff.org/deeplinks/` | HTML | ⭐⭐⭐⭐⭐ | 隐私/AI政策/数字权利 |
| Aeon | `https://www.aeon.co/` | HTML | ⭐⭐⭐⭐ | AI与社会交叉话题 |

### 维度四：哲学与自我进化
| 来源 | URL | 格式 | 可靠性 | 备注 |
|------|-----|------|--------|------|
| Aeon | `https://www.aeon.co/essays` | HTML | ⭐⭐⭐⭐⭐ | 高质量长文 |
| Aeon Computing & AI | `https://www.aeon.co/essays?topic=14` | HTML | ⭐⭐⭐⭐ | 直接 AI 哲学 |
| LessWrong | `https://www.lesswrong.com/` | HTML | ⭐⭐ | Vercel 安全拦截，经常失败 |

## 失败模式记录
- **The Verge** (`https://www.theverge.com/ai-artificial-intelligence`) — browser_navigate 超时
- **MIT TR** (`https://www.technologyreview.com/topic/artificial-intelligence/`) — browser_navigate 超时
- **OpenAI Blog** — Cloudflare 安全验证拦截
- **Reuters** — browser_navigate 超时
- **LessWrong** — Vercel Security Checkpoint 拦截
- **HN Algolia /best** — 502 Bad Gateway（不稳定）
