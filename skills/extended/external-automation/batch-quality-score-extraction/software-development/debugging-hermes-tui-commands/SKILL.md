---
name: debugging-hermes-tui-commands
description: 'Debug Hermes TUI slash commands: Python, gateway, Ink UI.'
version: 1.0.0
allowed-tools:
- terminal
- file
- read_file
license: MIT
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
    - debugging
    - hermes-agent
    - tui
    - slash-commands
    - typescript
    - python
    related_skills:
    - python-debugpy
    - node-inspect-debugger
    - systematic-debugging
  synthos:
    author: Hermes Agent
    signature: 'command_error: str -> fix: str'
    related_skills:
    - agent-orchestration-harness
    - embedded-python-modularization
    - github-agent-contributions
    - hermes-agent-skill-authoring
    - k230-canmv-debugging
    version: 1.0.0

---



# Debugging Hermes TUI Slash Commands

## Overview

Hermes slash commands span three layers — Python command registry, tui_gateway JSON-RPC bridge, and the Ink/TypeScript frontend. When a command misbehaves (missing from autocomplete, works in CLI but not TUI, config persists but UI doesn't update), the bug is almost always one layer being out of sync with another.

Use this skill when you encounter issues with slash commands in the Hermes TUI, particularly when commands aren't showing in autocomplete, aren't working properly in the TUI, or need to be added/updated.

## When to Use

- A slash command exists in one part of the codebase but doesn't work fully
- A command needs to be added to both backend and frontend
- Command autocomplete isn't working for specific commands
- Command behavior is inconsistent between CLI and TUI
- A command persists config but doesn't apply live in the TUI

## Architecture Overview

```
Python backend (hermes_cli/commands.py)     <- canonical COMMAND_REGISTRY
       │
       ▼
TUI gateway (tui_gateway/server.py)         <- slash.exec / command.dispatch
       │
       ▼
TUI frontend (ui-tui/src/app/slash/)        <- local handlers + fallthrough
```

Command definitions must be registered consistently across Python and TypeScript to work properly. The Python `COMMAND_REGISTRY` is the source of truth for: CLI dispatch, gateway help, Telegram BotCommand menu, Slack subcommand map, and autocomplete data shipped to Ink.

## Investigation Steps

1. **Check if the command exists in the TUI frontend:**
   ```bash
   search_files --pattern "/commandname" --file_glob "*.ts" --path ui-tui/
   search_files --pattern "/commandname" --file_glob "*.tsx" --path ui-tui/
   ```

2. **Examine the TUI command definition:**
   ```bash
   read_file ui-tui/src/app/slash/commands/core.ts
   # If not there:
   search_files --pattern "commandname" --path ui-tui/src/app/slash/commands --target files
   ```

3. **Check if the command exists in the Python backend:**
   ```bash
   search_files --pattern "CommandDef" --file_glob "*.py" --path hermes_cli/
   search_files --pattern "commandname" --path hermes_cli/commands.py --context 3
   ```

4. **Examine the gateway implementation:**
   ```bash
   search_files --pattern "complete.slash|slash.exec" --path tui_gateway/
   ```

## Fix: Missing Command Autocomplete

If a command exists in the TUI but doesn't show in autocomplete:

1. Add a `CommandDef` entry to `COMMAND_REGISTRY` in `hermes_cli/commands.py`:
   ```python
   CommandDef("commandname", "Description of the command", "Session",
              cli_only=True, aliases=("alias",),
              args_hint="[arg1|arg2|arg3]",
              subcommands=("arg1", "arg2", "arg3")),
   ```

2. Pick `cli_only` vs gateway availability carefully:
   - `cli_only=True` — only in the interactive CLI/TUI
   - `gateway_only=True` — only in messaging platforms
   - neither — available everywhere
   - `gateway_config_gate="display.foo"` — config-gated availability in the gateway

3. Ensure `subcommands` matches the expected tab-completion options shown by the TUI.

4. If the command runs server-side, add a handler in `HermesCLI.process_command()` in `cli.py`:
   ```python
   elif canonical == "commandname":
       self._handle_commandname(cmd_original)
   ```

5. For gateway-available commands, add a handler in `gateway/run.py`:
   ```python
   if canonical == "commandname":
       return await self._handle_commandname(event)
   ```

## Common Issues

1. **Command shows in TUI but not in autocomplete.** The command is defined in the TUI codebase but missing from `COMMAND_REGISTRY` in `hermes_cli/commands.py`. Autocomplete data ships from Python.

2. **Command shows in autocomplete but doesn't work.** Check the command handler in `tui_gateway/server.py` and the frontend handler in `ui-tui/src/app/createSlashHandler.ts`. If the command is local-only in Ink, it must be handled in `app.tsx` built-in branch; otherwise it falls through to `slash.exec` and must have a Python handler.

3. **Command behavior differs between CLI and TUI.** The command might have different implementations. Check both `cli.py::process_command` and the TUI's local handler. Local TUI handlers take precedence over gateway dispatch.

4. **Command persists config but doesn't apply live.** For TUI-local commands, updating `config.set` is not enough. Also patch the relevant nanostore state immediately (usually `patchUiState(...)`) and pass any new state through rendering components. Example: `/details collapsed` must update live detail visibility, not just save `details_mode`; in-session global `/details <mode>` may need a separate command-override flag so live commands can override built-in section defaults while startup/config sync preserves default-expanded thinking/tools behavior.

5. **Gateway dispatch silently ignores the command.** The gateway only dispatches commands it knows about. Check `GATEWAY_KNOWN_COMMANDS` (derived from `COMMAND_REGISTRY

... (内容截断，详见 references/)