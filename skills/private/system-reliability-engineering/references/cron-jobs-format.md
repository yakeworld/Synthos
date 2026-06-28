# Cron Jobs File Format

## 实际格式

`/home/yakeworld/.hermes/cron/jobs.json` 是 `{"jobs": [...]}` 格式，不是直接数组。

```python
with open('/home/yakeworld/.hermes/cron/jobs.json') as f:
    cron_data = json.loads(f.read())
cron_jobs = cron_data.get('jobs', [])
```

## 检查方法

```python
with open('/home/yakeworld/.hermes/cron/jobs.json') as f:
    cron_jobs = json.loads(f.read()).get('jobs', [])

error_jobs = [j for j in cron_jobs if j.get('last_status') == 'error']
```

## Cron日志目录

`/home/yakeworld/.hermes/cron/output/<job_id>/<date>_time.md`

- 每个job一个UUID目录，每个执行时间生成一个md文件
- 典型规模: 15个job, 2000+日志文件
- 检查error: grep `FAILED|timed out|Exception`

## Cron超时修复

- no_agent脚本默认120s超时
- 修复: 加`--quiet`、减`--stats`、加`--bwlimit`限速
- prompt开头加pre-flight探测

## 诊断参考

诊断报告在 `/media/yakeworld/sda2/Synthos/diagnostic-report-v2.json`，包含SRE各维度指标、critical issues和warnings。