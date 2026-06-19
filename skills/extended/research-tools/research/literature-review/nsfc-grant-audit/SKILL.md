---



name: nsfc-grant-audit
description: "Directory index for nsfc-grant-audit: nsfc-grant-audit"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "grant_proposal: dict, guidelines: dict -> audit_report: dict (compliance_score, gaps, suggestions, risk_areas)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `grant_proposal: str` — 用户请求描述、上下文信息
- **output**: `audit_report: dict — NSFC基金审计`


> 对应原则：P2（机械原子暴露输入输出规范）

# Nsfc Grant Audit

主skill | 国自然/省科技厅/市科技局三级课题评审编排器。九维评审矩阵。
