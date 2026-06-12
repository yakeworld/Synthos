# HuggingFace Mirror Workaround (China Network)

## Problem
HuggingFace (`huggingface.co`) is unreachable from mainland China networks — DNS resolves to `strategicts.net` (a GFW redirection IP) with an expired/incorrect SSL certificate. All `huggingface_hub` API calls and `curl` requests fail with `CERTIFICATE_VERIFY_FAILED` or connection timeout.

## Fix
Set `HF_ENDPOINT` environment variable to the Chinese mirror:

```bash
export HF_ENDPOINT="https://hf-mirror.com"
```

Apply for all Python calls:

```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from huggingface_hub import hf_hub_download, HfApi
# All calls now go through hf-mirror.com
```

For `curl`:
```bash
curl -skL "https://hf-mirror.com/api/datasets/{org}/{repo}"
```

## Verified Working (2026-05-12)
- Dataset download: `ScaleAI/researchrubrics` — 865KB JSONL, success
- Dataset listing: `Tevatron/browsecomp-plus` — parquet files accessible
- API listing: `hf-mirror.com/api/...` — returns valid JSON

## Not Working
- HuggingFace Spaces (`hf.co/spaces/...`) — may redirect back to the main domain
- Direct `huggingface.co` without mirror — will fail from Chinese networks

## Note
The `hf-mirror.com` certificate is valid (unlike the `strategicts.net` redirection). SSL verification succeeds on hf-mirror.com.
