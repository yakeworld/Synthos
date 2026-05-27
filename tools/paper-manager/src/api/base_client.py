import asyncio
import aiohttp
import requests
import logging
from typing import List, Dict, Optional, Any
from src.core.interfaces import IPaperProvider, IHttpClient
from src.core.config import Config
from src.utils.async_helpers import async_retry

logger = logging.getLogger(__name__)

class BaseAPIClient(IPaperProvider):
    """基础API客户端"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = None
        self.sync_session = requests.Session()
    
    async def create_session(self):
        """创建异步会话"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.download_timeout + 5)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """关闭异步会话"""
        if self.session:
            try:
                await self.session.close()
                self.session = None
                await asyncio.sleep(0.25)
            except Exception as e:
                logger.error(f"Error closing aiohttp session: {e}")
    
    def __del__(self):
        """析构函数"""
        if hasattr(self, 'sync_session') and self.sync_session:
            try:
                self.sync_session.close()
            except Exception:
                pass
    
    @async_retry(max_attempts=3, delay=1.0)
    async def _async_get(self, url: str, headers: Dict = None, params: Dict = None, timeout: int = 30) -> Any:
        """异步GET请求"""
        await self.create_session()
        
        if headers is None:
            headers = self.config.headers
        if params is None:
            params = {}
        
        try:
            async with self.session.get(url, headers=headers, params=params, timeout=timeout) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error for {url}: {e}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"Timeout for {url}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            raise
    
    def _sync_get(self, url: str, headers: Dict = None, timeout: int = 30) -> Any:
        """同步GET请求"""
        if headers is None:
            headers = self.config.headers
        
        try:
            response = self.sync_session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"HTTP error for {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            raise
    
    async def search_papers(self, query: str) -> List[Dict]:
        """搜索论文 - 需要在子类中实现"""
        raise NotImplementedError
    
    async def get_paper_details(self, paper_id: str) -> Optional[Dict]:
        """获取论文详情 - 需要在子类中实现"""
        raise NotImplementedError
    
    async def get_references(self, paper_id: str, limit: int = 100) -> List[Dict]:
        """获取引用文献 - 需要在子类中实现"""
        raise NotImplementedError
    
    async def get_citations(self, paper_id: str, limit: int = 100) -> List[Dict]:
        """获取被引文献 - 需要在子类中实现"""
        raise NotImplementedError
    
    async def get_recommendations(self, paper_id: str, limit: int = 10) -> List[Dict]:
        """获取推荐文献 - 需要在子类中实现"""
        raise NotImplementedError
    
    async def get_author_papers(self, author_id: str, limit: int = 100) -> List[Dict]:
        """获取作者论文 - 需要在子类中实现"""
        raise NotImplementedError


class AioHttpClient(IHttpClient):
    """基于aiohttp的HTTP客户端实现"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = None
    
    async def create_session(self):
        """创建会话"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.download_timeout + 5)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """关闭会话"""
        if self.session:
            try:
                await self.session.close()
                self.session = None
            except Exception as e:
                logger.error(f"Error closing aiohttp session: {e}")
    
    @async_retry(max_attempts=3, delay=1.0)
    async def get(self, url: str, headers: Dict = None, timeout: int = 30) -> Any:
        """发送GET请求"""
        await self.create_session()
        
        if headers is None:
            headers = {}
        
        headers.setdefault('User-Agent', 
                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            async with self.session.get(url, headers=headers, timeout=timeout) as response:
                response.raise_for_status()
                return await response.read()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error for {url}: {e}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"Timeout for {url}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            raise
    
    @async_retry(max_attempts=3, delay=1.0)
    async def post(self, url: str, json: Dict = None, headers: Dict = None, timeout: int = 30) -> Any:
        """发送POST请求"""
        await self.create_session()
        
        if headers is None:
            headers = {}
        if json is None:
            json = {}
        
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('User-Agent', 
                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            async with self.session.post(url, json=json, headers=headers, timeout=timeout) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error for {url}: {e}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"Timeout for {url}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            raise