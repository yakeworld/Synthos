# NotebookLM CLI Quick Reference

## Most Common Commands

```bash
# Setup
notebooklm login                          # OAuth via browser

# Daily workflow
notebooklm use <partial_id>               # Select notebook (first 6-8 chars)
notebooklm source list                    # See what sources are loaded
notebooklm ask "question"                 # Ask (auto multi-turn)
notebooklm history                        # View conversation log
notebooklm history --save                 # Save chat as a note
notebooklm status                         # Check active context
```

## Quick Operations

| Task | Command |
|------|---------|
| List notebooks | `notebooklm list` |
| Create notebook | `notebooklm create "Title"` |
| Add source file | `notebooklm source add file.md` |
| Add Google Drive | `notebooklm source add-drive` |
| Add YouTube | `notebooklm source add <url>` |
| Summarize notebook | `notebooklm summary` |
| Generate report | `notebooklm generate report "prompt"` |
| Generate audio | `notebooklm generate audio "prompt"` |
| Download artifact | `notebooklm artifact download report <id>` |
| Share with user | `notebooklm share add email@domain.com` |
| Search sources | `notebooklm source fulltext "keyword"` |
| Switch context | `notebooklm clear` |

## Notes
- All commands operate on the active notebook (set via `notebooklm use`).
- Storage state defaults to `~/.notebooklm/storage_state.json`.
- Use `--storage PATH` to specify a different state file (e.g., for a different Google account).
- Artifact generation may take time; use `notebooklm artifact wait <type> <id>` to poll.
