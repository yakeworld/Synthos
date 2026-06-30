#!/usr/bin/env python3
"""
论文目录结构校验工具 — 递归检查所有子目录
自动检查论文目录是否符合标准结构 v2.0

用法: python3 paper_dir_validator.py <paper_dir>
输出: 校验结果（通过/失败）+ 失败详情

v2.0 变更：递归检查所有子目录内的文件命名和目录命名
"""

import os
import sys
import json

# ===== 根目录规则 =====
ALLOWED_ROOT_FILES = {'state.json', 'paper.tex', 'paper.pdf'}
STANDARD_DIRS = {
    '01-manuscript', '02-abstract', '03-introduction',
    '04-methods', '05-results', '06-discussion',
    '07-quality', '08-refs'
}

# ===== 禁止的文件模式 =====
FORBIDDEN_FILE_PATTERNS = [
    '.backup', '.bak', '_backup.',
    '.aux', '.log', '.out', '.blg', '.bbl', '.toc', '.spl',
    '.tmp', '.swp', '.swo',
]

# ===== 禁止的目录模式 =====
FORBIDDEN_DIR_PATTERNS = [
    'tmp', 'temp', 'cache', 'backup', 'archive',
    'experiment', 'figures', 'pdfs', 'refs-md',
    'catboost_info', '3wd-framework', 'critical-review',
    'step_', '01-gap_analysis', '02-submission',
    '03-code', '04-data', '05-figures',
    '06-references', '07-notes', '07-ref_check',
    '08-quality_check', '09-manuscript', '09-background',
]

# ===== 允许在子目录中的文件 =====
# 某些子目录允许放特定文件
ALLOWED_IN_01_MANUSCRIPT = {'paper.tex', 'references.bib', 'paper.aux', 'paper.log', 'paper.out', 'paper.bbl', 'paper.toc', 'paper.blg'}
ALLOWED_IN_04_METHODS_CODE = {'.py', '.ipynb'}
ALLOWED_IN_04_METHODS_DATA = {'.csv', '.json', '.tsv', '.txt', '.xlsx', '.h5', '.hdf5'}
ALLOWED_IN_05_RESULTS = {'.json', '.csv', '.txt', '.xlsx', '.h5', '.hdf5'}
ALLOWED_IN_05_RESULTS_FIGURES = {'.pdf', '.png', '.svg', '.jpg', '.jpeg'}
ALLOWED_IN_07_QUALITY = {'.md', '.json'}
ALLOWED_IN_08_REFS = {'.bib', '.pdf'}


def check_file_name(filename):
    """检查文件名是否包含禁止模式"""
    for pattern in FORBIDDEN_FILE_PATTERNS:
        if filename.endswith(pattern) or pattern in filename:
            return False, f"文件名包含禁止模式: {pattern}"
    return True, ""


def check_dir_name(dirname):
    """检查目录名是否包含禁止模式"""
    for pattern in FORBIDDEN_DIR_PATTERNS:
        if dirname.startswith(pattern) or pattern in dirname:
            return False, f"目录名包含禁止模式: {pattern}"
    return True, ""


def get_allowed_extensions(subdir_name):
    """获取子目录允许的文件扩展名"""
    ext_map = {
        '01-manuscript': ALLOWED_IN_01_MANUSCRIPT,
        '04-methods': ALLOWED_IN_04_METHODS_CODE,
        '04-methods/code': ALLOWED_IN_04_METHODS_CODE,
        '04-methods/data': ALLOWED_IN_04_METHODS_DATA,
        '05-results': ALLOWED_IN_05_RESULTS,
        '05-results/figures': ALLOWED_IN_05_RESULTS_FIGURES,
        '07-quality': ALLOWED_IN_07_QUALITY,
        '08-refs': ALLOWED_IN_08_REFS,
    }
    return ext_map.get(subdir_name, None)


def validate_paper_structure(paper_dir):
    """
    验证论文目录结构是否符合标准
    v2.0: 递归检查所有子目录
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'info': [],
        'subdir_errors': []
    }

    if not os.path.isdir(paper_dir):
        result['valid'] = False
        result['errors'].append(f"目录不存在: {paper_dir}")
        return result

    # ===== 检查根目录 =====
    root_files = [f for f in os.listdir(paper_dir) if os.path.isfile(os.path.join(paper_dir, f))]
    for f in root_files:
        if f not in ALLOWED_ROOT_FILES:
            result['valid'] = False
            result['errors'].append(f"根目录不允许的文件: {f}")
        else:
            result['info'].append(f"根目录允许的文件: {f}")

    subdirs = [d for d in os.listdir(paper_dir) if os.path.isdir(os.path.join(paper_dir, d))]

    for std_dir in STANDARD_DIRS:
        if std_dir not in subdirs:
            result['valid'] = False
            result['errors'].append(f"缺少标准目录: {std_dir}")

    for d in subdirs:
        if d not in STANDARD_DIRS:
            valid, msg = check_dir_name(d)
            if not valid:
                result['valid'] = False
                result['errors'].append(f"非标准目录: {d} ({msg})")
            else:
                result['warnings'].append(f"非标准目录但未被禁止: {d}")

    for f in root_files:
        valid, msg = check_file_name(f)
        if not valid:
            result['valid'] = False
            result['errors'].append(f"根目录文件命名问题: {f} ({msg})")

    # ===== 递归检查子目录（v2.0 新增） =====
    for std_dir in STANDARD_DIRS:
        std_path = os.path.join(paper_dir, std_dir)
        if not os.path.isdir(std_path):
            continue

        # 递归遍历所有子目录
        for root, dirs, files in os.walk(std_path):
            rel_path = os.path.relpath(root, paper_dir)

            # 检查子目录名
            for d in dirs:
                if d in ('code', 'data', 'models', 'figures'):
                    continue
                valid, msg = check_dir_name(d)
                if not valid:
                    result['valid'] = False
                    err = f"子目录 {rel_path}/{d} 禁止命名: {msg}"
                    result['errors'].append(err)
                    result['subdir_errors'].append(err)

            # 检查文件
            for f in files:
                # 跳过符号链接
                full_path = os.path.join(root, f)
                if os.path.islink(full_path):
                    result['info'].append(f"符号链接: {rel_path}/{f}")
                    continue

                valid, msg = check_file_name(f)
                if not valid:
                    result['valid'] = False
                    err = f"子目录 {rel_path}/{f} 禁止命名: {msg}"
                    result['errors'].append(err)
                    result['subdir_errors'].append(err)
                    continue

                # 检查扩展名限制
                ext = os.path.splitext(f)[1]
                allowed_ext = get_allowed_extensions(rel_path)
                if allowed_ext is not None:
                    if ext and ext not in allowed_ext:
                        # 如果文件名不在白名单中且扩展名不在允许列表中
                        basename = os.path.splitext(f)[0]
                        if basename not in allowed_ext and ext not in allowed_ext:
                            # 检查是否可能是允许的文件
                            if f not in allowed_ext:
                                result['valid'] = False
                                err = f"子目录 {rel_path}/{f} 不允许的文件类型"
                                result['errors'].append(err)
                                result['subdir_errors'].append(err)
                                continue

                    # 文件名精确匹配检查
                    if f not in allowed_ext and ext not in allowed_ext:
                        # 检查是否是允许的文件名
                        pass  # 有些文件名可能不在列表中但应该允许

    return result


def print_report(result):
    """打印校验报告"""
    print("=" * 60)
    print("论文目录结构校验报告 (v2.0)")
    print("=" * 60)

    if result['valid']:
        print("✅ 校验通过")
    else:
        print("❌ 校验失败")

    print()

    if result['info']:
        print("📋 信息:")
        for info in result['info']:
            print(f"  • {info}")
        print()

    if result['warnings']:
        print("⚠️  警告:")
        for warning in result['warnings']:
            print(f"  • {warning}")
        print()

    if result['errors']:
        print("🚨 错误:")
        for error in result['errors']:
            print(f"  • {error}")
        print()

    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 paper_dir_validator.py <paper_dir>")
        sys.exit(1)

    paper_dir = sys.argv[1]
    result = validate_paper_structure(paper_dir)
    print_report(result)

    sys.exit(0 if result['valid'] else 1)


if __name__ == '__main__':
    main()
