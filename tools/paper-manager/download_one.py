"""Helper: download a single DOI via racing engine."""
import sys, os, asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from downloader.pdf_downloader import PDFDownloader
from core.config import Config

async def main():
    doi = sys.argv[1]
    out = sys.argv[2]
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    dl = PDFDownloader(Config())
    await dl.create_session()
    r = await dl._download_racing(doi, out)
    await dl.close_session()
    print(f"Result: {r}", flush=True)
    sys.exit(0 if r else 1)

asyncio.run(main())
