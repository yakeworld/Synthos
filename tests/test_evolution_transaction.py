#!/usr/bin/env python3
"""test_evolution_transaction.py — 实验2: auto-loop 事务边界故障注入

来源: 2026-09-07 外部评审三轮 (PoE Astra, P1 交付项), 用户拍板自主执行。

Astra 指出的缺陷 (源码已确认, 本测试将其固化为可复现反例):
  auto_loop() 跑 diagnose 子进程后, 无条件写 status='healthy' +
  consecutive_healthy += 1 — diagnose 崩溃 (returncode!=0) 也被记成健康周期,
  递归守卫 (status==healthy and consecutive<20) 据此 auto-continue → 失败冒充 healthy。

Astra 规定的最小验收 (本测试逐条断言):
  1. diagnose 被注入 returncode=1 (空 stdout) → 本轮不得新增健康成功记录
  2. consecutive_healthy 不得增加
  3. 失败必须有明确状态 (status != healthy)
  4. 验证失败的改动不得被提升为"已接受" (next_action 不得为 continue)
  5. 预先 staged 的无关 foreign.txt 不得被本轮提交吞并 / 失败恢复撤销

运行: python3 tests/test_evolution_transaction.py   (exit 0 = 全过)
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
AUTOCLOOP = os.path.join(ROOT, "skills", "private", "extended", "meta",
                         "evolution", "scripts", "auto-loop.py")

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def load_autoloop():
    spec = importlib.util.spec_from_file_location("autoloop", AUTOCLOOP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(args, cwd):
    subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def main():
    fx = tempfile.mkdtemp(prefix="txfixture_")
    try:
        # 1. 临时 git 仓库
        git(["init", "-q"], fx)
        git(["config", "user.email", "t@t.local"], fx)
        git(["config", "user.name", "TxTest"], fx)

        # 2. 最小技能文件 (缺原则/验证 → 会被策略选中注入)
        sk = os.path.join(fx, "skills", "txprobe")
        os.makedirs(sk)
        with open(os.path.join(sk, "SKILL.md"), "w") as f:
            f.write("---\nname: txprobe\nversion: 0.1\nsignature: 'tx'\n"
                    "io_contract: in\n---\n\n# txprobe\n\n占位正文, 待注入。\n")
        git(["add", "skills"], fx)
        git(["commit", "-qm", "fixture init"], fx)

        # 3. 初始 state: score=0.9, healthy, consecutive=0, diagnostics 全 1.0
        diag_ok = {k: 1.0 for k in
                   ("structural", "benchmark", "constitutional", "optimize",
                    "coverage", "absorption", "liveness", "behavior", "overall")}
        state_path = os.path.join(fx, "evolution-state.json")
        with open(state_path, "w") as f:
            json.dump({"score": 0.9, "status": "healthy", "state": "healthy",
                       "consecutive_healthy": 0, "cycle": 0,
                       "diagnostics": diag_ok,
                       "knowledge_pipeline": {}}, f)
        git(["add", "evolution-state.json"], fx)
        git(["commit", "-qm", "fixture state"], fx)

        # 4. 预先 staged 的无关 foreign.txt (验证不被吞并/撤销)
        foreign = os.path.join(fx, "foreign.txt")
        with open(foreign, "w") as f:
            f.write("pre-staged unrelated file\n")
        git(["add", "foreign.txt"], fx)  # staged, 未 commit

        # 5. 载入 auto-loop, 重定向 BASE_DIR 到夹具
        mod = load_autoloop()
        mod.BASE_DIR = fx
        real_run = mod.subprocess.run

        def fake_run(cmd, **kw):
            joined = " ".join(str(c) for c in cmd)
            if "diagnose.py" in joined:
                # 故障注入: diagnose 崩溃
                return SimpleNamespace(returncode=1, stdout="", stderr="injected diagnose failure")
            return real_run(cmd, **kw)

        mod.subprocess.run = fake_run

        # 6. 跑单周期
        try:
            mod.auto_loop(1, max_cycles=1)
        except Exception as e:
            print(f"  (auto_loop raised {type(e).__name__}: {e} — 记录后继续断言 state)")

        # 7. 断言
        st = json.load(open(state_path))
        check("T1 diagnose 失败 → status 不得为 healthy",
              st.get("status") != "healthy", f"status={st.get('status')}")
        check("T2 consecutive_healthy 不得增加 (保持 0)",
              st.get("consecutive_healthy", -1) == 0,
              f"consecutive={st.get('consecutive_healthy')}")
        check("T3 失败有明确状态 (degraded)",
              st.get("status") == "degraded", f"status={st.get('status')}")
        check("T4 未提升为已接受 (next_action != continue)",
              st.get("next_action") != "continue",
              f"next_action={st.get('next_action')!r}")
        check("T4b auto_trigger_active 关闭 (不 auto-continue)",
              st.get("auto_trigger_active") is False,
              f"auto_trigger_active={st.get('auto_trigger_active')}")
        check("T5 无关 foreign.txt 未被撤销 (仍存在)",
              os.path.exists(foreign), "file present" if os.path.exists(foreign) else "MISSING")
        # T5b foreign 未被吞进任何 commit (失败分支只应写 state/log; foreign 保持 staged)
        committed = subprocess.run(["git", "log", "--name-only", "--oneline"], cwd=fx,
                                   capture_output=True, text=True).stdout
        check("T5b 无关 foreign.txt 未被吞进任何 commit (保持 staged 独立)",
              "foreign.txt" not in committed,
              f"foreign in commits: {'foreign.txt' in committed}")
        porcelain = subprocess.run(["git", "status", "--porcelain"], cwd=fx,
                                   capture_output=True, text=True).stdout
        check("T5c 失败后 foreign.txt 仍为 staged (A  前缀), 未被 reset 丢失",
              any(l.strip().endswith("foreign.txt") for l in porcelain.splitlines()),
              f"porcelain: {porcelain.strip()[:100]!r}")
    finally:
        shutil.rmtree(fx, ignore_errors=True)

    fails = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(fails)}/{len(results)} passed")
    if fails:
        print("FAILED:", fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
