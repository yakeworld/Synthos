# Contributing to Synthos

Synthos is a pure SKILL.md-driven project — **no Python infrastructure code**. Contributions are welcome as cognitive atom skills.

## How to Contribute

1. **Add a new skill**: Create a `SKILL.md` under `skills/<category>/<skill-name>/` with YAML frontmatter + markdown body. Follow the three-tier language pattern (Classical Chinese principles → vernacular methods → English commands).

2. **Improve an existing skill**: Patch or rewrite the `SKILL.md` file. Ensure I/O contracts, triggers, and verification steps are updated.

3. **Report issues**: Open a GitHub issue describing the problem, expected behavior, and context.

## Skill Structure Convention

```
skills/<category>/<skill-name>/
├── SKILL.md              # Main skill definition
├── references/           # Supporting documents
└── templates/            # Output templates
```

## Principles

- **No Python** — all capabilities are declarative markdown
- **Epistemological honesty** — every claim must cite a verifiable source
- **Single responsibility** — each skill addresses exactly one cognitive operation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
