#!/usr/bin/env python3
"""
Quick test: verify the script is syntactically valid.
"""
import py_compile
script = '/home/yakeworld/.hermes/skills/devops/vllm-cluster-management/scripts/verify-vllm-nodes.py'
try:
    py_compile.compile(script, doraise=True)
    print("OK: verify-vllm-nodes.py compiles without errors")
except Exception as e:
    print(f"ERROR: {e}")
    import sys; sys.exit(1)