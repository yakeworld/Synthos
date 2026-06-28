# Docker systemd proxy 陷阱

## 症状

`docker pull` 或 `docker compose pull` 超时：
```
Error response from daemon: Get "https://registry-1.docker.io/v2/":
net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
```

或连接被重置：
```
proxyconnect tcp: dial tcp 172.18.0.12:1080: i/o timeout
```

## 根因

Docker daemon 被 systemd 配置了 HTTP/HTTPS 代理，指向一个可能已下线或网络不通的 shadowsocks 容器：

```
# /etc/systemd/system/docker.service.d/proxy.conf
[Service]
Environment="HTTP_PROXY=socks5://172.18.0.12:1080/"
Environment="HTTPS_PROXY=socks5://172.18.0.12:1080/"
Environment="NO_PROXY=localhost,127.0.0.1"
```

`172.18.0.12` 通常是 docker-compose 创建的 bridge 网络内的 shadowsocks 容器 IP（非 docker0 的 `172.17.0.1`）。

## 诊断

```bash
# 检查 Docker systemd env
systemctl show docker.service --property=Environment

# 检查 drop-in 配置
cat /etc/systemd/system/docker.service.d/proxy.conf

# 检查代理是否真的可达
curl -x socks5://172.18.0.12:1080 -s https://hub.docker.com -o /dev/null -w '%{http_code}'
```

## 修复

```bash
# 删除 proxy override
sudo rm /etc/systemd/system/docker.service.d/proxy.conf
sudo systemctl daemon-reload

# 如需镜像加速器，修改 daemon.json（不是 override）
sudo bash -c 'cat > /etc/docker/daemon.json << "EOF"
{
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    },
    "registry-mirrors": ["https://docker.1ms.run"]
}
EOF'

# 重启 Docker
sudo systemctl restart docker

# 验证
docker info --format '{{json .RegistryMirrors}}'
```

## 注意事项

- 删除 proxy.conf 后，Docker daemon 恢复直连互联网
- 如果服务器在 Tailscale exit node 且需要代理才能上网，需重新配置 proxy.conf，但目标 IP 应为真实可用的代理（非已下线的容器）
- Tailscale exit node 可能无法直连 Docker Hub，此时镜像加速器是必需项
