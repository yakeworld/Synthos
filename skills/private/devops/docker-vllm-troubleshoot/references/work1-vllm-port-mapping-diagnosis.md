# work1 vLLM 端口映射404问题诊断记录

## 时间
2026-06-19

## 症状
- Docker容器 `vllm-qwen3-nvfp4` 状态 Up 46分钟
- 容器内 `curl localhost:8000/ping` → 200 OK (空body) ✓
- 容器内 `curl localhost:8000/v1/models` → 200 OK (返回模型列表) ✓
- 宿主机 `curl localhost:8000/ping` → 404 "Not found" ✗
- 宿主机 `curl 172.17.0.2:8000/ping` → 404 "Not found" ✗

## 环境信息
- 主机: work1
- 容器: vllm-qwen3-nvfp4, vllm/vllm-openai:latest (v0.23.0)
- GPU: RTX 3090 (sm_89)
- Docker: 29.5.3
- docker0 MTU: 1300 (异常值，标准1500)
- /etc/docker/daemon.json: 设置了 mtu: 1300

## 容器内端口监听
```
/proc/net/tcp 第33行: 00000000:1F40 → 0.0.0.0:8000 (LISTEN)
```
只有一个进程（PID 1, vLLM serve）监听 8000。

## 对比 work3
- work3 的 `/ping` → 200 OK (空body) 正常
- work3 的 `/v1/models` → 200 OK (返回模型列表) 正常
- work3 的 curl localhost 和 curl 容器IP 都正常

## 根本原因推测
Docker NAT端口映射异常。具体可能原因：
1. `/etc/docker/daemon.json` 中 MTU=1300 导致网络异常
2. Portainer 容器内部占用 8000/tcp（Agent端口），与 vLLM 端口映射冲突
3. iptables NAT表被破坏（无root权限无法验证）

## 影响
- 所有外部请求到 work1:8000 返回 404
- 本机通过 Tailscale 无法调用 work1 vLLM
- 容器内进程正常工作但不被外部访问

## 修复方案
1. 将 daemon.json 中的 mtu 1300 改回 1500 或移除
2. 给 vLLM 换到非冲突端口（如 8060）
3. 确保 Portainer 不占用 8000 内部端口
4. 重启 Docker 服务使 MTU 生效

## 状态
诊断完成，等待用户确认修复。
