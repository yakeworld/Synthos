# 郭梓豪入组配置记录 (2026-06-22)

**学生**: 郭梓豪  
**背景**: 温州医科大学科研型硕士，医学背景  
**工作站**: work2 (100.100.252.99)  
**初始密码**: kyzxgzh  

## 配置内容

### 目录结构
```
~/workspace/eye-tracking/     — 主项目 + Python venv
~/workspace/papers/           — 论文相关
~/workspace/skills/           — Synthos技能学习
~/projects/3d-eye-tracking/   — 代码仓库（待配SSH key后克隆）
~/data/raw/                   — 原始数据
~/data/results/               — 分析结果
~/data/datasets/              — 公开数据集
~/scripts/                    — 脚本
```

### 软件环境
- **Python**: 3.14.4
- **uv**: 0.11.23
- **venv**: ~/workspace/eye-tracking/.venv/
- **核心库**: numpy 2.5.0, opencv 4.13.0, matplotlib 3.11.0, pandas 3.0.3, scipy, scikit-learn, jupyter
- **Node.js**: v24.17.0
- **Codex CLI**: v0.141.0
- **git**: user.name="Guo Zihao", user.email="guozihao@wmu.edu.cn"

### Codex 配置
```toml
model = "qwen3.6-35b-nvfp4"
model_provider = "vllm"
base_url = "http://localhost:8000/v1"
VLLM_API_KEY = any dummy (local, no auth needed)
```

### 未完成（学生自行配置）
- [ ] GitHub SSH Key (`ssh-keygen -t ed25519` → add to GitHub)
- [ ] 克隆私有仓库到 ~/projects/3d-eye-tracking/
- [ ] 修改初始密码 (`passwd`)

### 培养方案
文件: `~/workspace/三维眼动分析研究生培养方案.md`

**第一篇论文建议**: 3D Kappa角在健康中国人群中的分布特征
- 数据来源: 科室自有眼动采集设备
- 样本量: 50-80例
- 预计周期: 8周
