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


def run_scenario(fx, fault_mode, init_consecutive, score_before):
    """跑单周期故障注入。fault_mode: 'rc1' | 'timeout' | 'empty_stdout' | 'ok'"""
    state_path = os.path.join(fx, "evolution-state.json")
    with open(state_path, "w") as f:
        json.dump({"score": score_before, "status": "healthy", "state": "healthy",
                   "consecutive_healthy": init_consecutive, "cycle": 0,
                   "diagnostics": {k: 1.0 for k in
                                   ("structural", "benchmark", "constitutional",
                                    "optimize", "coverage", "absorption",
                                    "liveness", "behavior", "overall")},
                   "knowledge_pipeline": {}}, f)
    foreign = os.path.join(fx, "foreign.txt")
    with open(foreign, "w") as f:
        f.write("pre-staged unrelated file\n")
    subprocess.run(["git", "add", "foreign.txt"], cwd=fx, capture_output=True, text=True)

    mod = load_autoloop()
    mod.BASE_DIR = fx
    real_run = mod.subprocess.run

    def fake_run(cmd, **kw):
        joined = " ".join(str(c) for c in cmd)
        if "diagnose.py" in joined:
            if fault_mode == "rc1":
                return SimpleNamespace(returncode=1, stdout="",
                                       stderr="injected diagnose failure")
            if fault_mode == "timeout":
                raise subprocess.TimeoutExpired(cmd=cmd, timeout=kw.get("timeout", 120))
            if fault_mode == "empty_stdout":
                return SimpleNamespace(returncode=0, stdout="", stderr="")
            return SimpleNamespace(returncode=0,
                                   stdout="OVERALL: 0.9512\nBEHAVIOR: 0.6\n",
                                   stderr="")
        return real_run(cmd, **kw)

    mod.subprocess.run = fake_run
    raised = None
    try:
        mod.auto_loop(1, max_cycles=1)
    except Exception as e:
        raised = e
    st = json.load(open(state_path))
    return st, raised, foreign


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

        # ===== 场景 A: diagnose rc=1 (原 T1-T5c) =====
        st, raised, foreign = run_scenario(fx, "rc1", 0, 0.9)
        if raised:
            print(f"  (场景A auto_loop raised {type(raised).__name__}: {raised})")
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
        # T5c (评审四轮强化): porcelain 行名检查太弱 (git reset 后 ?? 前缀仍匹配文件名)
        # → 断言 index 级: foreign.txt 在 index 中且有暂存内容 (ls-files -s 非空)。
        idx = subprocess.run(["git", "ls-files", "-s", "foreign.txt"], cwd=fx,
                             capture_output=True, text=True).stdout.strip()
        check("T5c 失败后 foreign.txt 仍在 git index (staged 对象未丢失)",
              idx != "" and "foreign.txt" in idx, f"index: {idx!r}")
        if idx:
            blob = idx.split()[1]
            blob_ct = subprocess.run(["git", "cat-file", "-p", blob], cwd=fx,
                                     capture_output=True, text=True).stdout
            check("T5c2 index 内容保全 (暂存对象内容 = 原文件内容)",
                  "pre-staged unrelated file" in blob_ct, f"blob: {blob_ct[:40]!r}")
        else:
            check("T5c2 index 内容保全 (暂存对象内容 = 原文件内容)", False, "no blob")

        # ===== 场景 B: diagnose TimeoutExpired (评审四轮: 旧版超时在状态降级前抛出) =====
        st, raised, _ = run_scenario(fx, "timeout", 7, 0.9)
        check("T6 诊断超时 → status degraded (不得遗留旧 healthy)",
              st.get("status") == "degraded",
              f"status={st.get('status')}" + (f" raised={raised}" if raised else ""))
        check("T7 诊断超时 → 非零 consecutive_healthy 归零 (7→0)",
              st.get("consecutive_healthy") == 0,
              f"consecutive={st.get('consecutive_healthy')}")
        check("T7b 诊断超时 → next_action 含 HALT",
              "HALT" in str(st.get("next_action", "")), f"next_action={st.get('next_action')!r}")
        check("T7c 诊断超时 → 分数不更新 (保持 0.9, 故障周期不写自算分数)",
              abs(st.get("score", -1) - 0.9) < 1e-9, f"score={st.get('score')}")

        # ===== 场景 C: rc=0 但 stdout 空 (无效成功输出不得计为健康周期) =====
        st, raised, _ = run_scenario(fx, "empty_stdout", 3, 0.88)
        check("T8 rc=0 但无 OVERALL 输出 → status degraded (无效输出=故障)",
              st.get("status") == "degraded", f"status={st.get('status')}")
        check("T8b rc=0 无效输出 → consecutive 归零 (3→0)",
              st.get("consecutive_healthy") == 0, f"consecutive={st.get('consecutive_healthy')}")

        # ===== 场景 D: 正常诊断 (OVERALL 解析) → healthy + 计数 +1 + 分数更新 =====
        st, raised, _ = run_scenario(fx, "ok", 4, 0.87)
        check("T9 正常诊断 → status healthy 且 consecutive 4→5",
              st.get("status") == "healthy" and st.get("consecutive_healthy") == 5,
              f"status={st.get('status')} consecutive={st.get('consecutive_healthy')}")
        check("T9b 正常诊断 → 分数=诊断 OVERALL 原值 (0.9512, 凡数必源)",
              abs(st.get("score", -1) - 0.9512) < 1e-6, f"score={st.get('score')}")
        check("T9c 正常诊断 → next_action=continue 且 auto_trigger 开",
              st.get("next_action") == "continue" and st.get("auto_trigger_active") is True,
              f"next_action={st.get('next_action')!r} trigger={st.get('auto_trigger_active')}")
    finally:
        shutil.rmtree(fx, ignore_errors=True)

    fails = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(fails)}/{len(results)} passed")
    if fails:
        print("FAILED:", fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
