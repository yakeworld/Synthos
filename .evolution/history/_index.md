# history/ — Evolution State Snapshots

Stores timestamped snapshots of previous evolution states. Each snapshot captures the
state before a significant evolution cycle, enabling rollback, diffing, and audit.

## Convention

Snapshots are named `YYYY-MM-DDThhmmssZ.json` (ISO 8601 UTC format).

## Usage

- The evolution engine saves a snapshot here before applying changes.
- Comparison with current `state.json` shows what changed.
- Rollback restores a snapshot to `state.json`.
