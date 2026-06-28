# Path Redundancy Discovery — 2026-06-18

## Discovery

On 2026-06-18, during skill audit, found that `/home/yakeworld/Synthos/` is a symbolic link pointing to `/media/yakeworld/sda2/Synthos/`.

### Verification

```bash
# Same inode confirms same filesystem object
stat -c '%i' /home/yakeworld/Synthos/ /media/yakeworld/sda2/Synthos/
# Both show inode 178178

# Symlink target
ls -la /home/yakeworld/Synthos
# → /media/yakeworld/sda2/Synthos
```

### Impact

1. Scanning both paths for duplicate skills is meaningless — they are the same directory
2. Any script or config using `/home/yakeworld/Synthos/` or `/media/yakeworld/sda2/Synthos/` works identically
3. Current convention: use `/media/yakeworld/sda2/Synthos/` in scripts, `/home/yakeworld/Synthos/` in interactive shells

### Resolution

- `/media/yakeworld/sda2/Synthos/` confirmed as canonical path (used in all scripts)
- `/home/yakeworld/Synthos/` can be removed without data loss (it is a symlink)
- `~/.hermes/skills/` is independent — 20 unique hermes runtime skills, not duplicated from Synthos
- Total skill count: 214 in Synthos + 20 in Hermes = 234 unique skills

### Recommendation

Delete `/home/yakeworld/Synthos` symlink to eliminate filesystem redundancy. Verify no config uses it before deletion.
