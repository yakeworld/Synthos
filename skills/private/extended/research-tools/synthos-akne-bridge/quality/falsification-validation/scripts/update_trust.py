#!/usr/bin/env python3
"""
Automated Bayesian Trust Update Script

Usage:
  python3 update_trust.py --skill-name <name> --result pass/fail [--metrics "metric1:val1 metric2:val2"]

Updates trust score using Bayes theorem based on test results.
"""
import argparse
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRUST_SYSTEM = os.path.join(BASE_DIR, "trust-system.json")

# Default trust values
DEFAULT_PRIORS = {
    "knowledge-acquisition": 0.8,
    "knowledge-extraction": 0.7,
    "association-discovery": 0.6,
    "hypothesis-generation": 0.5,
    "argument-expression": 0.6,
    "viewpoint-verification": 0.5,
    "task-router": 0.7,
}

def load_trust_system():
    with open(TRUST_SYSTEM, 'r') as f:
        return json.load(f)

def save_trust_system(trust_system):
    with open(TRUST_SYSTEM, 'w') as f:
        json.dump(trust_system, f, indent=2, ensure_ascii=False)

def update_trust(skill_name, test_result, metrics=None):
    """Update trust score using Bayes theorem."""
    trust_system = load_trust_system()
    
    if skill_name not in trust_system['skills']:
        print(f"Error: {skill_name} not found in trust system")
        return False
    
    skill = trust_system['skills'][skill_name]
    
    # Get prior trust
    prior = skill.get('current_trust', DEFAULT_PRIORS.get(skill_name, 0.5))
    
    # Calculate likelihood based on test result and metrics
    if test_result == 'pass':
        if metrics:
            # Calculate average metric score as likelihood
            metric_scores = [float(v.split(':')[1]) for v in metrics.split()]
            likelihood = sum(metric_scores) / len(metric_scores)
        else:
            likelihood = 0.8  # Default likelihood for pass
        
        # Apply bonus for consecutive successes
        consecutive = skill.get('consecutive_successes', 0)
        if consecutive >= 3:
            likelihood = min(1.0, likelihood + 0.1)
            
    else:  # fail
        likelihood = 0.2  # Low likelihood for failure
        
        # Apply penalty for consecutive failures
        consecutive = skill.get('consecutive_failures', 0)
        if consecutive >= 3:
            likelihood = max(0.0, likelihood - 0.2)
    
    # Calculate posterior using Bayes theorem
    # P(A|B) = P(B|A) * P(A) / P(B)
    # P(B) = P(B|A)*P(A) + P(B|not A)*P(not A)
    # For simplicity: P(B|not A) = 1 - P(B|A)
    
    posterior = (likelihood * prior) / (likelihood * prior + (1 - likelihood) * (1 - prior))
    
    # Clamp to [0, 1]
    posterior = max(0.0, min(1.0, posterior))
    
    # Update skill data
    skill['current_trust'] = round(posterior, 4)
    skill['tests_run'] = skill.get('tests_run', 0) + 1
    skill['tests_failed' if test_result == 'fail' else 'tests_passed'] = \
        skill.get('tests_failed' if test_result == 'fail' else 'tests_passed', 0) + 1
    
    # Track consecutive successes/failures
    if test_result == 'pass':
        skill['consecutive_successes'] = skill.get('consecutive_successes', 0) + 1
        skill['consecutive_failures'] = 0
    else:
        skill['consecutive_failures'] = skill.get('consecutive_failures', 0) + 1
        skill['consecutive_successes'] = 0
    
    # Add test history
    test_entry = {
        'timestamp': datetime.now().isoformat(),
        'test_result': test_result,
        'metrics': metrics,
        'prior': prior,
        'likelihood': round(likelihood, 4),
        'posterior': round(posterior, 4),
        'update_direction': 'positive' if posterior > prior else 'negative'
    }
    
    if 'test_history' not in skill:
        skill['test_history'] = []
    skill['test_history'].append(test_entry)
    
    save_trust_system(trust_system)
    
    print(f"Updated {skill_name}:")
    print(f"  Result: {test_result}")
    print(f"  Prior: {prior:.4f}")
    print(f"  Likelihood: {likelihood:.4f}")
    print(f"  Posterior: {posterior:.4f}")
    print(f"  Change: {'+' if posterior > prior else ''}{posterior - prior:.4f}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Update Bayesian trust score')
    parser.add_argument('--skill-name', required=True, help='Name of the skill')
    parser.add_argument('--result', required=True, choices=['pass', 'fail'], help='Test result')
    parser.add_argument('--metrics', default=None, help='Metrics as space-separated key:value pairs')
    
    args = parser.parse_args()
    
    success = update_trust(args.skill_name, args.result, args.metrics)
    
    if success:
        print("✅ Trust update successful")
    else:
        print("❌ Trust update failed")
        exit(1)

if __name__ == '__main__':
    main()
