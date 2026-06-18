#!/usr/bin/env python3
"""
Sci-Hub 单DOI下载器 — 域探测 + HTML解析 + Referer头下载 + PDF验证

用法:
  python3 scihub_download.py 10.1016/j.diabres.2021.109119 /tmp/output.pdf
  python3 scihub_download.py 10.1016/j.diabres.2021.109119 /tmp/output.pdf --verbose

域探测顺序: ru → ee → wf (2026-05-31实测有效)
"""
import curl_cffi.requests as r
import sys, re, os, time, argparse

PDF_HEADER = b'%PDF'

# 按稳定性排序，首域无效自动回退
DOMAINS = ['https://sci-hub.ru', 'https://sci-hub.ee', 'https://sci-hub.wf']

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


def probe_domains(domains: list[str], timeout: int = 5) -> list[str]:
    """快速探测哪些域可达，返回按响应码排序的可达域列表"""
    import subprocess
    alive = []
    for d in domains:
        try:
            code = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                 '--connect-timeout', str(timeout), d],
                capture_output=True, text=True, timeout=timeout + 2
            )
            c = code.stdout.strip()
            if c in ('200', '301', '302'):
                alive.append((d, int(c)))
        except Exception:
            pass
    return [d for d, _ in alive]


def try_download(session, domain: str, doi: str, output: str, verbose: bool = False) -> bool:
    """尝试从指定域下载DOI全文PDF"""
    url = f'{domain}/{doi}'
    if verbose:
        print(f'  → {url}')
    
    try:
        resp = session.get(url, impersonate='chrome120', timeout=30)
    except Exception as e:
        if verbose:
            print(f'  ✗ 连接失败: {e}')
        return False
    
    # 情况1: 直接返回PDF
    if resp.content[:4] == PDF_HEADER:
        _save_pdf(resp.content, output)
        if verbose:
            print(f'  ✅ 直出PDF ({len(resp.content)} bytes)')
        return True
    
    # 情况2: HTML页面 → 提取PDF存储URL
    html = resp.text
    
    # 提取模式: iframe src / embed src / 直接href
    pdf_url = None
    patterns = [
        r'iframe[^>]+src=["\']([^"\']+\.pdf[^"\']*)["\']',
        r'embed[^>]+src=["\']([^"\']+\.pdf[^"\']*)["\']',
        r'href=["\']([^"\']+\.pdf[^"\']*)["\']',
    ]
    for p in patterns:
        m = re.search(p, html)
        if m:
            pdf_url = m.group(1)
            break
    
    if not pdf_url:
        # 回退: 找 /storage/tail/ 路径
        m = re.search(r'(/storage/tail/[^"\']+\.pdf)', html)
        if m:
            pdf_url = m.group(1)
    
    if not pdf_url:
        if verbose:
            print('  ✗ 未找到PDF链接（可能需要手动浏览器导航）')
            with open('/tmp/scihub_debug.html', 'w') as f:
                f.write(html[:100000])
            print('  Debug HTML → /tmp/scihub_debug.html')
        return False
    
    # 规范化URL
    if pdf_url.startswith('//'):
        pdf_url = 'https:' + pdf_url
    elif pdf_url.startswith('/'):
        pdf_url = domain + pdf_url
    
    # 下载PDF（必须带Referer头！）
    if verbose:
        print(f'  → 存储PDF: {pdf_url[:80]}...')
    try:
        pdf_resp = session.get(
            pdf_url, impersonate='chrome120', timeout=60,
            headers={'Referer': url}
        )
        if pdf_resp.status_code == 200 and pdf_resp.content[:4] == PDF_HEADER:
            _save_pdf(pdf_resp.content, output)
            if verbose:
                print(f'  ✅ PDF via HTML提取 ({len(pdf_resp.content)} bytes)')
            return True
        else:
            if verbose:
                print(f'  ✗ 下载失败: HTTP {pdf_resp.status_code}, 头={pdf_resp.content[:20]}')
    except Exception as e:
        if verbose:
            print(f'  ✗ 存储下载异常: {e}')
    
    return False


def _save_pdf(content: bytes, path: str):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'wb') as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(description='Sci-Hub DOI PDF下载器')
    parser.add_argument('doi', help='论文DOI (如 10.1016/j.diabres.2021.109119)')
    parser.add_argument('output', help='输出PDF路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--timeout', type=int, default=30, help='单域超时(秒)')
    parser.add_argument('--probe', action='store_true', default=True,
                        help='下载前先域探测（默认开启，跳过可大幅加速）')
    args = parser.parse_args()
    
    # 可选: 先域探测
    domains = DOMAINS
    if args.probe:
        if args.verbose:
            print(f'域探测中...', end=' ', flush=True)
        alive = probe_domains(DOMAINS)
        if not alive:
            print('❌ 所有Sci-Hub域均不可达')
            sys.exit(1)
        if args.verbose:
            print(f'可用: {alive}')
        domains = alive
    
    # 创建session
    s = r.Session()
    s.headers.update({'User-Agent': UA})
    
    # 逐域尝试
    for domain in domains:
        if try_download(s, domain, args.doi, args.output, args.verbose):
            sys.exit(0)
        if args.verbose:
            print(f'  {domain} → 跳过')
    
    print(f'❌ 所有域均下载失败: {args.doi}')
    sys.exit(1)


if __name__ == '__main__':
    main()
