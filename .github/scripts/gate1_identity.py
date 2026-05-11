#!/usr/bin/env python3
"""Gate 1: Validate AGENT_MANIFEST.yaml"""
import yaml, os, sys

path = 'AGENT_MANIFEST.yaml'
if not os.path.exists(path):
    print("MISSING")
    sys.exit(1)

with open(path) as f:
    data = yaml.safe_load(f)

agent = data.get('agent', {})
required = ['name', 'framework', 'capability']
for field in required:
    if field not in agent:
        print(f"MISSING_FIELD:{field}")
        sys.exit(1)

if not agent.get('verification', {}).get('self_test_passed', False):
    print("SELF_TEST_NOT_PASSED")
    sys.exit(1)

name = agent['name']
framework = agent['framework']
print(f"OK name={name} framework={framework}")
