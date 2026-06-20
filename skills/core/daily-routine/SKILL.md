---
name: daily-routine
description: "Daily Routine Automation - Automates the super-individual daily workflow: email check, code review, task management, research tracking, skill maintenance. All automated, all traceable."
version: 1.0.0
author: Synthos
license: MIT
allowed-tools: shell (bash), Read (view), Write (write), task_delegation
metadata:
  synthos:
    priority: P1
    atom_type: cognitive_atom
    description: "Daily routine automation - orchestrates email, code, tasks, research, and skill maintenance into a single daily workflow"
    signature: "date: str -> daily_report: dict, actions: list[str]"
    related_skills:
      - apple-notes
      - apple-reminders
      - github-code-review
      - productivity
      - evolution
---

# Daily Routine Automation (日常自动化)

## Core Positioning

> **一日之计在于晨，一年之计在于春。** A super individual does not react - they proactively manage. Daily automation ensures nothing falls through the cracks.

Goal: Create an automated daily workflow that handles email, code review, task management, research tracking, and skill maintenance - all traceable through the evolution log.

## IO_CONTRACT

- **input**: date: str - Date for the daily run (defaults to today)
- **output**: daily_report: dict - Summary of all automated actions
- **output**: actions: list[str] - List of actions taken (for audit trail)
- **output**: pending_items: list[dict] - Items requiring human review

## Daily Workflow

### 06:00 - Morning Check

1. **Email Scan** (if email integration available)
   - Check for new emails since last run
   - Flag urgent/important items
   - Generate email summary

2. **Research Pulse**
   - Check Semantic Scholar/arXiv for new papers in key domains
   - Flag papers matching current research topics
   - Queue for ACQ (knowledge acquisition)

3. **Code Health**
   - Check Git status (uncommitted changes, new files)
   - Run quick YAML/Markdown validation
   - Flag broken references or files

### 09:00 - Deep Work Preparation

4. **Task Triage**
   - Review pending tasks from Apple Reminders
   - Prioritize by: deadlines > impact > effort
   - Update task state in knowledge system

5. **Research Priority**
   - Check paper pipeline status
   - Identify papers ready for submission
   - Flag papers needing attention

6. **Skill Maintenance**
   - Run quick structural probe on all SKILL.md files
   - Check for YAML validity
   - Flag any drifted references

### 12:00 - Midday Sync

7. **Progress Check**
   - Update evolution log with morning actions
   - Check if any evolution cycles need resuming
   - Generate midday progress report

8. **Social/Network Pulse** (optional)
   - Check Twitter/LinkedIn for mentions
   - Track relevant research discussions
   - Flag engagement opportunities

### 18:00 - Evening Wrap

9. **Daily Summary**
   - Compile all morning + afternoon actions
   - Generate daily summary report
   - Update personal knowledge base

10. **Tomorrow Prep**
    - Identify top 3 priorities for tomorrow
    - Queue any automated tasks
    - Record daily state in evolution log

## Quality Control

- P0 Evidence traceability: Every action recorded in evolution log
- P1 Atomic reproducibility: Each daily step independently executable
- P2 Stability sinking: Validated daily patterns become standard
- P3 Human-machine layering: Human reviews all flags and decisions

## Output Files

- outputs/daily/{date}.md - Daily summary report
- outputs/daily/{date}.json - Structured daily data
- .evolution/reviews/daily/{date}/audit.md - Daily audit trail

---

*一日三省吾身。自动化不是替代，是增强。*
