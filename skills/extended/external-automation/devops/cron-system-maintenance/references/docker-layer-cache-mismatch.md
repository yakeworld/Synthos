# Docker 镜像层缓存不一致陷阱

## 现象

两台服务器拉取相同的 Docker 镜像 `vllm/vllm-openai:latest`，
镜像 digest 完全相同 (`sha256:f37691f675bb...`)，
但容器内的 Python 包版本不同。

### 实际案例

- Tailscale 节点 (100.82.27.51): vLLM **0.23.0**, torch 2.11.0, flashinfer 0.6.12
- work1 (100.125.10.93): vLLM **0.19.1**, torch 2.10.0, flashinfer 0.6.6

`docker images` 和 `docker inspect` 都显示相同 image ID，
但 `docker exec` 进容器后 `pip3 show vllm` 版本不同。

## 根因

`docker inspect` 只检查顶层层（ENTRYPOINT 层），
但容器运行时使用整个层叠加。
中间层（包含 Python 包的层）被旧缓存覆盖。

## 验证

```bash
docker exec <container> stat /usr/local/lib/python3.12/dist-packages/vllm/__init__.py
# 正常版本: Modify: 2026-06-12 23:22:53
# 旧版本缓存: Modify: 2026-04-18 01:20:09
```

## 修复

```bash
docker stop <container> && docker rm <container>
docker rmi vllm/vllm-openai:latest
docker pull vllm/vllm-openai:latest
# 重新启动容器
```

## 预防

1. 始终通过 `docker exec` 进入容器验证版本，而非仅看 `docker images`
2. 生产环境用固定版本号标签（如 `:v0.23.0`）而非 `:latest`
3. 多节点部署时，定期统一 `docker pull` 刷新缓存
