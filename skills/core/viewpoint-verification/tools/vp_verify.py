#!/usr/bin/env python3
"""vp_verify.py — viewpoint-verification 铁律实现 (三必验)

SKILL.md 铁律:
  1. 不只看支持性证据 (confirmation bias 是最大敌人)
  2. 不验不可检验的命题 (那叫信仰不叫科学)
  3. 不产出模糊结论 (必须给出明确的 支持/反对/证据不足)

本脚本 = 验证报告的结构校验器: 检查报告是否含反方证据段、
可检验判据、以及明确的三态结论。

用法:
    python3 vp_verify.py <report.md>          # 校验单份报告
    python3 vp_verify.py <report.md> ...      # 批量

输出: 每份报告 3 项检查 + 判定; 全过 exit 0, 否则 exit 1。
"""
import re
import sys

CONCLUSION_RE = re.compile(r'(支持|反对|证据不足|PASS|REJECT|INCONCLUSIVE)', re.I)


def verify(path: str):
    try:
        text = open(path, encoding='utf-8').read()
    except OSError as e:
        return False, f'unreadable({e})', []
    checks = []
    # 1. 反方证据段 (confirmation bias 对账)
    has_counter = bool(re.search(r'(反方|反对证据|Counter|falsif|证伪|反面|dissent|against)', text, re.I))
    checks.append((has_counter, '反方证据段'))
    # 2. 可检验判据 (可证伪性)
    has_testable = bool(re.search(r'(可检验|可证伪|证伪|判据|阈值|threshold|criterion|falsif|falsifier|testable)', text, re.I))
    checks.append((has_testable, '可检验判据'))
    # 3. 明确结论 (三态)
    has_conclusion = bool(CONCLUSION_RE.search(text))
    checks.append((has_conclusion, '明确三态结论'))
    ok = all(c[0] for c in checks)
    detail = ', '.join(name for passed, name in checks if not passed)
    return ok, f'pass' if ok else f'missing[{detail}]', checks


def main():
    if not sys.argv[1:]:
        print('usage: vp_verify.py <report.md> ...', file=sys.stderr)
        return 2
    fail = 0
    for p in sys.argv[1:]:
        ok, reason, checks = verify(p)
        marks = ' '.join('✓' if c[0] else '✗' + c[1] for c in checks)
        print(f'{"PASS" if ok else "FAIL"}  {p}  {marks}')
        if not ok:
            fail += 1
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
