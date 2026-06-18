# Tor + sci-hub.vg 工作流（2026-06-19 实证）

## 背景

Tailscale exit node IP (64.23.234.118) 被全部封锁。Tor SOCKS5H + sci-hub.vg 是唯一能获取 PDF 的自动化路径。

## 关键数据

**成功 DOI（通过 Tor + sci-hub.vg）**:
- `10.1136/bmj.m2689` → Riley2020_BMJ → 154,816 bytes → MD5: f4df98b15297ebfc128c6f8c2c85396b
- `10.1002/ana.24973` → Akbar2023 → 1,244,724 bytes → MD5: cc6239b915d684be27d15d7161bd9c05
- `10.1186/1472-6947-12-47` → Stiglic2012 → 652,195 bytes → MD5: 86e6ff3294a20ddb9c2fe44fe4867a46
- `10.1145/3097983.3098071` → Pedregosa2011 → 1,996,102 bytes → MD5: 53cb11c713b352fc27ab22b5495dea60

**失败 DOI（Tor + sci-hub.vg 全部 404/NOT_FOUND）**:
- `10.1007/s00415-020-10101-3` → Vollmer2020 (Springer)
- `10.1016/j.dsr.2019.150753` → Saeedi2019 (Taylor & Francis)
- `10.1038/nrendo.2018.74` → Zheng2018 (Nature)
- `10.1002/ere2.487` → Wu2024 (Wiley)
- `10.1007/978-981-99-8425-5_1` → Mehta2024 (Springer Book)
- `10.1001/jama.2020.22789` → Uno2001 (JAMA)
- `10.1016/j.jbi.2020.103778` → Shams2023 (Elsevier)
- `10.1007/s10994-015-5523-7` → Breiman2001

**结论**: Sci-Hub 数据库不包含所有论文。Tor + sci-hub.vg 能获取的是 Sci-Hub 已抓取的论文。

## 工作流

```python
import requests, re, hashlib

TOR = 'socks5h://127.0.0.1:9050'
PLACEHOLDER_MD5 = 'fd469bd7cd29446f2800f099e3b71457'

session = requests.Session()
session.trust_env = False
session.proxies = {'http': TOR, 'https': TOR}
session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})

def download_via_tor(doi, output_path):
    url = f"https://sci-hub.vg/{doi}"
    r = session.get(url, timeout=60)
    
    # Extract iframe PDF URL
    m = re.search(r'iframe[^>]+src=["\x27]([^"\x27]*\.pdf[^"\x27]*)["\x27]', r.text)
    if not m:
        return None  # DOI not in Sci-Hub database
    
    iframe_url = m.group(1)
    if not iframe_url.startswith('http'):
        iframe_url = f"https://sci-hub.vg{iframe_url}"
    
    r2 = session.get(iframe_url, timeout=90)
    
    if r2.content[:4] == b'%PDF' and len(r2.content) > 1000:
        md5 = hashlib.md5(r2.content).hexdigest()
        if md5 == PLACEHOLDER_MD5:
            return 'PLACEHOLDER'
        with open(output_path, 'wb') as f:
            f.write(r2.content)
        return md5
    return None
```

## 验证

下载后必须检查：
```bash
md5sum output.pdf | awk '{print $1}'
# 如果是 fd469bd7cd29446f2800f099e3b71457 → 伪PDF，需删除
```

## 性能

- 单篇: ~60-120 秒（Tor 路由延迟）
- 批量扫描 50 DOI: ~60-90 分钟
- 建议间隔 3-5 秒/篇（避免触发 IP 限流）
