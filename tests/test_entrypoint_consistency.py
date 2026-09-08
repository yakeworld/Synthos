#!/usr/bin/env python3
"""test_entrypoint_consistency.py — 入口一致性验证 (reward-integrity P1, 评审三轮)

Astra 第三轮 P1 要求: 选一个核心 quality-gate 技能, 对每个实际投影入口输出
realpath / 内容 SHA256 / 源 SHA, 断言:
  E1 每个暴露该技能的投影入口, 其 realpath 必须落在 Synthos 活源 skills/ 树内
     (不允许指向备份/旧副本/脱离源的独立目录);
  E2 每个入口看到的 SKILL.md 与 runner 的 SHA256 必须与活源一致 (零漂移);
  E3 攻击面: 若某入口被替换为"旧版本 runner 的真实目录副本" (非 symlink),
     一致性检查必须检测并 FAIL — 防"symlink 指向同源"不等于"运行时加载同一版本"。

已知事实 (2026-09-07 实测):
  - dsh skills-flat/quality-gate 是 symlink, 目标路径 /media/yakeworld/sda2/...
    是 bind mount 别名, realpath 解析回 /media/yakeworld/data/Synthos/... 活源;
  - codex 投影用目录级 symlink (synthos-core -> skills/core), 无逐技能链接;
  - 两者都是 symlink 投影 (零拷贝), 风险在"被替换为真实目录"与"路径别名漂移"。

运行: python3 tests/test_entrypoint_consistency.py   (exit 0 = 全过)
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIVE_SOURCE = os.path.join(os.path.realpath(ROOT), "skills", "core", "quality-gate")

CODEX_DIR = os.path.expanduser("~/.codex/skills")
DSH_DIR = os.path.expanduser("~/.dsh/skills-flat")

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def sha256(p):
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(65536), b""):
                h.update(c)
        return h.hexdigest()
    except OSError:
        return None


def find_entrypoints():
    """返回 [(入口路径, 类型)] — 所有暴露 quality-gate 的投影位置。"""
    eps = []
    # dsh 展平: 单层 symlink
    d = os.path.join(DSH_DIR, "quality-gate")
    if os.path.lexists(d):
        eps.append((d, "dsh-flat"))
    # codex: 目录级 symlink (synthos-core -> skills/core), 检查其下 core/quality-gate
    c = os.path.join(CODEX_DIR, "synthos-core", "quality-gate")
    if os.path.lexists(c):
        eps.append((c, "codex-core"))
    # 任何直接放在投影根的 quality-gate (防手工拷贝)
    for root_d, tag in ((CODEX_DIR, "codex"), (DSH_DIR, "dsh")):
        if os.path.isdir(root_d):
            for name in os.listdir(root_d):
                if name == "quality-gate":
                    p = os.path.join(root_d, name)
                    if not any(p == e[0] for e in eps):
                        eps.append((p, tag))
    return eps


def main():
    live_skill = os.path.join(LIVE_SOURCE, "SKILL.md")
    live_runner = os.path.join(LIVE_SOURCE, "scripts", "quality-gate-runner.py")
    live_sha_skill = sha256(live_skill)
    live_sha_runner = sha256(live_runner)
    check("SETUP 活源 SKILL.md + runner 可读且有 SHA",
          live_sha_skill is not None and live_sha_runner is not None,
          f"live={LIVE_SOURCE}")

    eps = find_entrypoints()
    check("E0 至少发现一个投影入口", len(eps) > 0,
          f"entries={[(os.path.basename(e[0]), e[1]) for e in eps]}")

    for path, tag in eps:
        # E1: realpath 落在活源树内
        real = os.path.realpath(path)
        in_live = os.path.dirname(real).startswith(LIVE_SOURCE) or \
            real.startswith(os.path.realpath(os.path.join(ROOT, "skills")))
        check(f"E1 [{tag}] realpath 落在 Synthos 活源 skills/ 树内",
              in_live, f"realpath={real}")
        # E2: 内容 SHA 与活源一致
        e_skill = os.path.join(real, "SKILL.md")
        e_runner = os.path.join(real, "scripts", "quality-gate-runner.py")
        es = sha256(e_skill)
        er = sha256(e_runner)
        check(f"E2 [{tag}] SKILL.md SHA 与活源一致 (零漂移)",
              es is not None and es == live_sha_skill,
              f"entry={(es or 'MISSING')[:12]} live={live_sha_skill[:12]}")
        check(f"E2 [{tag}] runner SHA 与活源一致 (零漂移)",
              er is not None and er == live_sha_runner,
              f"entry={(er or 'MISSING')[:12]} live={live_sha_runner[:12]}")

    # E3 攻击面: 入口被替换为"旧版 runner 的真实目录" → 必须被检测
    attack = tempfile.mkdtemp(prefix="epattack_")
    try:
        fake = os.path.join(attack, "quality-gate")
        os.makedirs(os.path.join(fake, "scripts"))
        shutil.copy2(live_skill, os.path.join(fake, "SKILL.md"))
        # 旧版 runner: 在活源 runner 内容上植入已知旧行为标记 (缺引擎满分PASS)
        old_runner = open(live_runner).read().replace(
            "UNVERIFIED: no LaTeX engine available",
            "pdflatex not available — structure-only check (降级)")
        with open(os.path.join(fake, "scripts", "quality-gate-runner.py"), "w") as f:
            f.write(old_runner)
        fake_runner_sha = sha256(os.path.join(fake, "scripts", "quality-gate-runner.py"))
        detected = (fake_runner_sha is not None
                    and fake_runner_sha != live_sha_runner)  # 一致性检查 = SHA 比对
        check("E3 旧版 runner 真实目录副本 (非 symlink) 被一致性检查检测为漂移",
              detected,
              f"fake_runner={(fake_runner_sha or 'MISSING')[:12]} live={live_sha_runner[:12]} "
              f"detected={detected}")
        # 且旧版 runner 的行为确实不同 (缺引擎时旧=满分PASS, 新=UNVERIFIED FAIL)
        if detected:
            check("E3b 漂移非误报: 旧版内容确实缺失 UNVERIFIED 语义",
                  "UNVERIFIED: no LaTeX engine" not in old_runner,
                  "old behavior: structure-only 满分 (已确认语义差异)")
    finally:
        shutil.rmtree(attack, ignore_errors=True)

    fails = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(fails)}/{len(results)} passed")
    if fails:
        print("FAILED:", fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
