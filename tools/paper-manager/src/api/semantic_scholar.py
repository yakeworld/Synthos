import asyncio
import time
import logging
from typing import List, Dict, Optional, Any
from urllib.parse import quote

from src.api.base_client import BaseAPIClient
from src.core.config import Config
from src.utils.paper_id import normalize_paper_id
from src.utils.async_helpers import async_retry

logger = logging.getLogger(__name__)

class SemanticScholarClient(BaseAPIClient):

    def __init__(self, config: Config):
        super().__init__(config)
        self.base_url = config.base_url
        self.recommendations_url = config.recommendations_url
        self.fields = config.fields

    async def search_papers(self, query: str, limit: int = 1000) -> List[Dict]:
        total_results = []
        tokens = set()
        params = {'query': query, 'fields': self.fields, 'limit': min(limit, 100)}

        try:
            while len(total_results) < limit:
                clean_params = {k: v for k, v in params.items() if v is not None}

                try:
                    data = await self._async_get(
                        f"{self.base_url}/paper/search",
                        params=clean_params
                    )

                    if 'data' in data:
                        total_results.extend(data['data'])
                        logger.info(f"Retrieved {len(total_results)} papers...")
                        if len(total_results) >= limit:
                            break
                    else:
                        logger.warning(f"No 'data' field in response: {data}")
                        break

                    if 'token' not in data or data['token'] in tokens:
                        break

                    tokens.add(data['token'])
                    params['token'] = data['token']
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"Error during API request: {e}")
                    break

        finally:
            tokens.clear()

        logger.info(f"Done! Retrieved {len(total_results)} papers total")
        return total_results
    
    async def get_paper_details(self, paper_id: str) -> Optional[Dict]:
        """获取论文详情"""
        norm_id = normalize_paper_id(paper_id)
        url = self._construct_paper_url(norm_id)
        
        if not url:
            logger.warning(f"Could not construct API URL for paper: {paper_id}")
            return None
        
        try:
            data = await self._async_get(url)
            
            # 处理批量API返回的数据结构
            if isinstance(data, dict) and 'data' in data:
                if data['data'] and len(data['data']) > 0:
                    return data['data'][0]
                else:
                    logger.warning(f"No search results found for paper: {paper_id}")
                    return None
            
            return data
        except Exception as e:
            logger.error(f"Error fetching paper details for {paper_id}: {e}")
            return None
    
    async def get_references(self, paper_id: str, limit: int = 100) -> List[Dict]:
        """获取引用文献"""
        norm_id = normalize_paper_id(paper_id)
        url = f"{self.base_url}/paper/{norm_id}/references"
        params = {"fields": self.fields, "limit": limit}
        
        try:
            data = await self._async_get(url, params=params)
            if isinstance(data, dict) and "data" in data:
                return [item["citedPaper"] for item in data["data"] if "citedPaper" in item]
            logger.warning(f"Unexpected references response: {data}")
            return []
        except Exception as e:
            logger.error(f"Error fetching references for {paper_id}: {e}")
            return []
    
    async def get_citations(self, paper_id: str, limit: int = 100) -> List[Dict]:
        """获取被引文献"""
        norm_id = normalize_paper_id(paper_id)
        url = f"{self.base_url}/paper/{norm_id}/citations"
        params = {"fields": self.fields, "limit": limit}
        
        try:
            data = await self._async_get(url, params=params)
            if isinstance(data, dict) and "data" in data:
                return [item["citingPaper"] for item in data["data"] if "citingPaper" in item]
            logger.warning(f"Unexpected citations response: {data}")
            return []
        except Exception as e:
            logger.error(f"Error fetching citations for {paper_id}: {e}")
            return []
    
    async def get_recommendations(self, paper_id: str, limit: int = 10) -> List[Dict]:
        """获取推荐文献"""
        norm_id = normalize_paper_id(paper_id)
        url = f"{self.recommendations_url}/papers/forpaper/{norm_id}"
        params = {"limit": limit}
        
        try:
            data = await self._async_get(url, params=params)
            if isinstance(data, dict) and "recommendedPapers" in data:
                return data["recommendedPapers"]
            if isinstance(data, list):
                return data
            logger.warning(f"Unexpected recommendations response: {data}")
            return []
        except Exception as e:
            logger.error(f"Error fetching recommendations for {paper_id}: {e}")
            return []
    
    async def get_author_papers(self, author_id: str, limit: int = 100) -> List[Dict]:
        """获取作者论文"""
        url = f"{self.base_url}/author/{author_id}/papers"
        params = {"fields": self.fields, "limit": limit}
        
        try:
            data = await self._async_get(url, params=params)
            if isinstance(data, dict) and "data" in data:
                return [item["paper"] if "paper" in item else item for item in data["data"]]
            logger.warning(f"Unexpected author papers response: {data}")
            return []
        except Exception as e:
            logger.error(f"Error fetching author papers for {author_id}: {e}")
            return []
    
    def _construct_paper_url(self, paper_id: str) -> Optional[str]:
        """构造论文API URL"""
        base_url = f"{self.base_url}/paper/"
        
        # ARXIV
        import re
        m = re.match(r"ARXIV:(.+)", paper_id, re.IGNORECASE)
        if m:
            return f"{base_url}ARXIV:{m.group(1)}?fields={self.fields}"
        
        # CorpusID
        m = re.match(r"CorpusID:(\d+)", paper_id, re.IGNORECASE)
        if m:
            return f"{base_url}CorpusID:{m.group(1)}?fields={self.fields}"
        
        # DOI
        m = re.match(r"DOI:(.+)", paper_id, re.IGNORECASE)
        if m:
            return f"{base_url}DOI:{m.group(1)}?fields={self.fields}"
        
        # S2 PaperId（40位小写hex）
        if re.match(r"^[a-f0-9]{40}$", paper_id):
            return f"{base_url}{paper_id}?fields={self.fields}"
        
        logger.warning(f"Could not construct API URL for paper ID: {paper_id}")
        return None
    
    async def fetch_papers_batch(self, paper_ids: List[str]) -> List[Dict]:
        """批量获取论文详情"""
        if not paper_ids:
            return []
        
        url = f"{self.base_url}/paper/batch"
        data = {"ids": paper_ids, "fields": self.fields}
        
        try:
            result = await self._async_post(url, json=data)
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            return result
        except Exception as e:
            logger.error(f"Error fetching papers batch: {e}")
            return []
    
    async def _async_post(self, url: str, json: Dict = None, headers: Dict = None, timeout: int = 120) -> Any:
        """异步POST请求"""
        await self.create_session()
        
        if headers is None:
            headers = self.config.headers
        if json is None:
            json = {}
        
        headers = headers.copy()
        headers.setdefault('Content-Type', 'application/json')
        
        try:
            async with self.session.post(url, json=json, headers=headers, timeout=timeout) as resp:
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error for POST {url}: {e}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"Timeout for POST {url}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for POST {url}: {e}")
            raise