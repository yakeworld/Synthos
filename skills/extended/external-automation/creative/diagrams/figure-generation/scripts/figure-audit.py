#!/usr/bin/env python3
"""Paper figure integrity audit — reusable class-level script.

SKILL.md 原理绑定:
- 铁律：每张图必须有对应生成脚本（05-figures → 03-code/）
- 铁律：脚本必须引用真实数据文件，不可硬编码
- 铁律：输出文件时间戳必须比脚本新
- 铁律：QA必须运行（架构图检测框重叠/箭头终点）

对应模式：G（QA自动化）+ 铁律检查

Usage: python figure-audit.py /path/to/paper/root
"""
import os, json, re, sys

def audit_papers(base_dir):
    """Run full audit on a single paper directory.
    
    Returns dict of results for reporting.
    """
    exp_dir = os.path.join(base_dir, '03-code', 'experiments')
    fig_dir = os.path.join(base_dir, '05-figures')
    tex_dir = os.path.join(base_dir, '01-manuscript')
    
    results = {
        'figures': {},
        'scripts': {},
        'latex_refs': [],
        'errors': [],
        'warnings': [],
    }
    
    # 1. Collect figures
    if os.path.isdir(fig_dir):
        for f in os.listdir(fig_dir):
            if f.endswith(('.png', '.pdf', '.svg', '.jpg')):
                name = os.path.splitext(f)[0]
                if name not in results['figures']:
                    results['figures'][name] = {}
                ext = os.path.splitext(f)[1][1:]
                results['figures'][name][ext] = os.path.join(fig_dir, f)
    
    # 2. Collect scripts
    if os.path.isdir(exp_dir):
        for f in sorted(os.listdir(exp_dir)):
            if f.startswith('generate_fig') and f.endswith('.py'):
                name = f.replace('generate_', '').replace('.py', '')
                results['scripts'][name] = os.path.join(exp_dir, f)
    
    # 3. Check figure-to-script mapping
    for fig_name in results['figures']:
        status = 'PASS' if fig_name in results['scripts'] else 'FAIL'
        results['figures'][fig_name]['has_script'] = status
        if status == 'FAIL':
            results['errors'].append(f'Missing script for {fig_name}')
    
    # 4. Data integrity check
    for fig_name, script_path in results['scripts'].items():
        with open(script_path) as f:
            content = f.read()
        
        # Hardcoding detectors — these patterns indicate data baked into code
        hardcoded_patterns = [
            'worst_radius',           # feature importance
            'FEATURE_IMPORTANCE = [', # explicit hardcoding
            "models_data = {",        # model performance dict
            'models_data={',
            'DATA = [',
        ]
        is_hardcoded = any(pat in content for pat in hardcoded_patterns)
        
        # Legitimate data reference patterns
        data_ref_patterns = [
            'json.load', 'json.loads',
            'pd.read_csv', 'pd.read_json',
            'csv.reader', 'csv.DictReader',
            'np.load', 'np.loadtxt', 'np.loadtxt',
            'h5py', '.h5', '.hdf5',
            'experiment', 'fold_data',
            'results.json', 'results.csv',
        ]
        has_data_ref = any(pat in content for pat in data_ref_patterns)
        
        if is_hardcoded and not has_data_ref:
            results['scripts'][fig_name]['data_integrity'] = 'hardcoded'
            results['errors'].append(f'{fig_name}: hardcoded data — must read from data file')
        elif has_data_ref:
            results['scripts'][fig_name]['data_integrity'] = 'data_ref'
        else:
            # Check if it's purely synthetic or mock data
            has_import = any(x in content for x in ['import', 'from'])
            has_data = any(x in content for x in ['data', 'dataset', 'matrix', 'array', 'values'])
            if not has_import or not has_data:
                results['scripts'][fig_name]['data_integrity'] = 'no_data'
            else:
                results['scripts'][fig_name]['data_integrity'] = 'check_required'
        
        results['scripts'][fig_name]['has_savefig'] = 'savefig' in content
        results['scripts'][fig_name]['file_size'] = os.path.getsize(script_path)
    
    # 5. Timestamp check
    for fig_name, script_path in results['scripts'].items():
        script_mtime = os.path.getmtime(script_path)
        fig_files = results['figures'].get(fig_name, {})
        for ext, path in fig_files.items():
            if os.path.getmtime(path) < script_mtime:
                age = script_mtime - os.path.getmtime(path)
                results['warnings'].append(f'{fig_name}.{ext}: output {int(age)}s older than script')
    
    # 6. File validity check
    for fig_name, fig_files in results['figures'].items():
        for ext, path in fig_files.items():
            if os.path.getsize(path) == 0:
                results['errors'].append(f'{fig_name}.{ext}: empty file')
                continue
            with open(path, 'rb') as f:
                header = f.read(8)
            if ext == 'png' and header[:4] != b'\x89PNG':
                results['errors'].append(f'{fig_name}.{ext}: invalid PNG header')
            elif ext == 'pdf' and not header.startswith(b'%PDF'):
                results['errors'].append(f'{fig_name}.{ext}: invalid PDF header')
            elif ext == 'svg' and not (header.startswith(b'<?xm') or header.startswith(b'<svg')):
                results['errors'].append(f'{fig_name}.{ext}: invalid SVG header')
    
    # 7. LaTeX reference check
    for f in os.listdir(tex_dir) if os.path.isdir(tex_dir) else []:
        if f.endswith('.tex'):
            with open(os.path.join(tex_dir, f)) as fp:
                content = fp.read()
            refs = re.findall(r'includegraphics.*?fig(\\d+)', content)
            results['latex_refs'].extend(refs)
    
    return results


def print_report(results):
    """Print audit report to stdout."""
    print('=' * 60)
    print('Paper Figure Audit Report')
    print('=' * 60)
    
    print(f'\nTotal figures: {len(results["figures"])}')
    print(f'Total scripts: {len(results["scripts"])}')
    
    print('\nFigure → Script mapping:')
    for fig_name, info in sorted(results['figures'].items()):
        print(f'  {info["has_script"]} {fig_name}')
    
    print('\nData integrity:')
    for name, info in sorted(results['scripts'].items()):
        print(f'  {info["data_integrity"]:15s} {name}')
    
    if results['errors']:
        print(f'\nERRORS ({len(results["errors"])}):')
        for e in results['errors']:
            print(f'  FAIL {e}')
    
    if results['warnings']:
        print(f'\nWARNINGS ({len(results["warnings"])}):')
        for w in results['warnings']:
            print(f'  WARN {w}')
    
    if not results['errors'] and not results['warnings']:
        print('\nAll checks passed')
    
    print('\n' + '-' * 60)
    refs = set(results['latex_refs'])
    print(f'LaTeX references: {", ".join(sorted(refs)) if refs else "None"}')


if __name__ == '__main__':
    base = sys.argv[1] if len(sys.argv) > 1 else '/media/yakeworld/sda2/Synthos/outputs/papers'
    results = audit_papers(base)
    print_report(results)
