# Cron Job State Persistence Pattern

## Problem

Cron jobs that produce sequential/iterative output (e.g., daily promo posts cycling through feature numbers 1-20) have no persistent state. When a job fails (timeout, crash), the next run has no way to know what number was last posted without extensive reconstruction from:
1. Cron output files (`~/.hermes/cron/output/<job_id>/<date>.md`)
2. Session DB (`session_search`)
3. Manual investigation of cron job configs

## Case Study: synthos-daily-promo (2026-06-25)

The June 25 run of `synthos-daily-promo` timed out before producing output. The June 26 run had to:
1. Check cron output directory for any successful run markers
2. Search session DB for previous feature posts
3. Confirm no state file exists
4. Decide to start from Feature #1 (since no successful post was recorded)

**Root cause**: The cron job prompt says "记录上次发的功能编号" (record last posted feature number) but there is NO mechanism to actually do this. The agent is asked to remember but has no durable state to write to.

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
