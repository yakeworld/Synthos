# Synthos Skill Location Migration — 2026-05-31

## Why

Synthos is an independent research OS, not tied to any specific Agent. Skills should live in the Synthos repo (`Synthos/skills/`), not in `~/.hermes/skills/` (Hermes Agent's private directory).

This makes Synthos:
- **Portable**: clone the repo and get all skills
- **Agent-agnostic**: works with any Agent supporting external skill directories
- **Version-controlled**: skills evolve together with the system

## Migration steps

```bash
# 1. Copy skill to Synthos repo
cp -r ~/.hermes/skills/<skill> /media/yakeworld/sda2/Synthos/skills/

# 2. Remove from Hermes
rm -rf ~/.hermes/skills/<skill>

# 3. Configure external_dirs
# ~/.hermes/config.yaml
# skills:
#   external_dirs:
#     - /media/yakeworld/sda2/Synthos/skills
```

## What was moved

| Count | Detail |
|:-----:|:-------|
| 126 | Synthos core skills to `Synthos/skills/` (via shutil.move) |
| 22 | Non-core skills moved back to `~/.hermes/skills/` |
| 2 | Merged (`devops/evolution → evolution`, `research-platform-philosophy → CAA`) |
| 1 | Relocated (`scc-bppv-kinematics` from Hermes to Synthos) |
| 121 | Final count in Synthos skills |

## Backup

- Backup of original Hermes skills: `~/.hermes/skills_bak_synthos_20260531/`
- Archived philosophy skill: `Synthos/skills/cognitive-atom-architecture/references/archived-research-platform-philosophy/`

## Verification

```bash
grep -A2 external_dirs ~/.hermes/config.yaml
find /media/yakeworld/sda2/Synthos/skills -name "SKILL.md" | wc -l
```
