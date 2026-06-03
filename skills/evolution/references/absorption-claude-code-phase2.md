# Claude Code Absorption — Phase 2: Karma + Assertion

> 吸收日期: 2026-06-03
> 源项目: anthropics/claude-code (123K⭐)
> 目标系统: Synthos v2.18.0
> 前情: 2026-05-16 已完成 5 层提取，Hook 系统已吸收；本次补 Karma + Assertion

## 已吸收清单

| 日期 | 机制 | 状态 |
|:-----|:-----|:-----|
| 2026-05-16 | Hook 事件规范 (8 种事件) | ✅ → evolution 引擎 v2.3→v2.4 |
| 2026-05-16 | 触发条件+验证清单规范 | ✅ → project-experience-distillation L1 |
| 2026-05-16 | 哲学免疫系统 | ✅ → CONSTITUTION.md |
| 2026-06-03 | **Karma moderation** | 🔴 待注入 → quality-gate |
| 2026-06-03 | **Assertion-based reliability** | 🔴 待注入 → falsification-validation |

## 本次吸收

### Karma Moderation

**Claude Code 机制**: 用户对输出有隐式/显式的反馈评分（Karma），系统用这个分数调整未来的行为偏好，但不改变宪法基线。

**Synthos 缺口**: 质量门是「通过/不通过」二元制，没有「轻微不满」的反馈通道。

**注入方式**: quality-gate 增加 Karma 子门

```
Karma 门 (L0.2):
  Step 1: 检查用户最近 5 次交互中的隐式修正（纠正措辞、补充要求、要求重做）
  Step 2: 如果修正模式符合已知「反感信号」→ 调低对应维度的默认评分
  Step 3: 记录到 lession 库
```

### Assertion-Based Reliability

**Claude Code 机制**: 每次输出前调用 `assert()` 级联检查 — 断言不可忽略，产生偏差直接阻止输出。

**Synthos 缺口**: falsification-validation 有测试但无「断言阻挡」机制。

**注入方式**: falsification-validation 增加断言协议

```
断言铁律:
  - 每个实验声明必须有可执行的断言
  - 断言失败 = 输出阻塞，不回退，不绕行
  - 断言层级: L1 (类型) → L2 (范围) → L3 (可复现) → L4 (跨数据一致性)
```

## 验证

- [ ] quality-gate 有 Karma 门的触发条件和执行步骤
- [ ] falsification-validation 有断言铁律和 4 层断言规范
