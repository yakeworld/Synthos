# OpenML API Endpoints (2026-06-20 验证有效)

## 基础端点

```
https://www.openml.org/api/v1/json/
```

## 数据集查询

```bash
# 获取数据集描述
curl -s 'https://www.openml.org/api/v1/json/data/37'

# 搜索数据集
curl -s 'https://www.openml.org/api/v1/json/data/search/data_name/diabetes'
```

## 任务查询

```bash
# 获取某数据集上的任务列表（注意参数是 data_id）
curl -s 'https://www.openml.org/api/v1/json/task/list/data_id/37/status/active'
```

**关键参数名**：`task`（不是 `task_id`），`data_id`

## 运行（Run）查询

```bash
# 获取某任务上的所有运行
curl -s 'https://www.openml.org/api/v1/json/run/list/task/37/limit/500'

# 获取单个运行详情（含性能指标）
curl -s 'https://www.openml.org/api/v1/json/run/175875'
```

**关键发现**：
- `run.predictive_accuracy` 返回 None
- 性能指标在 `run.output_data.evaluation[]` 数组中
- value 是字符串类型，需 `float()` 转换

## 评估指标

| 指标名 | 含义 |
|--------|------|
| `predictive_accuracy` | 准确率 |
| `f_measure` | F1 Score |
| `area_under_roc_curve` | AUC |
| `recall` | 召回率 |
| `precision` | 精确率 |
