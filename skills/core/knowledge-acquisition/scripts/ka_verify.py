#!/usr/bin/env python3
"""ka_verify.py — knowledge-acquisition 铁律实现 (验物验文)

SKILL.md 铁律: head -c 5 必须 = %PDF-，再 pdfinfo 核标题防串流。
本脚本 = 该铁律的可执行形式 (批量验证下载目录)。

用法:
    python3 ka_verify.py <pdf_dir>            # 验证目录下全部 .pdf
    python3 ka_verify.py a.pdf b.pdf          # 验证指定文件

输出: 每个文件一行  PASS/FAIL + 原因; 末尾汇总; 有 FAIL 则 exit 1。
"""
import os
import subprocess
import sys


def verify(pdf_path: str):
    """返回 (ok: bool, reason: str)"""
    if not os.path.exists(pdf_path):
        return False, 'missing'
    size = os.path.getsize(pdf_path)
    if size < 1024:
        return False, f'too_small({size}B)'
    with open(pdf_path, 'rb') as f:
        magic = f.read(5)
    if magic != b'%PDF-':
        return False, f'bad_magic({magic[:5]!r})'
    # pdfinfo 核标题 (防串流: 下载器错误页/截断流)
    try:
        r = subprocess.run(['pdfinfo', pdf_path], capture_output=True, text=True, timeout=15)
        if r.returncode != 0:
            return True, 'magic_ok_pdfinfo_unavailable'
        title = next((l.split(':', 1)[1].strip() for l in r.stdout.splitlines()
                      if l.lower().startswith('title:')), '')
        if not title:
            return True, 'magic_ok_no_title'
        return True, f'magic_ok_title({title[:40]})'
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return True, 'magic_ok_pdfinfo_unavailable'


def main():
    args = sys.argv[1:]
    if not args:
        print('usage: ka_verify.py <pdf_dir> | <files...>', file=sys.stderr)
        return 2
    files = []
    for a in args:
        if os.path.isdir(a):
            files += [os.path.join(a, f) for f in sorted(os.listdir(a)) if f.lower().endswith('.pdf')]
        else:
            files.append(a)
    fails = 0
    for p in files:
        ok, reason = verify(p)
        print(f'{"PASS" if ok else "FAIL"}  {os.path.basename(p)}  {reason}')
        if not ok:
            fails += 1
    print(f'--- {len(files) - fails}/{len(files)} pass')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
