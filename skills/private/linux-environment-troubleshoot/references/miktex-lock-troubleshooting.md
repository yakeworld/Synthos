# MiKTeX 锁文件诊断

## 症状

```
pdflatex: No space left on device: path="/home/yakeworld/.miktex/texmfs/data/miktex/data/le/"
pdflatex: Data: path="/home/yakeworld/.miktex/texmfs/data/miktex/data/le/"
```

但 `df -h` 显示有 82G 可用空间。

## 根因

MiKTeX 内部使用 kpathsea 文件系统抽象层。"No space left" 错误来自 kpathsea 的 `write_file()` 失败，可能的原因：

1. **锁文件 (`lock`) 存在但未释放** — MiKTeX 检测到锁文件后认为有另一个进程在使用数据目录，拒绝写入
2. **目录状态不一致** — `~/.miktex/texmfs/data/miktex/` 中的文件权限/所有者不一致
3. **MiKTeX 运行时损坏** — `.fmt` 文件部分写入导致后续读写失败

## 完整诊断流程

```bash
# Step 1: 确认不是真正的磁盘满
df -h /
df -h /home
# Step 2: 确认不是 inode 耗尽
df -i /
# Step 3: 检查锁文件
ls -la ~/.miktex/texmfs/data/miktex/lock
file ~/.miktex/texmfs/data/miktex/lock
# Step 4: 检查缓存目录状态
ls -la ~/.miktex/texmfs/data/miktex/
du -sh ~/.miktex/
# Step 5: 检查权限
ls -la ~/.miktex/
ls -la ~/.miktex/texmfs/
ls -la ~/.miktex/texmfs/data/miktex/
```

## 修复方案（按风险从低到高）

### 方案1：清除锁文件（推荐，风险最低）
```bash
rm -f ~/.miktex/texmfs/data/miktex/lock
```

### 方案2：清除锁文件 + 损坏日志
```bash
rm -f ~/.miktex/texmfs/data/miktex/lock
rm -f ~/.miktex/texmfs/data/miktex/log/*
```

### 方案3：重建整个 .miktex 缓存（风险中等）
```bash
# 备份配置文件（如果有自定义设置）
cp -r ~/.miktex ~/.miktex-backup
rm -rf ~/.miktex/
# 重新初始化
mpm --install=marticle
```

### 方案4：检查 MiKTeX 安装完整性
```bash
# 确认 pdflatex 指向正确的二进制
file $(which pdflatex)
readlink -f $(which pdflatex)
# 确认 .miktex 目录结构
find ~/.miktex/texmfs/data/miktex/ -maxdepth 1 -type d
```

## 验证

```bash
echo '\documentclass{article}\begin{document}Hello World\end{document}' > /tmp/test.tex
cd /tmp && pdflatex -interaction=nonstopmode test.tex 2>&1 | tail -5
```

期望输出包含：
```
Output written on test.pdf (1 page, XXXXX bytes).
Transcript written on test.log.
```
