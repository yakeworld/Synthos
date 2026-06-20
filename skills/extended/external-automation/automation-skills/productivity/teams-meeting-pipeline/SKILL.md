---
name: teams-meeting-pipeline
description: "Redirect to productivity-suite skill."
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    atom_type: redirect
    priority: P3
    redirect_to: "productivity-suite"
    signature: "redirect -> productivity-suite"
    related_skills: []

---

# teams-meeting-pipeline

## Redirect

This skill redirects to the composite skill `productivity-suite`.

## Composite Skill

See `productivity-suite.md` for the full implementation.
## IO_CONTRACT

- **input**: `Skill request matching 'teams-meeting-pipeline'`
- **output**: `Redirect to productivity-suite skill`
- **redirect_target**: `productivity-suite`

> This is a redirect stub. For full implementation, see `productivity-suite`.
