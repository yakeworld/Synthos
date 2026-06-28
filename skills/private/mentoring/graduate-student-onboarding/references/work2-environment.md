# Work2 工作站环境

## Server Info
- Hostname: work2 (amax-servcer2)
- IP: 100.100.252.99
- OS: Ubuntu 26.04 LTS
- Python: 3.14.4
- Disk: /dev/sdb1 (3.6T, ~3.4T free) at /mnt/data

## User Accounts (2026-06-22)
| Username | Name | UID | Notes |
|:---------|:-----|:----|:------|
| yakeworld | 杨晓凯 | 1000 | sudo, primary |
| shaoqiqi | 邵奇奇 | 1001 | student |
| yangqiancheng | 杨前程 | 1002 | student |
| guozihao | 郭梓豪 | 1003 | student |

## Standard Setup
```bash
# Create new user
sudo useradd -m -s /bin/bash -c '姓名' 用户名
sudo passwd 用户名

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv with scientific stack
uv venv ~/workspace/eye-tracking/.venv
uv pip install numpy scipy opencv-python matplotlib pandas jupyter scikit-learn
```
