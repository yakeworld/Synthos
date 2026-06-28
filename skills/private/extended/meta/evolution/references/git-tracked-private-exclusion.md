# Git Tracked Exclusion for Private/ — Cycle 184

## 问题

diagnose.py 计算 structural 时：
```
gp = git_tracked / total_skills
```

但 `total_skills = 191` 包含 private 目录（86 个技能），
而 private 被 `.gitignore` 的 `/skills/private/` 行有意排除（含凭证）。

git tracked 显示 105/191 = 55%，实际上 public-only 是 105/105 = 100%。

## 修复

```python
# 排除 private/ 路径
git_tracked = len([l for l in r.stdout.split('\n') if 'SKILL.md' in l and '/private/' not in l])

# public-only 分母
total_public = git_tracked + untracked_public
gp = git_tracked / total_public if total_public else 0
```

## 影响

- structural 从 0.8874 → 1.0000
- overall 从 0.9513 → 0.9795
- private 技能不再拖累 structural 评分

## 规则

private/ 目录中的技能始终不被 git tracked（含凭证）。
diagnose.py 的所有 git 相关计算都应排除 private/ 路径。
