#!/usr/bin/env python3
"""批量修复论文引用: 补DOI→下载PDF。见 SKILL.md 的 batch_fix 章节。"""
import os, re, json, time, socket, ssl, urllib.request, urllib.parse
BASE = "/media/yakeworld/sda2/Synthos/outputs/papers"
PROXY_FILE = "/home/yakeworld/proxy_final.txt"
with open(PROXY_FILE) as f:
    proxies = [l.strip().split(' -> ')[0] for l in f if l.strip()]
def resolve_doi(t):
    m = re.search(r'(10\.\d{4,}/[^\s}]+)', t)
    if m: return m.group(1), 'inline'
    q = re.sub(r'\\{1,2}[a-z]+(?:\{[^}]*\})?', '', t)[:120]
    q = re.sub(r'[{}]', '', q).strip()
    try:
        url = f"https://api.crossref.org/works?query={urllib.parse.quote(q)}&rows=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Synthos/1.0'})
        d = json.loads(urllib.request.urlopen(req, timeout=10).read())
        items = d.get('message', {}).get('items', [])
        if items: return items[0].get('DOI',''), 'crossref'
    except: pass
    return '', ''
def dl_pdf(doi, path):
    if os.path.exists(path) and os.path.getsize(path) > 5000: return True
    try:
        import ssl
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        s = socket.socket(); s.settimeout(8)
        ip = socket.getaddrinfo('sci.bban.top', 443, socket.AF_INET)[0][4][0]
        s.connect((ip, 443))
        ss = ctx.wrap_socket(s, server_hostname='sci.bban.top')
        ss.sendall(f'GET /pdf/{doi}.pdf HTTP/1.0\r\nHost: sci.bban.top\r\nUser-Agent: curl/8.0\r\nConnection: close\r\n\r\n'.encode())
        d = b''
        while True:
            c = ss.read(8192)
            if not c: break
            d += c
        ss.close()
        b = d.split(b'\r\n\r\n',1)[-1] if b'\r\n\r\n' in d else d
        if b[:4]==b'%PDF' and len(b)>5000:
            with open(path,'wb') as f: f.write(b)
            return True
    except: pass
    return False
for idx,name in enumerate(sorted(d for d in os.listdir(BASE) if os.path.isdir(os.path.join(BASE,d)) and not d.startswith('_') and d not in ('pdfs','scripts','08-refs','07-quality'))):
    dpath = os.path.join(BASE, name)
    tex_path = os.path.join(dpath, 'paper.tex') if os.path.exists(os.path.join(dpath,'paper.tex')) else (os.path.join(dpath,'01-manuscript','paper.tex') if os.path.exists(os.path.join(dpath,'01-manuscript','paper.tex')) else None)
    if not tex_path: continue
    with open(tex_path) as f: tex = f.read()
    m = re.search(r'\\begin\{thebibliography\}(.*?)\\end\{thebibliography\}', tex, re.DOTALL)
    if not m: continue
    bib = m.group(1)
    items = re.findall(r'\\bibitem\{(\w+)\}(.*?)(?=\\bibitem\{|\\Z)', bib, re.DOTALL)
    pdf_dir = os.path.join(dpath, '06-references','pdfs'); os.makedirs(pdf_dir, exist_ok=True)
    d_found=0;p_added=0;changes=[]
    for k,t in items:
        if re.search(r'DOI:\s*\\url\{10\.', t): d_found+=1; continue
        doi,_=resolve_doi(t)
        if doi:
            d_found+=1; tex=tex.replace(t, t.rstrip()+f'\n  \\newblock DOI: \\url{{{doi}}}.')
            changes.append(k)
            if dl_pdf(doi, os.path.join(pdf_dir,f'{k}.pdf')): p_added+=1
        time.sleep(0.3)
    if changes:
        with open(tex_path,'w') as f: f.write(tex)
    print(f"  [{idx+1:2d}] {name[:30]:30s} refs={len(items):2d} DOI={d_found:2d} PDF+={p_added:2d}")
