# Credential → Environment Variable Audit

> 记录 Synthos 工具代码库中凭证硬编码的清理情况，供后续审计延续。

## 目标

所有 API 凭证、数据库密码、SSO 账号不得硬编码在源代码中。必须通过环境变量注入。

## 本轮清理（2026-05-31）

### 清理文件

| 文件 | 硬编码内容 | 改为 | 状态 |
|:-----|:-----------|:-----|:------|
| `tools/paper-manager/batch_refresh.sh` | `export MEDDATA_USERNAME/PASSWORD` | 移除 export，加缺失告警 | ✅ |
| `tools/paper-manager/batch_meddata_all.py` | `ENV["MEDDATA_USERNAME"] = "<MEDDATA_USERNAME>"` | `os.environ.copy()` + 缺失检查 | ✅ |
| `tools/paper-manager/batch_enhance_all.py` | 同上 | 同上 | ✅ |
| `tools/paper-manager/auto_fix_d8.py` | 同上 | 同上 | ✅ |

### 底层未动

`src/sources/meddata.py` 已经正确读取环境变量 `MEDDATA_USERNAME` / `MEDDATA_PASSWORD` / `MEDDATA_TOKEN`，无需改动。

## 环境变量清单

| 变量 | 用途 | 值 | 设置位置 |
|:-----|:-----|:---|:---------|
| `MEDDATA_USERNAME` | meddata SSO 账号 | `<MEDDATA_USERNAME>` | ~/.bashrc 或等效 |
| `MEDDATA_PASSWORD` | meddata SSO 密码 | `<MEDDATA_PASSWORD>` | ~/.bashrc 或等效 |
| `GITHUB_TOKEN` | GitHub API | (已设置) | ~/.bashrc |
| `SEMANTIC_SCHOLAR_API_KEY` | SS API | (已设置) | ~/.bashrc |

## 审计方法

对 Synthos 工具目录的全量硬编码检测：

```bash
cd /media/yakeworld/sda2/Synthos/tools
# 搜索常见的硬编码模式
grep -rn "export.*USERNAME\|export.*PASSWORD\|ENV\[\"MEDDATA" --include="*.sh" --include="*.py" .
# 也可搜具体值
grep -rn "<MEDDATA_USERNAME>\|<MEDDATA_PASSWORD>" --include="*.sh" --include="*.py" --include="*.json" .
```

## 续审指引

下次清理时从以下优先级开始：

| 优先级 | 检查范围 | 方法 |
|:------:|:---------|:-----|
| P0 | 所有 `.py` 中 `ENV["..."] = "..."` 赋值 | `grep -rn 'ENV\["'` |
| P0 | 所有 `.sh` 中 `export.*TOKEN\|export.*PASSWORD\|export.*SECRET` | `grep -rn 'export.*\(TOKEN\|PASSWORD\|SECRET\|API_KEY\)'` |
| P1 | 配置文件 `.env`, `.json`, `.yaml` 中的明文秘密 | `find . -name '*.json' -exec grep -l 'password\|secret\|token' {} +` |
| P1 | CI/CD 脚本中硬编码的 curl token | 人工审查 deploy/test 脚本 |
