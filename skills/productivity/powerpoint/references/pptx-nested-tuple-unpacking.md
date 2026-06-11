# Nested Tuple Unpacking Pitfall — PPTX Loop Generation

**Date discovered:** 2026-06-11
**Source:** 瓯越英才PPT generation (P9 未来研究计划与预期效益)

## The Trap

When generating multi-section PPTX content with nested tuple data like:

```python
data = [
    (2.1, "Title", [("line1", 11, WHITE), ("line2", 11, DIM)]),
    (3.7, "Title2", [("line1", 11, WHITE)]),
]
```

**Wrong:**
```python
# enumerate adds index → 4 values unpacked into 3 slots
for i, (ypos, title, lines) in enumerate(data):
    # ValueError: too many values to unpack (expected 3)
    # enumerate yields (0, (2.1, "Title", [...])) → i, then (2.1, "Title", [...])
    # unpacked to: i=(0), (ypos=2.1, title="Title", lines=[...])
    # Result: 4 values, 3 slots → FAIL

# Wrong: unpack 4 values into 3 slots
for i, title, lines, ypos in data:
    # ValueError: not enough values to unpack (expected 4, got 3)
    # enumerate yields (0, (2.1, "Title", [...])) → unpacked as i, title, lines, ypos
    # i=0, title=(2.1, "Title", [...]), lines=???, ypos=??? → FAIL
```

**Correct:**
```python
# Remove enumerate, iterate directly — tuple matches slots exactly
for (ypos, title, lines) in data:
    # 3 values → 3 slots → works
    print(ypos, title, lines)
```

## Rule

**Never combine `enumerate()` with multi-variable tuple unpacking on the same target.**
`enumerate` wraps the tuple, increasing the unpack count by 1. Either:
1. `for (a, b, c) in data:` — direct iteration, or
2. `for i, item in enumerate(data): ypos, title, lines = item` — unpack after

## Related

See references/pptx-generation-template.md for the full PPTX loop pattern.
