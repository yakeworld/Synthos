#!/usr/bin/env python3
"""Download a paper PDF by any identifier.

Usage:
    python3 download_one.py <DOI|arXiv|CorpusID|PMID|PMC> <output.pdf>

Supports all ID types:
    DOI:        10.1234/abc.2024.56789
    arXiv:      2403.12345  or  arXiv:2403.12345
    CorpusID:   CorpusID:12345678  or  bare 8+ digit number
    PMID:       PMID:12345678  or  12345678
    PMC:        PMC1234567
"""
import sys, os, logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from downloader.unified_download_core import download_paper

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    identifier = sys.argv[1]
    output_path = sys.argv[2]
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    success = download_paper(identifier, output_path)
    print(f"Result: {success}")
    sys.exit(0 if success else 1)
