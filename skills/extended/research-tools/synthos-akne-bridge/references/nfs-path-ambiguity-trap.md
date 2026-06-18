# NFS 路径混淆陷阱

## 问题

`/mnt/nfs/` 下有与主仓库同名的子目录，但内容不完整，是 NFS 共享副本/工作缓存。

## 陷阱

```
/mnt/nfs/Synthos/       ← NFS 副本（仅66项内容，evolution-state.json 非最新）
/media/yakeworld/sda2/Synthos/ ← 主仓库（8192项，完整121技能+43篇论文）
~/Synthos/              ← symlink 副本，与主仓库一致
```

## 识别方法

| 路径 | 目录项数 | evolution-state.json 日期 | 内容完整度 |
|------|---------|------------------------|-----------|
| `/media/yakeworld/sda2/Synthos/` | 8,192 | 最新 | 完整 |
| `/mnt/nfs/Synthos/` | 66 | 5月29日 | 残缺（无AGENTS.md, 无完整skills/） |
| `~/Synthos/` | 8,192 | 最新 | 完整（symlink） |

## 判断规则

- 检查目录项数：完整 repo ≥ 8000，NFS 副本 ≤ 100
- 检查是否有 `AGENTS.md`、`CONSTITUTION.md`：副本中缺失
- 检查 `evolution-state.json` 日期：副本通常落后数天
- 检查 `skills/` 目录：副本中技能目录结构不完整

## 其他 NFS 混淆案例

```
/mnt/nfs/synthos_data/   ← NFS 副本，非主仓库
/media/yakeworld/sda2/Synthos/  ← 真正的 Synthos
```

## 教训

分析 `/mnt/nfs/` 内容时，不能假设同名目录就是主仓库。必须通过结构完整性判断。`du` 和 `os.walk` 在 NFS 上响应极慢（>300s），使用 `timeout` 或 `ls` 快速命令。