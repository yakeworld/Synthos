# GOLDEN_SET.md — feishu-gateway-debug

> 对应原则：P2（机械原子：error_msg + session_id + platform → diagnosis 根因 + 修复建议）
> golden_set_origin: self_defined

## 设计依据

本技能输入为 `(error_msg, session_id, platform)`，输出为诊断结论（根因 + 修复建议）。
金标准为自设（self_defined），验证目标：**给定相同的错误与日志线索，技能能否正确区分
错误来源（vLLM / DeepSeek / 飞书 API，FEIS-001）、按时间线定位消息流断点（FEIS-002）、
在错误路径上给出正确的根因与可执行修复（FEIS-003/004/007），且结论可追溯至具体日志行
（不编造数据）**。

判定规则（expected 以 `checks` 键给出逐条布尔判定）：
- 来源判定必须基于 `base_url`（404 不得误判为飞书问题，FEIS-001）
- 断点定位必须给出 Gateway 时间线中具体的缺失环节（FEIS-002）
- 每条 diagnosis 必须含 evidence（日志行/命令输出）与 repair（可执行动作）
- MEDIA 附件未收到类 case 必须先路径验证 + 大小检查 + gs 压缩（FEIS-004/005）

## 测试用例表

| case | 名称 | 类型 | 输入摘要 | 期望要点 | 关联 Genes |
|------|------|------|----------|----------|-----------|
| case_001 | vLLM 404 误报为飞书错误 | 正常 | session=feishu:dm，API call failed 404，agent.log base_url=http://192.168.64.21:8000/v1 | 来源=vLLM 节点（非飞书）；/v1/models 确认模型存在；重发后时间线完整 | FEIS-001/002/003 |
| case_002 | MEDIA 附件 33MB 超限静默失败 | 错误 | 用户发 PDF 后未收到附件、无报错，文件 33MB | 根因=文件 >10MB；先 ls -la 验证路径、避开 /tmp；gs /screen 压缩至 ~2.4MB 重发 | FEIS-004/005 |
| case_003 | Stream 断开 180s 超时 | 错误 | RemoteProtocolError, http_status=200 bytes=0 elapsed=180.07s | 根因=vLLM 节点 180s 超时/负载过高；检查节点状态或调整超时配置 | FEIS-007 |

## 通过标准

- **pass_threshold: 0.80**（3 个 case 至少 2 个通过）
- case_001：来源判定正确（vLLM 非飞书）+ 修复动作含 `/v1/models` 验证 + 时间线断点定位
- case_002：路径验证优先（ls -la）+ 10MB 超限判定 + gs 压缩修复，顺序不可颠倒
- case_003：180s 超时判定命中 vLLM 节点问题，未误判为飞书网关
- 权重区分：case_001 为 critical（主路径），case_002/003 为 high（错误路径）
- 所有 diagnosis 必须含 evidence 字段（可追溯至日志行或命令输出），无 evidence 即判失败（P0）

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-27 | 初始自设金标准，3 个 case（1 正常 + 2 错误） | Synthos Agent |
