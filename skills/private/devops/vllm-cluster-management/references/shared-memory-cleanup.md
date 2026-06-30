# vLLM 容器共享内存清理指南

## 问题现象

vLLM 容器（35B+ 模型，TP≥2）异常退出后，`/dev/shm` 中残留 `psm_*` 和 `sem.mp-*` 文件，新容器启动时报错：

```
RuntimeError: Engine core initialization failed
There appear to be N leaked shared_memory objects to clean up at shutdown
```

## 诊断

```bash
# 1. 查看共享内存残留
ls -la /dev/shm/
# 典型输出：
# psm_792e620a   (160MB - EngineCore 通信)
# psm_8973b85a   (252MB - GPU 内存映射)
# sem.mp-xxx     (信号量)

# 2. 查看 ipcs
ipcs -m
# 如果有 psm/sem 条目，说明有残留

# 3. 查看容器状态
docker ps -a --filter name=vllm --format '{{.Names}} {{.Status}}'
# 如果看到频繁 restart，说明在循环重启

# 4. 查看日志确认
docker logs vllm-qwen3-nvfp4 --tail 20
# 看到 "leaked shared_memory" + "Engine core initialization failed"
```

## 清理方法

### 方法 1：ipcrm（需要 root）

```bash
# 查看共享内存 ID
ipcs -m | grep -E 'psm_|sem.mp'

# 清理共享内存段
ipcrm -M <shmid>        # 按数字 ID 清理

# 清理信号量
ipcrm -s <semid>        # 按数字 ID 清理
```

### 方法 2：重启机器

如果无法获取 root 权限或 ipcrm 失败，重启机器即可彻底清理：

```bash
sudo reboot
```

### 方法 3：Docker 清理

```bash
# 停止并删除容器
docker stop vllm-qwen3-nvfp4
docker rm vllm-qwen3-nvfp4

# 重启后（仍需 ipcrm 清理残留）
docker run -d --shm-size 128g ...
```

## 预防措施

1. **启动时必须设置 `--shm-size 128g`**（或更大）
2. **不要使用 `--restart unless-stopped`** 策略——如果共享内存泄漏导致启动失败，容器会进入重启死循环
3. **清理后再重启**——旧容器退出了也要先清理 `/dev/shm`
4. **多用户共享的机器**——其他用户的容器也可能留下残留（如 `libpod_rootless_lock_*`），需要定期清理

## 实际案例

2026-06-29 100.125.10.93：
- 旧 4 卡 TP=4 容器异常退出，留下 `psm_95b62aa5` (160MB) 和 `sem.mp-*`
- 新 2 卡 TP=2 容器反复重启 12 次以上
- 排查发现 `psm_*` 文件属于 root 用户，yakeworld 用户无法删除
- 即使设置了 `--shm-size 128g` 也无法创建新段（旧段被 Docker 守护进程锁定）
- **关键教训**：Docker 的 `--shm-size` 参数只控制新容器分配的 shm，但不会清理旧的 `psm_*` 文件
- 最终节点完全不可达（SSH timeout + ping 100% loss），无法远程修复
- **故障蔓延**：100.125.10.93 从 shm 问题 → SSH 超时 → 完全不可达，需要从 provider 列表中移除

2026-06-27 首次发现（memory 已记录）：
- Docker restart `unless-stopped` 在 shm_broadcast.py 超时(60s) 后无限重启循环
- 部署 vLLM 容器不应使用 `restart` policy
