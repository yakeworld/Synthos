import os
import re
import asyncio
import logging
from typing import Optional
from src.downloader.base_downloader import BaseDownloader
from src.core.config import Config
from src.utils.async_helpers import async_retry
from src.utils.file_ops import ensure_directory_exists

logger = logging.getLogger(__name__)

class PDFDownloader(BaseDownloader):
    """PDF下载器"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.sci_hub_mirrors = config.sci_hub_mirrors
    
    async def download_pdf(self, identifier: str, save_path: str, open_access_pdf: dict = None) -> bool:
        if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
            logger.info(f"PDF file already exists at {save_path}")
            return True

        # 尝试从openAccessPdf直接下载
        if open_access_pdf and isinstance(open_access_pdf, dict):
            pdf_url = open_access_pdf.get('url')
            if pdf_url:
                logger.info(f"Trying to download from Open Access URL: {pdf_url}")
                if await self.download_file(pdf_url, save_path):
                    return True

        # 尝试从arXiv下载
        arxiv_result = await self._try_arxiv_download(identifier, save_path)
        if arxiv_result:
            return True

        # 使用并行竞速引擎下载
        return await self._download_racing(identifier, save_path)
    
    async def _try_arxiv_download(self, identifier: str, save_path: str) -> bool:
        """尝试从arXiv下载"""
        arxiv_id = self._extract_arxiv_id(identifier)
        if not arxiv_id:
            return False
        
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        logger.info(f"Trying to download from arXiv: {url}")
        
        return await self.download_file(url, save_path)
    
    async def _try_sci_hub_download(self, identifier: str, save_path: str) -> bool:
        """尝试从Sci-Hub下载"""
        doi = self._extract_doi(identifier)
        if not doi:
            return False
        
        # 快速检测：先试第一个镜像，如果返回HTML而非PDF就跳过
        test_mirror = self.sci_hub_mirrors[0] if self.sci_hub_mirrors else None
        if test_mirror:
            test_url = f"{test_mirror}{doi}"
            try:
                import requests as req
                r = req.get(test_url, headers={"User-Agent": "Mozilla/5.0"}, 
                           timeout=15, allow_redirects=True)
                content_type = r.headers.get('Content-Type', '')
                if 'html' in content_type:
                    logger.warning(f"Sci-Hub blocked by DDoS-Guard, trying Playwright browser...")
                    return await self._try_scihub_playwright(doi, save_path)
            except Exception:
                pass
        
        # 原逻辑：逐个镜像尝试
        for mirror in self.sci_hub_mirrors:
            try:
                url = f"{mirror}{doi}"
                logger.info(f"Trying Sci-Hub mirror: {mirror}")
                if await self.download_file(url, save_path):
                    logger.info(f"Successfully downloaded via {mirror}")
                    return True
            except Exception as e:
                logger.warning(f"Error using mirror {mirror} for DOI {doi}: {e}")
                continue
        
        return False
    
    @async_retry(max_attempts=2, delay=1.0)
    async def _download_from_sci_hub_mirror(self, mirror: str, doi: str, save_path: str) -> bool:
        """从Sci-Hub镜像下载"""
        await self.create_session()
        
        pattern = r'(//.*?\.pdf|/downloads/.*?\.pdf)'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            paper_url = mirror + doi
            async with self.session.get(paper_url, headers=headers, timeout=self.config.download_timeout) as response:
                if response.status != 200:
                    return False
                
                content = await response.text()
                download_urls = re.findall(pattern, content)
                
                if not download_urls:
                    return False
                
                url = download_urls[0]
                if url.startswith('//'):
                    url = 'https:' + url
                elif url.startswith('/downloads'):
                    url = mirror.rstrip('/') + url
                
                return await self.download_file(url, save_path)
                
        except asyncio.TimeoutError:
            logger.warning(f"Timeout using mirror {mirror} for DOI {doi}")
            return False
        except Exception as e:
            logger.warning(f"Error using mirror {mirror} for DOI {doi}: {e}")
            return False
    
    def _extract_arxiv_id(self, identifier: str) -> Optional[str]:
        """提取arXiv ID"""
        arxiv_patterns = [
            r'^(arxiv:)?(\d{4}\.\d{4,5}(v\d+)?|[a-z\-]+/\d{7})$',
            r'^10\.48550/arXiv\.(\d{4}\.\d{4,5}(v\d+)?)$',
            r'^arXiv\.(\d{4}\.\d{4,5}(v\d+)?)$'
        ]
        
        for pattern in arxiv_patterns:
            m = re.match(pattern, identifier, re.IGNORECASE)
            if m:
                if m.lastindex and m.lastindex >= 2:
                    return m.group(2)
                elif m.lastindex:
                    return m.group(1)
                else:
                    return identifier
        
        return None
    
    def _extract_doi(self, identifier: str) -> Optional[str]:
        """提取DOI"""
        # 直接DOI
        if re.match(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', identifier, re.IGNORECASE):
            return identifier
        
        # DOI:前缀
        m = re.match(r'^DOI:(.+)$', identifier, re.IGNORECASE)
        if m:
            return m.group(1)
        
        # 其他DOI格式
        m = re.match(r'^https?://doi\.org/(.+)$', identifier, re.IGNORECASE)
        if m:
            return m.group(1)
        
        return None
    
    async def get_paper_pdf(self, identifier: str, save_dir: str, filename: str = None, open_access_pdf: dict = None) -> str:
        ensure_directory_exists(save_dir)

        if filename is None:
            if self._extract_arxiv_id(identifier):
                arxiv_id = self._extract_arxiv_id(identifier)
                filename = f'arxiv_{arxiv_id}.pdf'
            elif self._extract_doi(identifier):
                doi = self._extract_doi(identifier)
                filename = f'{doi.replace("/", "_").replace(".","-")}.pdf'
            else:
                filename = f'{identifier}.pdf'

        file_path = os.path.join(save_dir, filename)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            logger.info(f"PDF file already exists at {file_path}")
            return file_path

        success = await self.download_pdf(identifier, file_path, open_access_pdf)
        if success:
            return file_path
        else:
            logger.error(f"Failed to download PDF for {identifier}")
            return ""
    
    async def get_arxiv_pdf(self, arxiv_id: str, save_dir: str, filename: str = None) -> str:
        """获取arXiv PDF"""
        ensure_directory_exists(save_dir)
        
        if filename is None:
            filename = f'arxiv_{arxiv_id}.pdf'
        
        file_path = os.path.join(save_dir, filename)
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            logger.info(f"PDF file for arXiv ID {arxiv_id} already exists at {file_path}")
            return file_path
        
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        if await self.download_file(url, file_path):
            return file_path
        
        logger.error(f"Failed to download PDF for arXiv ID {arxiv_id}")
        return ""
    
    async def get_doi_pdf(self, doi: str, save_dir: str, filename: str = None) -> str:
        """获取DOI PDF"""
        ensure_directory_exists(save_dir)
        
        if filename is None:
            filename = f'{doi.replace("/", "_").replace(".","-")}.pdf'
        
        file_path = os.path.join(save_dir, filename)
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            logger.info(f"PDF file for DOI {doi} already exists at {file_path}")
            return file_path
        
        # 尝试从Sci-Hub下载
        for mirror in self.sci_hub_mirrors:
            try:
                if await self._download_from_sci_hub_mirror(mirror, doi, file_path):
                    return file_path
            except Exception as e:
                logger.warning(f"Failed with mirror {mirror}: {e}")
                continue
        
        logger.error(f"Failed to download PDF for DOI {doi} from all mirrors")
        return ""

    async def _try_scihub_playwright(self, doi: str, save_path: str) -> bool:
        """Use curl_cffi (TLS fingerprint) to bypass DDoS-Guard and download from Sci-Hub"""
        try:
            import subprocess, sys as _sys
            scihub_script = os.path.join(os.path.dirname(__file__), 'scihub_download.py')
            if not os.path.exists(scihub_script):
                logger.error(f"Sci-Hub script not found: {scihub_script}")
                return False
            
            logger.info(f"Sci-Hub: trying curl_cffi for DOI {doi}")
            result = subprocess.run(
                [_sys.executable, scihub_script, doi, save_path],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0 and os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                logger.info(f"Sci-Hub download successful: {save_path}")
                return True
            else:
                logger.warning(f"Sci-Hub download failed: {result.stderr[:200]}")
                return False
        except Exception as e:
            logger.error(f"Sci-Hub download error: {e}")
            return False

    async def _download_racing(self, doi: str, save_path: str) -> bool:
        """Parallel racing download via curl_cffi + LibGen."""
        try:
            from racing_engine import race_sources, build_download_tiers
            from concurrent.futures import ThreadPoolExecutor
            import functools
            
            # Build tiers
            tiers = build_download_tiers(doi)
            
            for tier_sources, tier_label, timeout in tiers:
                logger.info(f"Tier [{tier_label}]: racing {len(tier_sources)} sources...")
                result = race_sources(doi, save_path, tier_sources, timeout=timeout)
                if result and result.get('success'):
                    return True
                logger.info(f"Tier [{tier_label}]: no source succeeded")
            
            logger.error(f"Failed to download PDF for DOI: {doi}")
            return False
        except Exception as e:
            logger.error(f"Racing download failed: {e}")
            return False