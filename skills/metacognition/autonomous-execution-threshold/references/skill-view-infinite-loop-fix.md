# Skill View Safety Incident — 2026-06-12

## 事故描述

agent 对 skills_list 返回结果外的技能名发起 skill_view 调用，进入无限循环。280+次连续失败，远超10次安全上限。

## 根因

1. 幻觉模式生成：LLM在模式驱动下持续生成不存在的技能名
2. 缺少实时检测：连续失败检测延迟
3. 名称域验证缺失：未验证请求名是否在skills_list返回的已知集合内

## 缓解措施

已在SKILL.md中更新的规则：
- 连续失败>=5次时必须检查skills_list确认有效性
- 连续失败>=10次必须完全停止
- 禁止对skills_list返回名之外的技能名发起skill_view
- 同一命名模式连续失败>=3次即停止

## 建议的系统级改进

1. agent框架层面硬编码10次上限
2. skill_view失败时自动检查skills_list
3. 命名模式探测：连续3次同一模式失败即终止
4. 监控工具调用序列检测重复失败模式

## 清理清单

1. 修复7个dangling symlink（指向sda2已删除的skill）
2. 清理usage.json中34个孤儿条目
3. 清理3个空目录
4. 清理嵌套重复目录