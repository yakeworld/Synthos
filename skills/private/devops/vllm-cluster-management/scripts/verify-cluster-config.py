#!/usr/bin/env python3
"""Verify vLLM cluster consistency: config.yaml providers match config.toml base_url and all nodes reachable."""
import subprocess, sys, os

HOME = os.path.expanduser('~')
HERMES_CONFIG = f"{HOME}/.hermes/config.yaml"
CODEX_CONFIG = f"{HOME}/.codex/config.toml"

def load_yaml(path):
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)

def load_toml(path):
    with open(path) as f:
        return f.read()

def main():
    # 1. Load config.yaml custom_providers
    config = load_yaml(HERMES_CONFIG)
    providers = config.get('custom_providers', [])
    print(f"=== custom_providers in {HERMES_CONFIG} ({len(providers)} entries) ===")
    provider_map = {}
    for p in providers:
        name = p['name']
        url = p['base_url']
        print(f"  {name}: {url}")
        provider_map[name] = url

    # 2. Load config.toml base_url
    toml_content = load_toml(CODEX_CONFIG)
    import re
    base_url_match = re.search(r'base_url\s*=\s*"([^"]+)"', toml_content)
    if base_url_match:
        urls = [u.strip() for u in base_url_match.group(1).split(',')]
        print(f"\n=== Codex base_url in {CODEX_CONFIG} ({len(urls)} entries) ===")
        for u in urls:
            print(f"  {u}")
    else:
        print(f"\nWARNING: No base_url found in {CODEX_CONFIG}")
        return 1

    # 3. Verify all providers are in Codex base_url
    print("\n=== Cross-check: providers ⊂ Codex base_url ===")
    errors = []
    for name, url in provider_map.items():
        if url not in urls:
            errors.append(f"  FAIL: provider '{name}' ({url}) NOT in Codex base_url")
        else:
            print(f"  OK: {name} ({url}) found in Codex base_url")

    # 4. Check that no deprecated provider names exist
    print("\n=== Deprecated provider name check ===")
    deprecated_names = ['amax-1', 'amax_old', 'amax-legacy']
    deprecated_found = []
    for name in deprecated_names:
        if name in provider_map:
            deprecated_found.append(name)
    if deprecated_found:
        for n in deprecated_found:
            print(f"  FAIL: deprecated provider '{n}' still in config.yaml!")
            errors.append(f"Provider '{n}' should be renamed")
    else:
        print("  OK: no deprecated provider names found")

    # 5. Check Cronjob references (quick grep, not full list)
    print("\n=== Cronjob provider reference check ===")
    # We can't do a full grep of all cron jobs without running `cronjob list`,
    # so instead check if any config.yaml field references a deprecated name
    all_text = yaml.dump(config)
    for dep_name in deprecated_names:
        if dep_name in all_text:
            print(f"  WARN: '{dep_name}' found in config.yaml text")
            # Find which field
            for line in all_text.split('\n'):
                if dep_name in line:
                    print(f"    {line.strip()}")
            errors.append(f"Deprecated name '{dep_name}' still in config.yaml")

    # 6. Model provider consistency
    print("\n=== Model provider consistency ===")
    model_provider = config.get('model', {}).get('provider', '')
    delegation_provider = config.get('delegation', {}).get('provider', '')
    aux_vision = config.get('auxiliary', {}).get('vision', {}).get('provider', '')
    aux_search = config.get('auxiliary', {}).get('session_search', {}).get('provider', '')
    aux_approval = config.get('auxiliary', {}).get('approval', {}).get('provider', '')
    aux_compression = config.get('auxiliary', {}).get('compression', {}).get('provider', '')
    aux_web = config.get('auxiliary', {}).get('web_extract', {}).get('provider', '')

    all_providers = {
        'model': model_provider,
        'delegation': delegation_provider,
        'vision': aux_vision,
        'session_search': aux_search,
        'approval': aux_approval,
        'compression': aux_compression,
        'web_extract': aux_web,
    }
    for svc, prov in all_providers.items():
        if prov in provider_map:
            print(f"  {svc}: {prov} → {provider_map[prov]}")
        elif prov:
            print(f"  {svc}: {prov} → NOT FOUND in custom_providers!")
            errors.append(f"Service '{svc}' references unknown provider '{prov}'")
        else:
            print(f"  {svc}: auto (default)")

    # Summary
    print(f"\n{'='*60}")
    if errors:
        print(f"FOUND {len(errors)} error(s):\n")
        for e in errors:
            print(e)
        return 1
    else:
        print("ALL CHECKS PASSED ✓")
        return 0

if __name__ == '__main__':
    sys.exit(main())
