# 技能目录全面审计方法论

> 系统性审计 skill 目录完整性和一致性的检查清单。每次发现断裂、重复、或质量门不通过时执行。

## 审计范围

| 目录 | 路径 | 说明 |
|------|------|------|
| 权威源 | /media/yakeworld/sda2/Synthos/skills | Synthos 核心技能，217个 |
| Hermes扩展 | ~/.hermes/skills | Hermes 独有扩展，32个 |

## 检查清单

### C1. 文件完整性

对每个技能目录：
- [ ] 有 SKILL.md（顶层或子技能）
- [ ] 类级别技能有 BOUNDARY.md + IO_CONTRACT.md + EVIDENCE_SCHEMA.md
- [ ] 类级别技能有 golden/ CHANGE_LOG.md references/
- [ ] 父级目录有 SKILL.md（作为子技能索引，23个曾缺失）

### C2. 命名冲突

- [ ] 检查同名技能在不同目录的存在
- [ ] 对重复技能比较内容是否一致
- [ ] 不一致的优先修复（AMBIGUOUS 错误直接阻断加载）

### C3. 嵌套层级

- [ ] 统计各层级技能数量（层级0=顶层, 1=分类下, 2=子技能）
- [ ] 检查二层子技能的父级是否有 SKILL.md 索引
- [ ] mlops 系列13个二层子技能曾全部缺失父级SKILL.md

### C4. Cron 依赖

- [ ] 列出所有 cron job（~/.hermes/cron/*.json）
- [ ] 检查每个 job 的 skills 字段
- [ ] 对每个引用的 skill 检查是否存在
- [ ] 检查 script 模式 job 的脚本文件是否存在

### C5. 结构质量评分

对每个类级别技能检查：
- BOUNDARY 存在 = 1分
- IO_CONTRACT 存在 = 1分
- EVIDENCE_SCHEMA 存在 = 1分
- golden/ 存在 = 1分
- CHANGE_LOG 存在 = 1分
- references/ 存在 = 1分
- 原理层（文言）在 SKILL.md 中 = 1分
- 子技能/引用说明在 SKILL.md 中 = 1分
- 满分8分，≥7分为优秀，<4分为缺失

### C6. 路径同步

- [ ] 确认权威源（sda2）与镜像（~/.hermes/skills）的 inode 关系
- [ ] 检查同名技能内容是否同步一致
- [ ] 检查仅在一个目录存在的技能是否需要双向同步

## 审计输出

```
=== 技能目录审计结果 ===
总技能: XXX
- 层级0(顶层): XX
- 层级1(分类下): XX  
- 层级2(子技能): XX

重复命名: N个
- name: [path1, path2] [内容一致/不一致]

缺失结构: N个
- name: 缺失 [BOUNDARY/IO_CONTRACT/...]

父级SKILL.md缺失: N个
- parent/

Cron依赖问题: N个
- job_name: [missing_skill1, ...]

质量分布:
- 优秀(≥77.8%): N个
- 中等(44.4-77.8%): N个
- 缺失(<44.4%): N个

修复优先级:
P0: [最高优先级修复]
P1: [本周修复]
P2: [持续优化]
```

## 自动化脚本模板

```python
#!/usr/bin/env python3
"""技能目录审计脚本 - 可重运行"""
import os, json, sys

SKILLS_DIR = "/media/yakeworld/sda2/Synthos/skills"
HERMES_DIR = "/home/yakeworld/.hermes/skills"
CRON_DIR = "/home/yakeworld/.hermes/cron"

class_indicators = ['BOUNDARY.md', 'IO_CONTRACT.md', 'EVIDENCE_SCHEMA.md', 
                    'golden', 'CHANGE_LOG.md', 'references']

def count_skill_dirs(base):
    count = 0
    for root, dirs, files in os.walk(base):
        if 'SKILL.md' in files:
            count += 1
    return count

def check_duplicates(base_dirs):
    name_to_paths = {}
    for base in base_dirs:
        for root, dirs, files in os.walk(base):
            if 'SKILL.md' in files:
                name = os.path.basename(root)
                name_to_paths.setdefault(name, []).append(
                    os.path.relpath(root, base))
    return {n: p for n, p in name_to_paths.items() if len(p) > 1}

def check_cron_deps():
    issues = []
    for f in os.listdir(CRON_DIR):
        if not f.endswith('.json') or f in ['jobs.json']:
            continue
        try:
            with open(os.path.join(CRON_DIR, f)) as fh:
                job = json.load(fh)
            for s in job.get('skills', []):
                exists = (os.path.exists(os.path.join(SKILLS_DIR, s, "SKILL.md")) or
                          os.path.exists(os.path.join(HERMES_DIR, s, "SKILL.md")))
                if not exists:
                    issues.append((f, s))
        except:
            pass
    return issues

if __name__ == '__main__':
    print(f"权威源: {count_skill_dirs(SKILLS_DIR)} 个技能")
    print(f"Hermes: {count_skill_dirs(HERMES_DIR)} 个技能")
    dupes = check_duplicates([SKILLS_DIR, HERMES_DIR])
    if dupes:
        print(f"\n重复命名({len(dupes)}):")
        for n, p in dupes.items():
            print(f"  {n}: {p}")
    cron = check_cron_deps()
    if cron:
        print(f"\nCron依赖问题({len(cron)}):")
        for j, s in cron:
            print(f"  {j}: {s}")
```

## 常见陷阱

1. **嵌套cp陷阱**: `cp -r src/ skill/ dest/` 当 dest/skill/ 已存在时创建 skill/skill/。修复：先 rm -rf 再 cp -r。
2. **inode混淆**: /home/yakeworld/Synthos 是 /media/.../Synthos 的符号链接，同inode。审计时只扫描一个路径即可。
3. **AMBIGUOUS错误**: 同名技能存在于不同目录时，skill_view 直接拒绝加载。修复：删除冗余，保留一个权威版本。
4. **状态文件陈旧**: cron JSON 状态含已删除目录条目导致 KeyError。用 .get() 或清除状态文件。
5. **rclone超时**: rclone check 超过120s，直接 rclone sync。