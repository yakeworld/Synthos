#!/usr/bin/env python3
"""
OpenML Benchmark Fetcher
Fetches and analyzes benchmark results from OpenML for a given dataset.
Usage: python openml_benchmark_fetcher.py <data_id> [num_runs] [target_accuracy] [target_f1]

Example:
    python openml_benchmark_fetcher.py 37 100 0.7642 0.6857
"""

import subprocess
import json
import sys


def fetch_run_details(run_id):
    """Fetch detailed run results from OpenML API."""
    result = subprocess.run(
        ['curl', '-s', f'https://www.openml.org/api/v1/json/run/{run_id}'],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
        return data.get('run', {})
    except json.JSONDecodeError:
        return None


def extract_metrics(run_data):
    """Extract key performance metrics from run evaluation data."""
    if not run_data:
        return None

    evaluations = run_data.get('output_data', {}).get('evaluation', [])
    metrics = {}

    for eval_item in evaluations:
        name = eval_item.get('name')
        value = eval_item.get('value')
        if name and value is not None:
            try:
                metrics[name] = float(value)
            except (ValueError, TypeError):
                pass

    accuracy = metrics.get('predictive_accuracy') or metrics.get('mean_accuracy')
    f1 = metrics.get('f_measure')
    auc = metrics.get('area_under_roc_curve')
    recall = metrics.get('recall')
    precision = metrics.get('precision')

    if accuracy is None and f1 is None:
        return None

    return {
        'accuracy': accuracy or 0,
        'f1': f1 or 0,
        'auc': auc or 0,
        'recall': recall or 0,
        'precision': precision or 0,
    }


def fetch_benchmark_results(data_id, num_runs=500, sample_every=20):
    """Fetch benchmark results for a dataset from OpenML."""
    # Get task list
    result = subprocess.run(
        ['curl', '-s', f'https://www.openml.org/api/v1/json/task/list/data_id/{data_id}/status/active'],
        capture_output=True, text=True, timeout=30
    )
    data = json.loads(result.stdout)
    tasks = data.get('tasks', {}).get('task', [])

    if not tasks:
        print(f"No tasks found for data_id {data_id}")
        return []

    # Get the first classification task
    task_id = tasks[0].get('task_id')
    if not task_id:
        # Try to find a Supervised Classification task
        for t in tasks:
            if t.get('task_type') == 'Supervised Classification':
                task_id = t.get('task_id')
                break

    if not task_id:
        print("No classification task found")
        return []

    # Get runs for the task
    result = subprocess.run(
        ['curl', '-s', f'https://www.openml.org/api/v1/json/run/list/task/{task_id}/limit/{num_runs}'],
        capture_output=True, text=True, timeout=30
    )
    data = json.loads(result.stdout)
    runs = data.get('runs', {}).get('run', [])

    print(f"Found {len(runs)} runs for task {task_id}")

    # Sample runs
    sampled = runs[::sample_every] if len(runs) > num_runs else runs
    print(f"Sampling every {sample_every}th run: {len(sampled)} runs")

    # Fetch details for sampled runs
    results = []
    for i, run in enumerate(sampled):
        run_id = run.get('run_id')
        run_data = fetch_run_details(run_id)
        if run_data:
            metrics = extract_metrics(run_data)
            if metrics:
                results.append({
                    'run_id': run_id,
                    'flow_name': run_data.get('flow_name', 'Unknown'),
                    'task_id': task_id,
                    **metrics
                })
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{len(sampled)} runs...")

    return results


def print_report(results, target_accuracy=None, target_f1=None):
    """Print benchmark comparison report."""
    if not results:
        print("No results to report")
        return

    accuracies = [r['accuracy'] for r in results if r['accuracy'] > 0]
    f1_scores = [r['f1'] for r in results if r['f1'] > 0]

    print("\n" + "=" * 80)
    print("OpenML Benchmark Report")
    print("=" * 80)
    print(f"Total samples: {len(results)}")
    print(f"Valid samples: {len(accuracies)}")

    if accuracies:
        print(f"\nAccuracy Statistics:")
        print(f"  Max: {max(accuracies):.4f}")
        print(f"  Mean: {sum(accuracies)/len(accuracies):.4f}")
        print(f"  Min: {min(accuracies):.4f}")

    if f1_scores:
        print(f"\nF1 Statistics:")
        print(f"  Max: {max(f1_scores):.4f}")
        print(f"  Mean: {sum(f1_scores)/len(f1_scores):.4f}")
        print(f"  Min: {min(f1_scores):.4f}")

    if target_accuracy:
        acc_rank = sum(1 for a in accuracies if a > target_accuracy) + 1
        acc_percentile = 100 * (1 - acc_rank / len(accuracies)) if accuracies else 0
        print(f"\nTarget Accuracy: {target_accuracy}")
        print(f"  Rank: {acc_rank}/{len(accuracies)}")
        print(f"  Percentile: {acc_percentile:.1f}%")

    if target_f1:
        f1_rank = sum(1 for f in f1_scores if f > target_f1) + 1
        f1_percentile = 100 * (1 - f1_rank / len(f1_scores)) if f1_scores else 0
        print(f"\nTarget F1: {target_f1}")
        print(f"  Rank: {f1_rank}/{len(f1_scores)}")
        print(f"  Percentile: {f1_percentile:.1f}%")

    # Top models
    print(f"\nTop 10 Models by Accuracy:")
    print("-" * 80)
    print(f"{'Rank':<6} {'Run ID':<8} {'Flow Name':<35} {'Accuracy':<10} {'F1':<8} {'AUC':<10}")
    print("-" * 80)

    sorted_results = sorted(results, key=lambda x: x['accuracy'], reverse=True)
    for i, r in enumerate(sorted_results[:10], 1):
        print(f"{i:<6} {r['run_id']:<8} {r['flow_name'][:35]:<35} "
              f"{r['accuracy']:<10.4f} {r['f1']:<8.4f} {r.get('auc', 0):<10.4f}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python openml_benchmark_fetcher.py <data_id> [num_runs] [target_accuracy] [target_f1]")
        sys.exit(1)

    data_id = sys.argv[1]
    num_runs = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    target_accuracy = float(sys.argv[3]) if len(sys.argv) > 3 else None
    target_f1 = float(sys.argv[4]) if len(sys.argv) > 4 else None

    results = fetch_benchmark_results(data_id, num_runs)
    print_report(results, target_accuracy, target_f1)


if __name__ == '__main__':
    main()
