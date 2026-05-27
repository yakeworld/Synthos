import os
import aiohttp
import requests
import asyncio
import logging
from typing import Optional
from src.core.interfaces import IDownloader
from src.core.config import Config
from src.utils.async_helpers import async_retry
from src.utils.file_ops import ensure_directory_exists

logger = logging.getLogger(__name__)

class BaseDownloader(IDownloader):
    """基础下载器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = None
        self.semaphore = None
    
    async def create_session(self):
        """创建异步会话"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.download_timeout + 5)
            self.session = aiohttp.ClientSession(timeout=timeout)
            self.semaphore = asyncio.Semaphore(self.config.max_concurrent_downloads)
    
    async def close_session(self):
        """关闭异步会话"""
        if self.session:
            try:
                await self.session.close()
                self.session = None
                await asyncio.sleep(0.25)
            except Exception as e:
                logger.error(f"Error closing aiohttp session: {e}")
    
    @async_retry(max_attempts=3, delay=2.0)
    async def download_file(self, url: str, filename: str) -> bool:
        """
        下载文件
        
        Args:
            url: 文件URL
            filename: 保存文件名
            
        Returns:
            是否下载成功
        """
        if not url or not isinstance(url, str) or not url.startswith("http"):
            logger.error(f"Invalid URL for download: '{url}'")
            return False
        
        # 检查文件是否已存在
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            logger.info(f"File {filename} already exists.")
            return True
        
        try:
            async with self.semaphore:
                return await self._download_file_internal(url, filename)
        except Exception as e:
            logger.exception(f"Error in download_file for {url}:")
            return False
    
    async def _download_file_internal(self, url: str, filename: str) -> bool:
        """内部下载实现"""
        try:
            logger.debug(f"Starting download from {url} to {filename}")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            async with self.session.get(url, headers=headers, timeout=self.config.download_timeout, allow_redirects=True) as response:
                if response.status != 200:
                    logger.error(f"HTTP {response.status}, trying curl_cffi fallback")
                    return await self._fallback_download(url, filename)
                
                ensure_directory_exists(os.path.dirname(os.path.abspath(filename)))
                
                with open(filename, 'wb') as f:
                    chunk_size = 8192
                    while True:
                        chunk = await response.content.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                
                # Validate PDF
                if await self._validate_pdf(filename):
                    logger.info(f"File {filename} downloaded successfully.")
                    return True
                else:
                    logger.warning(f"Downloaded file is not a valid PDF, trying fallback")
                    os.remove(filename)
                    return await self._fallback_download(url, filename)
                
        except (asyncio.TimeoutError, aiohttp.ClientError, Exception) as e:
            logger.warning(f"aiohttp download failed, trying requests fallback: {e}")
            return await self._fallback_download(url, filename)
    
    async def _fallback_download(self, url: str, filename: str) -> bool:
        """Fallback: try curl_cffi (handles brotli, TLS fingerprint), then requests."""
        try:
            from curl_cffi import requests as cffi
            logger.info(f"curl_cffi fallback: {url}")
            r = cffi.get(url, impersonate="chrome120", 
                        timeout=120, allow_redirects=True)
            if r.status_code == 200 and r.content[:4] == b'%PDF':
                ensure_directory_exists(os.path.dirname(os.path.abspath(filename)))
                with open(filename, 'wb') as f:
                    f.write(r.content)
                logger.info(f"curl_cffi download successful: {filename}")
                return True
            else:
                logger.warning(f"curl_cffi failed: HTTP {r.status_code}, type={r.headers.get('Content-Type','')[:30]}")
        except ImportError:
            logger.warning("curl_cffi not available")
        except Exception as e:
            logger.warning(f"curl_cffi error: {e}")
        
        # Last resort: requests
        try:
            import requests as req
            logger.info(f"requests fallback: {url}")
            r = req.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, 
                       timeout=self.config.download_timeout, stream=True)
            if r.status_code == 200:
                ensure_directory_exists(os.path.dirname(os.path.abspath(filename)))
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                if await self._validate_pdf(filename):
                    logger.info(f"requests download successful: {filename}")
                    return True
                else:
                    os.remove(filename)
            logger.error(f"requests failed: HTTP {r.status_code}")
        except Exception as e:
            logger.error(f"All fallbacks failed: {e}")
        return False

    async def _validate_pdf(self, path: str) -> bool:
        """Validate that file is a real PDF."""
        try:
            if not os.path.exists(path) or os.path.getsize(path) < 1000:
                return False
            with open(path, 'rb') as f:
                header = f.read(5)
                if header != b'%PDF-':
                    return False
                f.seek(-100, 2)
                tail = f.read()
                return b'%%EOF' in tail
        except:
            return False
    
    async def download_pdf(self, identifier: str, save_path: str) -> bool:
        """
        下载PDF文件
        
        Args:
            identifier: 论文标识符（DOI、arXiv ID等）
            save_path: 保存路径
            
        Returns:
            是否下载成功
        """
        # 需要在子类中实现具体的PDF下载逻辑
        raise NotImplementedError
    
    def download_paper_sync(self, url: str, filename: str) -> bool:
        """
        同步下载论文
        
        Args:
            url: 论文URL
            filename: 保存文件名
            
        Returns:
            是否下载成功
        """
        if not url or not isinstance(url, str) or not url.startswith("http"):
            logger.error(f"Invalid URL for download: '{url}'")
            return False
        
        ensure_directory_exists(os.path.dirname(os.path.abspath(filename)))
        
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            logger.info(f"File {filename} already exists.")
            return True
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=self.config.download_timeout)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
            else:
                logger.error(f"Failed to download paper from {url}. Status code: {response.status_code}")
                return False
        except requests.Timeout:
            logger.error(f"Timeout downloading paper from {url}")
            return False
        except requests.ConnectionError:
            logger.error(f"Connection error downloading paper from {url}")
            return False
        except Exception as e:
            logger.error(f"Error downloading paper from {url}: {str(e)}")
            return False


class SimpleDownloader(BaseDownloader):
    """简单下载器，用于直接URL下载"""
    
    async def download_pdf(self, identifier: str, save_path: str) -> bool:
        """
        下载PDF文件
        
        Args:
            identifier: 直接URL或标识符
            save_path: 保存路径
            
        Returns:
            是否下载成功
        """
        # 如果是URL，直接下载
        if identifier.startswith(('http://', 'https://')):
            return await self.download_file(identifier, save_path)
        
        # 否则尝试构造URL
        if identifier.startswith('arxiv:'):
            arxiv_id = identifier[6:]
            url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            return await self.download_file(url, save_path)
        
        logger.warning(f"Unsupported identifier format: {identifier}")
        return False