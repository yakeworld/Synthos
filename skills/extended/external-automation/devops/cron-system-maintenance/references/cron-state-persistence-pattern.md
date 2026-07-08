# Cron Job State Persistence Pattern

## Problem

Cron jobs that produce sequential/iterative output (e.g., daily promo posts cycling through feature numbers 1-20) have no persistent state. When a job fails (timeout, crash), the next run has no way to know what number was last posted without extensive reconstruction from:
1. Cron output files (`~/.hermes/cron/output/<job_id>/<date>.md`)
2. Session DB (`session_search`)
3. Manual investigation of cron job configs

## Case Study: synthos-daily-promo (2026-06-25)
The June 25 run timed out before producing output. June 26 run had to reconstruct state from output files + session DB.

## Case Study: synthos-daily-promo (2026-07-07)
Previous run calculated rotation as "Day 32 mod 10 = 2 -> Slot 3" which was WRONG. The actual daily progression from cron output files showed: 07-03=#1, 07-04=#2, 07-05=#3, 07-06=#4, 07-07=#5 (文献监控). Modular arithmetic failed because it did not account for the actual first day correctly.

## Case Study: synthos-daily-promo (2026-07-08)
This run also failed to reconstruct the rotation correctly. The correct approach: read the most recent successful output file and extract the function number from its title, then increment by 1. More reliable than any modular arithmetic.

## Key Lesson: NEVER rely on date arithmetic for cron job rotation.
Date-based calculations are fragile (leap years, timezone issues, DST, missed runs, off-by-one errors, ambiguous first day). Always derive state from actual output files. The most recent successful output file IS the source of truth.

## Fix: Option C - Embed state check in cron prompt
Add a state-check step to the cron job prompt:
1. Check if the state file exists
2. Read the number, increment it
3. Use this as your feature number
4. Write the new number back to the file
5. If the file does not exist, start from 1

## Fix Patterns

### Option A: State file in cron output directory
Create a `state.json` or `next_number.txt` in the job's output directory. Next run reads this, increments, posts, updates the file.

### Option B: State file in a known shared location
Create a file at a well-known path like `~/.hermes/cron/state/daily-promo/next_number.txt`. All promo jobs reference this single file.

### Option C: Embed state check in cron prompt
Add to the cron job prompt:
1. Check if the state file exists
2. Read the number, increment it
3. Use this as your feature number
4. Write the new number back to the file
5. If the file doesn't exist, start from 1

## Recommendation

Option C is the most robust because state lives with the job, no external dependency on shared state, and if state is lost defaulting to 1 is safe. For `synthos-daily-promo`, the prompt should be updated to include this state check as a required first step.
