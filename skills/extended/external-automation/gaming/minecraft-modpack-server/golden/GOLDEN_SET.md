---
name: minecraft-modpack-server
description: minecraft-modpack-server 金测集 — NeoForge/Forge Mod 包服务器配置/调优/备份决策的可执行测试
---

# 金测集: minecraft-modpack-server

> 来源: SKILL.md Golden 集合 + 验证清单（VERIFICATION 6 项）+ Genes (MINE-001~007) + EXAMPLES（3 个示例）。
> 本技能封装 Mod 包服务器（ATM10 等）从 zip 下载到启动验证的完整配置决策，
> 覆盖 NeoForge/Forge loader、JVM 调优、server.properties、防火墙、备份。
> 技能签名：`server_spec: str -> server_config: dict`；本 golden 集验证"输入 spec → 配置决策"的正确性。
> 每个 case 验证策略决策（loader 匹配 / 内存分配 / 认证配对 / 备份策略）的正确性（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路径：ATM10 4 人正版服务器（250+ mods） | MC 1.21+ → OpenJDK 21；`allow-flight=true` + `max-tick-time=180000`（MINE-002/003）；`online-mode=true` + `enforce-secure-profile=true`（配对一致）；4-6 人档 `view-distance=10`/`simulation-distance=6`；200-350+ mods → `-Xms12G -Xmx24G` + 系统留 ≥8GB 空闲（MINE-004）；`ufw allow 25565/tcp`；独立启动脚本引用 `user_jvm_args.txt`（MINE-006） |
| case_002 | 正常路径：局域网非正版模式（online-mode=false） | `online-mode=false` 必须同步 `enforce-secure-profile=false`（MINE-005，否则客户端被 rejected）；`allow-flight=true` 与 `max-tick-time=180000` 仍然保留（非正版不影响 modded 需求）；其余字段与正版路径一致 |
| case_003 | 错误路径：JVM 内存超额分配（300 mods 但主机仅 16GB RAM） | `-Xmx24G` 超过可用 RAM（扣除 ≥8GB 系统预留后可用 8GB），违反 MINE-004 → 必须拒绝并按 16GB 主机降档（`-Xms6G -Xmx8G`）+ 给出恢复建议（升级硬件 / 裁剪 mods / 降低 view-distance）；错误信息含上下文（主机 RAM 实测值 + Mod 数量 + 请求值） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: `server.properties` 必含 `allow-flight=true` + `max-tick-time=180000`（MINE-002/003）；`online-mode=true` 且 `enforce-secure-profile=true`（配对）；view/sim distance 在 4-6 人档（10/6）；JVM `-Xms12G -Xmx24G` 且系统预留 ≥8GB 检查通过（MINE-004）；启动脚本为独立脚本引用 `user_jvm_args.txt` + loader 参数（MINE-006，非 startserver.sh）
- case_002: `online-mode=false` 且 `enforce-secure-profile=false` 同时出现（MINE-005，二者必须成对）；`allow-flight=true` 与 `max-tick-time=180000` 不缺失
- case_003: 必须走 Golden Error 路径 —— 拒绝 `-Xmx24G`（可用 RAM 不足），降档值可复现（16GB 主机 → `-Xms6G -Xmx8G`），错误信息同时含 `context`（主机实测 RAM + Mod 数量 + 请求 Xmx）与 `recovery`（≥2 条：升级 / 裁剪 mods / 降 view-distance）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: server_config 决策（properties 关键字段 + JVM 参数 + 脚本/防火墙/备份）或错误结构（context / recovery）
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- `server.properties` 字段值必须精确匹配（allow-flight / max-tick-time / online-mode / enforce-secure-profile 配对）
- JVM 分配必须按 Mod 数量分档且满足 ≥8GB 系统预留（MINE-004）
- 错误路径必须同时含 `context` 与 `recovery` 两个字段
- 启动脚本必须独立且引用 `user_jvm_args.txt`（MINE-006）

## 关联

- SKILL.md Genes: MINE-001~007
- SKILL.md 验证清单: 6 项（Java 版本匹配 / allow-flight+max-tick-time+认证配对 / JVM 分档 / ufw 25565 / 独立启动脚本 / 启动验证+备份 cron 24 份）
- EXAMPLES: 示例 1（ATM10 正常）/ 示例 2（非正版配对）/ 示例 3（备份策略）
