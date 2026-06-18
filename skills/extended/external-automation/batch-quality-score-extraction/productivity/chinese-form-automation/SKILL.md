---
name: chinese-form-automation
description: >-
version: 1.0.0
  自动填写中文政府/教育/学术申请表 — docx+xlsx模板填充。
metadata:
  synthos:
    version: 1.1.0
    author: Synthos

---


# Chinese Form Automation

自动填写中文政府/教育/学术申请表 — docx+xlsx模板填充。

详细内容请加载对应 references/ 目录下的参考文件。

## Environment Pitfalls

- **python-docx sandbox**: In Hermes sandbox (Python 3.12), `pip install python-docx` requires `--break-system-packages` flag (PEP 668). Python 3.11 environments do NOT need this flag. Always check Python version before pip install. If sandbox fails, use `terminal` tool directly.
- **markitdown docx**: Also requires `markitdown[docx]` extra for .docx conversion. Prefer direct `python-docx` library for reliability.

## User Preference Pitfalls

- User explicitly prefers **特色介绍** (highlight-based feature showcase) over **平台架构** (platform architecture). When asked to introduce Synthos or research capabilities, focus on distinctive/unique capabilities, not comprehensive platform overview. Do NOT create PPT unless explicitly requested — document (docx) is the default format.
- For file sending: Feishu requires specific chat_id format `feishu:oc_<id>` for direct messages, not bare `feishu`.
- NJJK (神经网络科技/脑机接口) 摸底模板：科技局标准调查表，按框架逐项填写。收到模板文件后直接按框架填充，不额外创建 PPT。

## References

- `templates/njjk-survey-template.md` — NJJK 摸底调查框架模板及 Synthos 填充指南
- `references/competition-application-workflow-2026-05-30.md`
- `references/competition-data-source-audit-2026-05-30.md`
- `references/hangzhou-medical-college-industry-mentor-2026.md`
- `references/researcher-profiling-via-notebooklm.md`