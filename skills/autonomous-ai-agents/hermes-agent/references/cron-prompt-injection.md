# Cron Job Prompt Injection Scanner

> 2026-05-25 实战记录：`autonomous-core-researcher` cron job 被注入扫描器反复封杀

## 问题现象

Cron job 创建后无法执行，错误日志：

```
cron.scheduler: Cron job 'autonomous-core-researcher': assembled prompt blocked by injection scanner
  — Blocked: prompt contains invisible unicode U+200B (possible injection).
cron.scheduler: Job 'autonomous-core-researcher' (ID: b46ac11d0a9f): blocked by prompt-injection scanner
```

## 根因

有两种来源会导致「assembled prompt」被拦截：

### 来源A：Cron prompt 本身含有 U+200B

Cron prompt 中含有 **U+200B (零宽空格, Zero-Width Space)**，这是种不可见的 Unicode 字符。来源：

- 从飞书/Feishu 对话中复制粘贴 prompt 时，格式处理可能插入零宽空格
- 中英文混排时编辑器自动插入的格式字符
- Markdown 的 `---` 分隔线、中文引号、长破折号附近的零宽间距字符

### 来源B：Cron 加载的 Skill 文件中含有 U+200B（2026-05-25 实战）

这是更隐蔽的根因。即使 cron prompt 是纯 ASCII，如果 cron 加载的 **任何一个 SKILL.md 文件中**含有 U+200B，组装后的完整 prompt 也会被拦截。

2026-05-25 实战：`post-compile-dual-quality-check/SKILL.md` 第226行的「Te​X」一词中，字母 T 和 e 之间藏着一个 U+200B：

```
Line 226: char U+200B (ZERO WIDTH SPACE) at pos 5874
  原文: "若Te​X源中的正确拼写存在..."
```

当 cron 加载这个 skill 时，系统将 cron prompt + 所有 skill 内容拼接为「assembled prompt」，扫描器检测到 U+200B 后直接拦截。

**诊断方法：扫描所有加载的 skill 文件，而非仅检查 cron prompt 本身：**

```bash
python3 -c "
import os
invisible = {0x200b: 'U+200B', 0x200c: 'U+200C', 0x200d: 'U+200D', 0xfeff: 'BOM'}
for root, dirs, files in os.walk(os.path.expanduser('~/.hermes/skills')):
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            with open(path, 'rb') as fh:
                content = fh.read()
            for i, b in enumerate(content):
                if b == 0xe2 and i+2 < len(content) and content[i+1] == 0x80 and content[i+2] in [0x8b, 0x8c, 0x8d, 0x8e]:
                    code = f'U+{content[i+1]:02x}{content[i+2]:02x}'
                    # 找到对应行号
                    text = content.decode('utf-8', errors='replace')
                    line_num = text[:i].count(chr(10)) + 1
                    print(f'{path}:{line_num} - {code}')
            if content.count(b'\\xe2\\x80\\x8b') > 0:
                text = content.decode('utf-8', errors='replace')
                print(f'{path}: {content.count(bchr(0xe2)+chr(0x80)+chr(0x8b))} occurrences of U+200B')
"
```

或者用 od/xxd：

```bash
# 检查所有 skill 文件的 SKILL.md
find ~/.hermes/skills -name 'SKILL.md' -exec sh -c 'xxd "$1" | grep -q "200b" && echo "FOUND: $1"' _ {} \;
```

**修复：**

```bash
python3 -c "
import os
for root, dirs, files in os.walk(os.path.expanduser('~/.hermes/skills')):
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            cleaned = content.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '').replace('\ufeff', '')
            if cleaned != content:
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(cleaned)
                print(f'Fixed: {path}')
"
```

## 检测

```bash
# 方法1: od 查看原始字节
xxd /path/to/cron_prompt.txt | grep -i '200b'
# 无输出表示无该字符

# 方法2: Python 检测
python3 -c "
with open('/path/to/cron_prompt.txt') as f:
    content = f.read()
invisible = [hex(ord(c)) for c in content if ord(c) in [0x200b, 0x200c, 0x200d, 0xfeff, 0x2060, 0x2061, 0x2062, 0x2063, 0x2064]]
print(f'Invisible chars: {invisible}' if invisible else 'CLEAN')
"
```

## 修复步骤

1. **重写 prompt**：用纯 ASCII 字符编写，避免任何特殊 Unicode。中文可以正常使用标准 CJK 字符，但避免零宽字符。
   - 不要使用 `---` 分隔线（易混入格式字符）
   - 不要从富文本编辑器中复制粘贴
   - 先用文本编辑器写入纯文本文件

2. **写入文件并验证**：
   ```bash
   cat > /tmp/prompt.txt << 'EOF'
   纯 ASCII prompt 内容
   EOF
   xxd /tmp/prompt.txt | grep -i '200b' || echo 'CLEAN'
   ```

3. **从文件创建 cron**：
   ```bash
   cat /tmp/prompt.txt | hermes cron create '*/10 * * * *' \
     --name job-name \
     --skill skill1 --skill skill2 \
     --deliver origin
   ```

4. **验证运行**：
   ```bash
   hermes cron list | grep -A6 'job-name'
   # 检查 Repeat: ∞, 有 next_run_at
   ```

## 预防

- 使用 cronjob 工具创建时，prompt 参数必须手动输入纯 ASCII，不要从 markdown 渲染结果中复制
- 首次创建后先 `hermes cron run <id>` 测试，不要等自动调度发现失败
- 2026-05-25 实战：第一版 prompt 通过 `cronjob` 工具 API 创建时参数中的中文标点可能被序列化为 Unicode 转义序列，在反序列化时混入不可见字符。**安全做法**是写入文件 → `cat file | hermes cron create`。
