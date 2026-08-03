#!/usr/bin/env python3
"""Synthos Core Atom Golden Tests — structural verification.

Gate: G6 (regression guard)
Usage: python3 golden_test.py
Exit: 0 = all pass, 1 = any fail
"""

import os, sys, json

SYNTHOS = "/media/yakeworld/sda2/Synthos"

CORE_ATOMS = {
    "knowledge-acquisition":   {"version": True, "signature": True, "io_contract": True},
    "knowledge-extraction":    {"version": True, "signature": True, "io_contract": True},
    "association-discovery":   {"version": True, "signature": True, "io_contract": True},
    "hypothesis-generation":   {"version": True, "signature": True, "io_contract": True},
    "argument-expression":     {"version": True, "signature": True, "io_contract": True},
    "viewpoint-verification":  {"version": True, "signature": True, "io_contract": True},
}

def check_atom(name: str) -> dict:
    path = os.path.join(SYNTHOS, "skills", "core", name, "SKILL.md")
    if not os.path.exists(path):
        return {"ok": False, "reason": "SKILL.md not found"}
    
    with open(path) as f:
        content = f.read()
    
    result = {}
    result["has_version"] = "version:" in content.split("---")[1] if content.startswith("---") else False
    result["has_signature"] = "signature:" in content
    result["has_io_contract"] = "IO_CONTRACT" in content or "io_contract:" in content
    result["ok"] = all([result["has_version"], result["has_signature"], result["has_io_contract"]])
    return result

def main():
    fails = 0
    print("=== Synthos Core Atom Golden Tests ===\n")
    for name in CORE_ATOMS:
        r = check_atom(name)
        icon = "✅" if r["ok"] else "❌"
        print(f"  {icon} {name}")
        print(f"       version: {'✅' if r['has_version'] else '❌'}  "
              f"signature: {'✅' if r['has_signature'] else '❌'}  "
              f"IO_CONTRACT: {'✅' if r['has_io_contract'] else '❌'}")
        if not r["ok"]:
            fails += 1
    
    print(f"\n  {'='*40}")
    print(f"  Result: {len(CORE_ATOMS) - fails}/{len(CORE_ATOMS)} pass")
    print(f"  Gate G6: {'✅ PASS' if fails == 0 else '❌ FAIL'}")
    return 1 if fails > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
