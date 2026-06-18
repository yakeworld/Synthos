# Correction Record — 2026-06-05

## Correction: 30-second auto-execute rule confirmed
- **Context**: After completing a dual quality check on vor-bppv-diagnosis, the calibration score was 0.83 (below T1 threshold). Per the autonomous-execution-threshold rules, the revision should auto-start without asking.
- **Correction**: User confirmed: "判断用户可能回答，超过阈值自动执行；可以在每一次任务完成后，咨询人类意见的时候执行，超过30秒没有回复自动执行。"
- **Applied to**: `autonomous-execution-threshold` SKILL.md — 30-second rule section updated with user's exact words.
- **Lesson**: The rule already existed in v2.7.0 but the user's explicit reconfirmation this session was worth anchoring with their exact quote.
