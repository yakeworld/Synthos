#!/usr/bin/env python3
"""
Sci-Hub PDF downloader using curl_cffi (TLS fingerprint bypass for DDoS-Guard).
Usage: python3 scihub_download.py <doi> <output_path>
"""
import sys, os, logging
from curl_cffi import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

SCI_HUB_MIRRORS = [
    "https://sci-hub.ru/", "https://sci-hub.ee/", "https://sci-hub.shop/",
    "https://sci-hub.ren/", "https://sci-hub.red/", "https://sci-hub.al/",
    "https://sci-hub.vg/", "https://sci-hub.wf/", "https://sci-hub.es/",
    "https://sci-hub.box/", "https://sci-hub.yt/",
]

def download_pdf(doi: str, output_path: str) -> bool:
    """Download PDF from Sci-Hub using curl_cffi to bypass DDoS-Guard"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for mirror in SCI_HUB_MIRRORS:
        url = f"{mirror}{doi}"
        log.info(f"Trying {mirror}")
        
        try:
            # Step 1: Get landing page
            r = requests.get(url, headers=headers, impersonate="chrome120", timeout=30, allow_redirects=True)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Extract PDF URL from page
            pdf_rel = None
            for a in soup.find_all('a'):
                href = a.get('href', '')
                if 'download' in a.text.lower() or ('.pdf' in href and 'storage' in href):
                    pdf_rel = href
                    break
            
            if not pdf_rel:
                iframe = soup.find('iframe', id='pdf')
                if iframe and iframe.get('src'):
                    pdf_rel = iframe['src']
            
            if not pdf_rel:
                # Check if article exists
                title = soup.title.string if soup.title else ''
                if 'отсутствует' in title.lower() or 'not found' in title.lower():
                    log.warning(f"Article not in Sci-Hub database")
                    continue
                log.info(f"No PDF link found on page")
                continue
            
            # Step 2: Download PDF
            pdf_url = pdf_rel if pdf_rel.startswith('http') else f"https:{pdf_rel}" if pdf_rel.startswith('//') else f"https://sci-hub.ru{pdf_rel}"
            
            r2 = requests.get(pdf_url, headers=headers, impersonate="chrome120", timeout=60, allow_redirects=True)
            
            if r2.content[:4] == b'%PDF':
                os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(r2.content)
                log.info(f"✅ Downloaded: {output_path} ({len(r2.content)} bytes)")
                return True
            else:
                log.warning(f"Response is not PDF: {r2.content[:50]}")
                
        except Exception as e:
            log.warning(f"Mirror {mirror} failed: {e}")
            continue
    
    return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 scihub_download.py <doi> <output_path>")
        sys.exit(1)
    success = download_pdf(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
