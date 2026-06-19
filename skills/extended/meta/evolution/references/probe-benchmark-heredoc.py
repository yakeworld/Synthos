# PROBE + BENCHMARK combined script for Synthos Evolution cron cycles
# Usage: cd /media/yakeworld/sda2/Synthos && python3 << 'PYEOF'
# (paste this entire file as heredoc body)
# CRITICAL: No emoji in output (cron security scan will block)
# CRITICAL: No execute_code — use terminal() heredoc directly

import json, os, yaml, re, subprocess

SKILLS_ROOT = "skills"
STATE_PATH = "evolution-state.json"

# ========================================
# PROBE: 7 Core Atoms (recursive search)
# ========================================
core_atoms = [
    "argument-expression", "association-discovery",
    "hypothesis-generation", "knowledge-acquisition",
    "knowledge-extraction", "task-router", "viewpoint-verification"
]

print("=" * 60)
print("PROBE: 7 CORE ATOMS")
atom_status = {}
for atom in core_atoms:
    found = False
    path = ""
    for root, dirs, files in os.walk(SKILLS_ROOT):
        for d in dirs:
            if d == atom:
                skill_path = os.path.join(root, d, "SKILL.md")
                if os.path.exists(skill_path):
                    found = True
                    path = skill_path
                    break
        if found:
            break
    status = "OK" if found else "MISSING"
    atom_status[atom] = {"found": found, "path": path}
    print(f"  [{status}] {atom}: {path if found else 'NOT FOUND'}")

atom_found = sum(1 for v in atom_status.values() if v["found"])
atom_score = atom_found / 7.0
print(f"  Atom score: {atom_found}/7 = {atom_score:.4f}")

# ========================================
# PROBE: All SKILL.md files
# ========================================
print("\n" + "=" * 60)
print("PROBE: ALL SKILL.MD FILES")
all_skills = []
for root, dirs, files in os.walk(SKILLS_ROOT):
    for f in files:
        if f == "SKILL.md":
            all_skills.append(os.path.join(root, f))
all_skills.sort()
total_skills = len(all_skills)
print(f"  Total SKILL.md files: {total_skills}")

# ========================================
# PROBE: YAML Frontmatter Validity
# ========================================
print("\n" + "=" * 60)
print("PROBE: YAML FRONTMATTER")
valid_yaml = 0
invalid_yaml = 0
no_opening = []
alias_errors = []
other_yaml_errors = []

for sp in all_skills:
    try:
        with open(sp, 'r') as f:
            content = f.read()
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    yaml.safe_load(parts[1])
                    valid_yaml += 1
                except Exception as e:
                    invalid_yaml += 1
                    err = str(e)
                    if 'alias' in err.lower():
                        alias_errors.append(sp)
                    else:
                        other_yaml_errors.append((sp, err[:100]))
            else:
                invalid_yaml += 1
        else:
            invalid_yaml += 1
            no_opening.append(sp)
    except Exception as e:
        invalid_yaml += 1

print(f"  Valid YAML: {valid_yaml}/{total_skills} ({valid_yaml/total_skills*100:.1f}%)")
print(f"  Invalid YAML: {invalid_yaml}/{total_skills}")
print(f"    No opening ---: {len(no_opening)}")
print(f"    Alias errors (**bold** in frontmatter): {len(alias_errors)}")
print(f"    Other errors: {len(other_yaml_errors)}")

# ========================================
# BENCHMARK: version + signature + IO_CONTRACT
# ========================================
print("\n" + "=" * 60)
print("BENCHMARK: version + signature + IO_CONTRACT")
has_version = 0
has_signature = 0
has_io_contract = 0

for sp in all_skills:
    with open(sp, 'r') as f:
        content = f.read()
    if re.search(r'version:', content):
        has_version += 1
    if re.search(r'signature:', content):
        has_signature += 1
    if 'IO_CONTRACT' in content:
        has_io_contract += 1

print(f"  Has version: {has_version}/{total_skills} ({has_version/total_skills*100:.1f}%)")
print(f"  Has signature: {has_signature}/{total_skills} ({has_signature/total_skills*100:.1f}%)")
print(f"  Has IO_CONTRACT: {has_io_contract}/{total_skills} ({has_io_contract/total_skills*100:.1f}%)")

v_pct = has_version / total_skills
s_pct = has_signature / total_skills
io_pct = has_io_contract / total_skills
benchmark_raw = v_pct * 0.33 + s_pct * 0.33 + io_pct * 0.34
print(f"  Benchmark = {v_pct*0.33:.4f} + {s_pct*0.33:.4f} + {io_pct*0.34:.4f} = {benchmark_raw:.4f}")

# ========================================
# BENCHMARK: Git tracked
# ========================================
print("\n" + "=" * 60)
print("BENCHMARK: GIT TRACKED")
untracked_skills = []
for sp in all_skills:
    result = subprocess.run(["git", "ls-files", "--error-unmatch", sp],
                          capture_output=True, text=True)
    if result.returncode != 0:
        untracked_skills.append(sp)
tracked = total_skills - len(untracked_skills)
print(f"  Git tracked: {tracked}/{total_skills} ({tracked/total_skills*100:.1f}%)")

# ========================================
# BENCHMARK: Encoding
# ========================================
print("\n" + "=" * 60)
print("BENCHMARK: ENCODING")
utf8_ok = 0
for sp in all_skills:
    try:
        with open(sp, 'r', encoding='utf-8') as f:
            f.read()
        utf8_ok += 1
    except:
        pass
print(f"  UTF-8 valid: {utf8_ok}/{total_skills} ({utf8_ok/total_skills*100:.1f}%)")

# ========================================
# PROBE: Circular Dependencies
# ========================================
print("\n" + "=" * 60)
print("PROBE: CIRCULAR DEPENDENCIES")
deps = {}
for sp in all_skills:
    try:
        with open(sp, 'r') as f:
            content = f.read()
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_data = yaml.safe_load(parts[1])
                if yaml_data and isinstance(yaml_data, dict):
                    name = yaml_data.get('name', os.path.basename(os.path.dirname(sp)))
                    related = []
                    meta = yaml_data.get('metadata', {})
                    if isinstance(meta, dict):
                        synthos = meta.get('synthos', {})
                        if isinstance(synthos, dict):
                            rel = synthos.get('related_skills', [])
                            if isinstance(rel, list):
                                related = rel
                    if related:
                        deps[name] = related
    except:
        pass

has_circular = False
circular_pairs = []
for skill, related in deps.items():
    for r in related:
        if r in deps and skill in deps.get(r, []):
            pair = tuple(sorted([skill, r]))
            if pair not in circular_pairs:
                circular_pairs.append(pair)
                print(f"  CIRCULAR: {pair[0]} <-> {pair[1]}")
                has_circular = True
if not has_circular:
    print("  No circular dependencies detected")
print(f"  Total circular pairs: {len(circular_pairs)}")
print(f"  Skills with deps: {len(deps)}/{total_skills}")

# ========================================
# PROBE: Structural Score
# ========================================
print("\n" + "=" * 60)
print("PROBE: STRUCTURAL SCORE")
struct_score = valid_yaml / total_skills
dirty_result = subprocess.run(["git", "status", "--porcelain"],
                             capture_output=True, text=True)
dirty_skill_count = len([l for l in dirty_result.stdout.split('\n') if 'SKILL.md' in l])
struct_penalty = min(0.05, dirty_skill_count * 0.005)
adjusted_struct = max(0.0, struct_score - struct_penalty)
print(f"  YAML validity: {struct_score:.4f}")
print(f"  Dirty SKILL.md penalty: -{struct_penalty:.4f} ({dirty_skill_count} files)")
print(f"  Structural (adjusted): {adjusted_struct:.4f}")

# ========================================
# SUMMARY with state comparison
# ========================================
print("\n" + "=" * 60)
print("SUMMARY")
with open(STATE_PATH) as f:
    state = json.load(f)

state_benchmark = state["dimensions"]["benchmark"]
state_structural = state["dimensions"]["structural"]

diff_b = abs(benchmark_raw - state_benchmark)
flag_b = "OVERCLAIM" if state_benchmark > benchmark_raw + 0.02 else "OK"

print(f"  State-claimed benchmark: {state_benchmark}")
print(f"  Actual benchmark: {benchmark_raw:.4f}")
print(f"  Benchmark diff: {diff_b:.4f} [{flag_b}]")
print(f"  State-claimed structural: {state_structural}")
print(f"  Actual structural: {adjusted_struct:.4f}")
print(f"  Structural diff: {abs(adjusted_struct - state_structural):.4f}")

overall = (adjusted_struct * 0.25 + benchmark_raw * 0.25 +
           1.0 * 0.15 + 1.0 * 0.15 + 1.0 * 0.10 + 1.0 * 0.10)
print(f"  Overall (recalculated): {overall:.4f}")
print(f"  State-claimed overall: {state['overall_score']}")

# JSON result for downstream processing
result = {
    "total_skills": total_skills,
    "atom_score": atom_score,
    "valid_yaml": valid_yaml,
    "invalid_yaml": invalid_yaml,
    "alias_errors": len(alias_errors),
    "no_opening": len(no_opening),
    "has_version": has_version,
    "has_signature": has_signature,
    "has_io_contract": has_io_contract,
    "v_pct": round(v_pct, 4),
    "s_pct": round(s_pct, 4),
    "io_pct": round(io_pct, 4),
    "benchmark_raw": round(benchmark_raw, 4),
    "tracked": tracked,
    "untracked": len(untracked_skills),
    "utf8_ok": utf8_ok,
    "dirty_skill_count": dirty_skill_count,
    "adjusted_struct": round(adjusted_struct, 4),
    "overall": round(overall, 4),
    "circular_pairs": len(circular_pairs),
    "skills_with_deps": len(deps),
}
print("\nJSON_RESULT:")
print(json.dumps(result, indent=2, ensure_ascii=False))
