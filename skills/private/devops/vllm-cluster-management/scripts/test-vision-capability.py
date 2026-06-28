#!/usr/bin/env python3
"""Detect which vLLM node supports image_input (vision)."""
import requests

NODES = {
    "amax": "http://100.100.252.99:8000",
    "amax-1": "http://100.125.10.93:8000",
    "amax-fallback": "http://100.82.27.51:8000",
}

# Tiny 1x1 red PNG
TEST_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

for name, base in NODES.items():
    try:
        r = requests.post(
            f"{base}/v1/chat/completions",
            headers={"Authorization": "Bearer EMPTY", "Content-Type": "application/json"},
            json={
                "model": "qwen3.6-35b-nvfp4",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What color?"},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/png;base64,{TEST_IMAGE}"
                        }}
                    ]
                }],
                "max_tokens": 10
            },
            timeout=15
        )
        if r.status_code == 200:
            print(f"{name}: VISION OK")
        elif r.status_code == 400:
            err = r.json().get("error", {}).get("message", "")
            if "0 image" in err or "image" in err.lower():
                print(f"{name}: NO VISION - {err}")
            else:
                print(f"{name}: ERR - {err}")
        else:
            print(f"{name}: HTTP {r.status_code}")
    except Exception as e:
        print(f"{name}: EXCEPTION - {e}")
