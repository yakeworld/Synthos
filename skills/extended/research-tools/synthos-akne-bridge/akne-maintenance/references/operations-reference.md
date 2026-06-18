# AKNE 运维操作速查 — 2026-06-10 修复后

## 日常运维

### 1. 健康检查
```bash
python3 akne/scripts/akne-optimize.py diagnose
```
检查: 连通性 > 95%, 源文件覆盖率 100%, Wiki 污染 0, 向量 > 200, Synthos 论文孤立 < 10%

### 2. 修复
```bash
python3 akne/scripts/akne-optimize.py fix     # 统一边格式+去重+填充源文件+修复孤立论文
python3 akne/scripts/synthos-akne-bridge-v2.py sync  # 增量同步 Synthos
python3 akne/scripts/akne-optimize.py diagnose  # 再次确认
```

### 3. 守护进程
```bash
# 启动
cd akne && bash scripts/auto_evolve.sh
# 状态
cat logs/auto_evolve.pid
tail -20 logs/auto_evolve.log
# 停止
kill $(cat logs/auto_evolve.pid) 2>/dev/null; rm logs/auto_evolve.pid
```

## 常见问题速查

| 症状 | 原因 | 修复 |
|------|------|------|
| 图谱孤立节点 > 10% | 桥接失败或未运行 | run `bridge-v2.py sync` |
| Wiki 有 `[X]::` 垃圾 | LLM 摄入污染 | grep 正则删除 |
| 守护进程不运行 | PID 文件丢失或进程死 | pkill + nohup 重启 |
| 论文没有 01-manuscript | 目录不规范 | fix_bridge.py 扫描归入子目录 |
| 边格式不一致 | `relation` vs `link_type` | `akne-optimize.py fix` |
| 向量记录少 | GPU模型未加载 | 仅需结构填充，实际嵌入需GPU |
