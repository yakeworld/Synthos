#!/usr/bin/env python3
"""test_reward_integrity.py — 奖励完整性测试 (reward integrity / 假阳性反例集)

来源: 2026-09-07 外部评审实验1 (reward integrity), 用户拍板自主执行。
纪律 (EVOL-007 独立计算): 本文件的反例与断言在补丁前先冻结;
修评估器时对本文件只读 — 改断言 = 改考题, 不算修评估器。

覆盖评审五脆弱点中的可测部分:
  [2] L0.5 数据诚实门: "有 state.json 字典" 不等于 "数字有证据"
  [2] G2 编译门: "有 \\documentclass 字符串" 不等于 "编译成功"
  [1] behavior 维: "status=completed" 不等于 "产物存在"

运行: python3 tests/test_reward_integrity.py   (exit 0 = 全过)
依赖: pdflatex 在 PATH (本机 /usr/local/bin/pdflatex); 缺失时 G2 编译断言降级跳过并打印 SKIP。
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUNNER = os.path.join(
    ROOT, "skills", "core", "quality-gate", "scripts", "quality-gate-runner.py"
)


def load_runner():
    spec = importlib.util.spec_from_file_location("qgr", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_paper(base, name, tex, state=None, extra_files=None):
    """标准布局: <base>/<name>/01-manuscript/paper.tex + <base>/<name>/state.json"""
    paper_dir = os.path.join(base, name)
    ms = os.path.join(paper_dir, "01-manuscript")
    os.makedirs(ms)
    with open(os.path.join(ms, "paper.tex"), "w") as f:
        f.write(tex)
    if state is not None:
        with open(os.path.join(paper_dir, "state.json"), "w") as f:
            json.dump(state, f)
    for rel, content in (extra_files or {}).items():
        p = os.path.join(ms, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(content)
    return paper_dir, ms


# ── 冻结 fixtures ──────────────────────────────────────────────
TEX_NUMERIC_OK = r"""\documentclass{article}
\title{T}\author{A}\begin{document}\section{R}
Accuracy 95.2\% with p < 0.001.
\end{document}
"""
TEX_NUMERIC_BAD = r"""\documentclass{article}
\title{T}\author{A}\begin{document}\section{R}
Accuracy 95.2\% with p < 0.001.
\end{document}
"""
TEX_COMPILES = r"""\documentclass{article}
\title{T}\author{A}\begin{document}\section{R}
Hello. 42 subjects.
\end{document}
"""
TEX_BROKEN = r"""\documentclass{article}
\title{T}\author{A}\begin{document}\section{R}
\undefinedcommandxyz 42
\end{document}
"""
STATE_MATCH = {"accuracy_pct": 95.2, "p_value": 0.001}
STATE_EMPTY = {}

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def main():
    qgr = load_runner()
    have_pdflatex = shutil.which("pdflatex") is not None
    if not have_pdflatex:
        print("SKIP pdflatex not in PATH — G2 编译断言降级为结构断言")

    tmp = tempfile.mkdtemp(prefix="reward_integrity_")
    try:
        # ── L0.5 ──
        p_ok, ms_ok = make_paper(tmp, "n1", TEX_NUMERIC_OK, state=STATE_MATCH)
        r = qgr.check_l05_data_honesty(ms_ok)
        check("L05-P1 数字与state.json交叉核对一致 → PASS且score==1.0",
              r.pass_ and abs(r.score - 1.0) < 1e-9, f"pass={r.pass_} score={r.score}")

        p_bad, ms_bad = make_paper(tmp, "n2", TEX_NUMERIC_BAD, state=STATE_EMPTY)
        r = qgr.check_l05_data_honesty(ms_bad)
        check("L05-N1 空state.json不能背书95.2% → FAIL或score<0.5(一票否决)",
              (not r.pass_) or r.score < 0.5, f"pass={r.pass_} score={r.score}")

        p_no, ms_no = make_paper(tmp, "n3", TEX_NUMERIC_BAD, state=None)
        r = qgr.check_l05_data_honesty(ms_no)
        # 冻结意图: 无证据源不得拿高分 PASS。2026-09-07 补丁实际更严:
        # 有数值声明但无任何 state.json → FAIL(0.3, 一票否决)。断言取并集:
        # 必须 (FAIL) 或 (PASS 且 <0.5), 排除 "PASS 0.6/0.8" 旧假阳性。
        check("L05-N2 无state.json → FAIL或score<0.5 (不得高分PASS)",
              (not r.pass_) or r.score < 0.5, f"pass={r.pass_} score={r.score}")

        # ── G2 ──
        p_c, ms_c = make_paper(tmp, "g1", TEX_COMPILES)
        r = qgr.check_g2_compile(ms_c)
        check("G2-P1 可编译文档 → PASS且score==1.0",
              r.pass_ and abs(r.score - 1.0) < 1e-9, f"pass={r.pass_} score={r.score}")

        p_b, ms_b = make_paper(tmp, "g2", TEX_BROKEN)
        r = qgr.check_g2_compile(ms_b)
        if have_pdflatex:
            check("G2-N1 含未定义命令 → FAIL(pdflatex退出码非0)",
                  not r.pass_, f"pass={r.pass_} score={r.score} findings={r.findings[:2]}")
        else:
            print("SKIP  G2-N1 需 pdflatex")

        # run_gate 一票否决: G2 失败必须拉低 overall_pass
        rep = qgr.run_gate(p_b, mode="fast")
        g2f = rep.gates.get("G2_compile", {}).get("pass")
        if have_pdflatex and g2f is False:
            check("G2-VETO run_gate: G2编译失败 → overall_pass=False",
                  not rep.overall_pass, f"overall_score={rep.overall_score}")
        else:
            print("SKIP  G2-VETO (G2未判失败, 依赖 G2-N1)")

        # ── behavior: completed 须有产物佐证 (通过 diagnose.py 子进程) ──
        # 构造最小 outputs 树放进临时 cwd, 跑 diagnose 的 behavior 段
        diag = os.path.join(ROOT, "skills", "private", "extended", "meta",
                            "evolution", "scripts", "diagnose.py")
        t2 = tempfile.mkdtemp(prefix="reward_behavior_")
        try:
            outs = os.path.join(t2, "outputs")
            os.makedirs(outs)
            # diagnose.py 从 SYNTHOS_DIR 读 skills/, 缺失会 ZeroDivisionError
            os.symlink(os.path.join(ROOT, "skills"), os.path.join(t2, "skills"))
            with open(os.path.join(outs, "pipeline_trace_ok.json"), "w") as f:
                json.dump({"gene_activation": {"ACQ": ["KA-001"]},
                           "atoms": {"knowledge-acquisition": {
                               "status": "completed",
                               "output_file": "out.json"}}}, f)
            with open(os.path.join(outs, "out.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(outs, "pipeline_trace_ghost.json"), "w") as f:
                json.dump({"gene_activation": {"ACQ": ["KA-001"]},
                           "atoms": {"knowledge-acquisition": {
                               "status": "completed",
                               "output_file": "ghost_missing.json"}}}, f)
            env = dict(os.environ)
            env['SYNTHOS_DIR'] = t2  # diagnose.py 强制 chdir(SYNTHOS_DIR)
            proc = subprocess.run(
                [sys.executable, diag], cwd=t2, env=env,
                capture_output=True, text=True, timeout=300)
            out = proc.stdout
            # diagnose 会打印 behavior 维; 提取其值
            import re
            m = re.search(r"BEHAVIOR:\s*(0\.\d+|1\.0)", out)
            if m:
                bv = float(m.group(1))
                # 2 traces 均有 gene_activation → activation=1.0; lessons 无文件 → 0
                # 旧代码: verify=2/2=1.0 → behavior=0.5+0.3=0.80 (ghost 被计入)
                # 新代码: verify=1/2=0.5 → behavior=0.5+0.15=0.65 (ghost 被剔除)
                check("BEH-N1 无产物的completed不得计入verify (behavior<0.80)",
                      bv < 0.79, f"behavior={bv}")
            else:
                print("SKIP  BEH-N1 未能从 diagnose 输出解析 behavior 值; 见 /tmp 日志")
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
