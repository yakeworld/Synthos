# arXiv HTML Parsing Reference

## Key Parsing Pattern

arXiv new listing pages use `<dt>` blocks, each containing one paper entry. The structure is:

```html
<dt>
  <a name='item1'>[1]</a>
  <a href="/abs/2606.23699" title="Abstract">arXiv:2606.23699</a>
  ...
</dt>
<dd>
  ...
  <div class='list-title mathjax'>
    <span class='descriptor'>Title:</span>
    [actual paper title text]
  </div>
</dd>
```

## Critical Detail: Single Quotes in HTML Attributes

arXiv HTML uses **single quotes** for class attributes: `class='list-title mathjax'` and `class='descriptor'`.
Most regex engines default to double-quote matching. Must use `\x27` or escaped quotes.

## Working Python Pattern

```python
import re
blocks = re.split(r"<dt>", html)
for block in blocks[1:]:
    if "list-title" not in block: continue
    id_match = re.search(r"arXiv:(\d+\.\d+)", block)
    if not id_match: continue
    # Single quotes in HTML — class='descriptor'
    desc_match = re.search(r'class=[\x27"].*?Title:</span>.*?([^<]+)', block, re.DOTALL)
```

## Categories to Query
- cs.CV (Computer Vision) — primary for image/medical imaging/segmentation papers
- cs.AI (Artificial Intelligence) — for agent/RL/reasoning papers
- cs.LG (Machine Learning) — for modeling/ODE/ODE-related papers

## Rate Limits
- No auth required
- ~25 requests/min safe
- No API key needed unlike Semantic Scholar
