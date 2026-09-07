#!/usr/bin/env python3
"""test_reward_integrity_adversarial.py — 反操纵攻击测试 (奖励单调性契约)

来源: 2026-09-07 外部评审三轮 (PoE Astra, 验收不通过), 用户拍板自主执行。
纪律: 本文件是独立攻击测试, 不改动冻结文件 tests/test_reward_integrity.py (EVOL-007)。

核心不变量 (评审三轮原文):
  "移除证据、隐藏证据字段或缺失验证依赖, 不得提高通过概率与奖励。"

攻击族 (每族至少一个候选, 旧错误版本必须被杀死, 修复版本必须通过):
  A1 无关同值 — room_temperature: 85.2 背书正文 "Accuracy 85.2%" (已知局限, 显式声明)
  A2 p 声明 — 正文只有 "p < 0.001" 无 state → 不得按 "无可核对项" 满分放行
  A3 人数 2024 — "enrolled 2024 participants" 不得被当年份漏核
  A4 排版参数 — 12pt 不得计入待核对数字 (防误拒: 真实正确样例仍须通过)
  A5 无编译器 — 无任何 LaTeX 引擎 → 不得满分通过 (UNVERIFIED 语义)
  A6 仅 xelatex — 无 pdflatex 有 xelatex → 必须尝试 xelatex, 成功 findings 记录真实引擎
  A7 缺产物字段 — 删除 trace 的 output_file 字段 → behavior 不得上升 (奖励单调)

运行: python3 tests/test_reward_integrity_adversarial.py   (exit 0 = 全过)
"""
import importlib.util
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FROZEN = os.path.join(HERE, "test_reward_integrity.py")
DIAG = os.path.join(ROOT, "skills", "private", "extended", "meta",
                    "evolution", "scripts", "diagnose.py")

PREFIX = (r"\documentclass{article}\title{Audit}\begin{document}")
SUFFIX = r"\end{document}"

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def run_diagnose_behavior(tmpdir):
    env = dict(os.environ)
    env['SYNTHOS_DIR'] = tmpdir
    proc = subprocess.run([sys.executable, DIAG], cwd=tmpdir, env=env,
                          capture_output=True, text=True, timeout=300)
    m = re.search(r"BEHAVIOR:\s*(0\.\d+|1\.0)", proc.stdout)
    return float(m.group(1)) if m else None


def main():
    t = runpy.run_path(FROZEN)
    q = t["load_runner"]()

    tmp = tempfile.mkdtemp(prefix="adversarial_")
    try:
        # ── A1 无关同值 (LEGACY 已知局限 + STRICT 绑定 现已修复) ──
        _, ms = t["make_paper"](tmp, "a1_unrelated",
                                PREFIX + r"Accuracy 85.2\%." + SUFFIX,
                                state={"room_temperature": 85.2})
        r = q.check_l05_data_honesty(ms)
        print(f"LI-A1 (legacy) 无关字段同值当前: pass={r.pass_} score={r.score}")
        check("A1 LEGACY 无关同值: 结果已显式记录 (无 provenance 时仍可通过, 向后兼容)",
              True, f"pass={r.pass_}")
        # A1-STRICT: 补全 provenance → 无关字段同值必须不再背书
        _, ms_s = t["make_paper"](tmp, "a1s_unrelated_bound",
                                  PREFIX + r"Accuracy 85.2\%." + SUFFIX,
                                  state={"room_temperature": 85.2,
                                         "provenance": {}})
        # 空 provenance dict = STRICT 模式已启用, 但无任何绑定记录 → 必须不通过
        r = q.check_l05_data_honesty(ms_s)
        check("A1s STRICT 空 provenance → 无关字段同值不再背书 (必须 FAIL)",
              not r.pass_, f"pass={r.pass_} score={r.score} findings={r.findings[:1]}")
        # A1s2: 完整绑定记录 (真实结果文件 + 哈希) → 必须通过
        import importlib.util, hashlib
        _, ms_bound = t["make_paper"](tmp, "a1s2_bound_ok",
                                      PREFIX + r"Accuracy 85.2\%." + SUFFIX,
                                      state={"room_temperature": 85.2,
                                             "provenance": {}})
        resf = os.path.join(ms_bound, "results_accuracy.json")
        with open(resf, "w") as f:
            f.write('{"accuracy": 0.852}')
        h = hashlib.sha256(open(resf, "rb").read()).hexdigest()[:16]
        # 回填完整绑定记录 (结果文件已存在, 哈希对得上)
        sj = os.path.join(tmp, "a1s2_bound_ok", "state.json")
        with open(sj) as f:
            st = json.load(f)
        st["provenance"] = {"accuracy": {
            "value": 85.2, "metric": "accuracy", "unit": "%",
            "run": "analyze.py --seed 42",
            "result_file": "01-manuscript/results_accuracy.json",
            "file_hash": h, "tex_location": "L3 'Accuracy 85.2\\%'"}}
        with open(sj, "w") as f:
            json.dump(st, f)
        r = q.check_l05_data_honesty(ms_bound)
        check("A1s2 STRICT 完整绑定 (结果文件存在+哈希匹配) → 通过 (防'全部拒绝'投机)",
              r.pass_ and r.score >= 1.0, f"pass={r.pass_} score={r.score}")

        # ── A2 p 声明无证据 → 不得满分放行 ──
        _, ms = t["make_paper"](tmp, "a2_p_only",
                                PREFIX + "The test yielded p < 0.001." + SUFFIX,
                                state=None)
        r = q.check_l05_data_honesty(ms)
        check("A2 仅 p 声明无 state → 不得 PASS 1.0 (旧版绕过: '无可核对项')",
              not (r.pass_ and r.score >= 1.0), f"pass={r.pass_} score={r.score}")
        # 变体: state 存在但缺 p 值
        _, ms = t["make_paper"](tmp, "a2b_p_missing",
                                PREFIX + "The test yielded p < 0.001." + SUFFIX,
                                state={"other": 1})
        r = q.check_l05_data_honesty(ms)
        check("A2b 仅 p 声明 + state 缺 p 值 → 不得满分通过",
              not (r.pass_ and r.score >= 1.0), f"pass={r.pass_} score={r.score}")
        # 正例: state 含 p 值 → 必须通过 (防"全部拒绝"投机)
        _, ms = t["make_paper"](tmp, "a2c_p_bound",
                                PREFIX + "The test yielded p < 0.001." + SUFFIX,
                                state={"p_value": 0.001})
        r = q.check_l05_data_honesty(ms)
        check("A2c 仅 p 声明 + state 含 p 值 → 通过 (真实正确样例不被误杀)",
              r.pass_ and r.score >= 1.0, f"pass={r.pass_} score={r.score}")

        # ── A3 人数 2024 不得当年份漏核 ──
        _, ms = t["make_paper"](tmp, "a3_count_2024",
                                PREFIX + "We enrolled 2024 participants." + SUFFIX,
                                state=None)
        r = q.check_l05_data_honesty(ms)
        check("A3 人数 2024 无 state → 不得 PASS 1.0 (旧版绕过: 年份排除)",
              not (r.pass_ and r.score >= 1.0), f"pass={r.pass_} score={r.score}")
        _, ms = t["make_paper"](tmp, "a3b_count_bound",
                                PREFIX + "We enrolled 2024 participants." + SUFFIX,
                                state={"n_participants": 2024})
        r = q.check_l05_data_honesty(ms)
        check("A3b 人数 2024 + state 含 2024 → 通过 (防误拒)",
              r.pass_ and r.score >= 1.0, f"pass={r.pass_} score={r.score}")

        # ── A4 排版参数防误拒 ──
        _, ms = t["make_paper"](tmp, "a4_layout_12pt",
                                r"\documentclass[12pt]{article}\title{Audit}"
                                r"\begin{document}Accuracy 85.2\%."
                                r"\end{document}",
                                state={"accuracy_pct": 85.2})
        r = q.check_l05_data_honesty(ms)
        check("A4 12pt 排版参数 + 真实 85.2 有证据 → 通过 (评审三轮指出的误拒)",
              r.pass_ and r.score >= 1.0, f"pass={r.pass_} score={r.score}")

        # ── A5 无编译器 → 不得满分通过 ──
        _, ms = t["make_paper"](tmp, "a5_no_compiler",
                                PREFIX + r"\undefinedcommandxyz" + SUFFIX)
        with patch("shutil.which", return_value=None):
            with patch("subprocess.run") as compiler:
                r = q.check_g2_compile(ms)
                check("A5 无 LaTeX 引擎 → 不得 PASS 1.0 (UNVERIFIED 语义)",
                      not (r.pass_ and r.score >= 1.0),
                      f"pass={r.pass_} score={r.score} findings={r.findings[:1]}")
                check("A5b 无引擎时零编译调用",
                      compiler.call_count == 0, f"calls={compiler.call_count}")

        # ── A6 仅 xelatex → 必须尝试且记录真实引擎 ──
        real_which = shutil.which
        with patch("shutil.which", side_effect=lambda x: real_which(x) if x == "xelatex" else None):
            _, ms = t["make_paper"](tmp, "a6_xelatex_only",
                                    PREFIX + r"\undefinedcommandxyz" + SUFFIX)
            with patch("subprocess.run") as compiler:
                compiler.return_value = type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
                r = q.check_g2_compile(ms)
                check("A6 无 pdflatex 有 xelatex → 尝试编译 (旧版提前返回, 零调用)",
                      compiler.call_count > 0, f"calls={compiler.call_count}")
                eng_ok = r.pass_ and any("engine=xelatex" in f for f in r.findings)
                check("A6b 成功 findings 记录真实引擎 xelatex (旧版固定写 pdflatex)",
                      eng_ok, f"pass={r.pass_} findings={r.findings[:1]}")

        # ── A7 缺产物字段 → behavior 不得上升 (奖励单调) ──
        t2 = tempfile.mkdtemp(prefix="adversarial_beh_")
        try:
            outs = os.path.join(t2, "outputs")
            os.makedirs(outs)
            os.symlink(os.path.join(ROOT, "skills"), os.path.join(t2, "skills"))
            # 基线: 一证实一未证实 (声明产物但文件缺失)
            with open(os.path.join(outs, "pipeline_trace_a.json"), "w") as f:
                json.dump({"gene_activation": {"ACQ": ["KA-001"]},
                           "atoms": {"x": {"status": "completed",
                                           "output_file": "out.json"}}}, f)
            with open(os.path.join(outs, "out.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(outs, "pipeline_trace_b.json"), "w") as f:
                json.dump({"gene_activation": {"ACQ": ["KA-001"]},
                           "atoms": {"x": {"status": "completed",
                                           "output_file": "ghost.json"}}}, f)
            b_with_ghost = run_diagnose_behavior(t2)
            # 操纵: 删除 output_file 字段 (减少证据)
            with open(os.path.join(outs, "pipeline_trace_b.json"), "w") as f:
                json.dump({"gene_activation": {"ACQ": ["KA-001"]},
                           "atoms": {"x": {"status": "completed"}}}, f)
            b_no_field = run_diagnose_behavior(t2)
            check("A7 删除 output_file 字段 → behavior 不得上升 (旧版 0.65→0.80 操纵)",
                  b_no_field is not None and b_with_ghost is not None
                  and b_no_field <= b_with_ghost + 1e-9,
                  f"with_ghost={b_with_ghost} no_field={b_no_field}")
        finally:
            shutil.rmtree(t2, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    fails = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(fails)}/{len(results)} passed")
    if fails:
        print("FAILED:", fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
