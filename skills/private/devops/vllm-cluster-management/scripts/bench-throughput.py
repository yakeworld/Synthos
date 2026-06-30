#!/usr/bin/env python3
"""Benchmark vLLM throughput on a node for TP sizing comparison."""
import json, time
from urllib.request import Request, urlopen

BASE = "http://100.125.10.93:8000/v1/chat/completions"
AUTH=*** ***"
MODEL = "qwen3.6-35b-nvfp4"

def chat(messages, max_tokens=64, temp=0.1):
    data = json.dumps({
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temp,
        "stream": False,
    }).encode()
    req = Request(BASE, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": AUTH,
    })
    t0 = time.time()
    resp = urlopen(req, timeout=120)
    elapsed = time.time() - t0
    result = json.loads(resp.read())
    u = result["usage"]
    completion_tokens = u["completion_tokens"]
    throughput = completion_tokens / elapsed if elapsed > 0 else 0
    return {
        "elapsed_s": round(elapsed, 2),
        "completion_tokens": completion_tokens,
        "throughput_tok_s": round(throughput, 1),
    }

print("vLLM Throughput Benchmark")
# Short prompt, medium output
r = chat([{"role": "user", "content": "Write a paragraph about AI in healthcare"}], max_tokens=128, temp=0.7)
print(f"Short→Medium: {r['throughput_tok_s']} tok/s in {r['elapsed_s']}s")

# Medium prompt (~200 tok)
med = ("Here is a detailed description of the medical imaging pipeline for analyzing "
       "brain MRI scans. The pipeline consists of several stages: image preprocessing using "
       "NIfTI format handling, skull stripping with FSL BET algorithm, tissue segmentation "
       "using FAST tool, registration to MNI space using FNIRT, voxel-based morphometry "
       "analysis using FEAT, and statistical analysis using FLIRT and FSL. Each stage produces "
       "intermediate outputs that are validated against quality metrics. The pipeline handles "
       "multiple modalities including T1-weighted, T2-weighted, FLAIR, and diffusion-weighted "
       "images. Quality control includes visual inspection of registration overlays, checking of "
       "segmentation boundaries, and quantitative measures such as Dice coefficients for structural "
       "overlap. The final outputs include statistical parametric maps showing group differences, "
       "along with effect size estimates and confidence intervals. All processing steps are logged "
       "with timestamps and system resource utilization metrics for reproducibility and audit "
       "purposes.")
r = chat([{"role": "user", "content": med}], max_tokens=128, temp=0.7)
print(f"Med prompt→Medium: {r['throughput_tok_s']} tok/s in {r['elapsed_s']}s")
