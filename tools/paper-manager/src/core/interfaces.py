from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

class IPaperProvider(ABC):
    """论文提供商接口"""
    
    @abstractmethod
    async def search_papers(self, query: str) -> List[Dict]:
        """搜索论文"""
        pass
    
    @abstractmethod
    async def get_paper_details(self, paper_id: str) -> Optional[Dict]:
        """获取论文详情"""
        pass
    
    @abstractmethod
    async def get_references(self, paper_id: str, limit: int = 100) -> List[Dict]:
        """获取引用文献"""
        pass
    
    @abstractmethod
    async def get_citations(self, paper_id: str, limit: int = 100) -> List[Dict]:
        """获取被引文献"""
        pass
    
    @abstractmethod
    async def get_recommendations(self, paper_id: str, limit: int = 10) -> List[Dict]:
        """获取推荐文献"""
        pass
    
    @abstractmethod
    async def get_author_papers(self, author_id: str, limit: int = 100) -> List[Dict]:
        """获取作者论文"""
        pass


class IDownloader(ABC):
    """下载器接口"""
    
    @abstractmethod
    async def download_pdf(self, identifier: str, save_path: str, open_access_pdf: dict = None) -> bool:
        """下载PDF文件"""
        pass
    
    @abstractmethod
    async def download_file(self, url: str, filename: str) -> bool:
        """下载文件"""
        pass


class IBibtexConverter(ABC):
    """BibTeX转换器接口"""
    
    @abstractmethod
    def create_bibtex_entry(self, row: Dict, pdf_dir: str = "", bib_dir: str = None) -> tuple:
        """创建BibTeX条目"""
        pass
    
    @abstractmethod
    def convert_csv_to_bib(self, csv_file: str, output_file: str, pdf_dir: str = "") -> str:
        """转换CSV到BibTeX"""
        pass
    
    @abstractmethod
    def parse_bibtex_file(self, bibtex_file: str) -> List[Dict]:
        """解析BibTeX文件"""
        pass
    
    @abstractmethod
    def save_to_bib_file(self, entries: List[str], filename: str):
        """保存到BibTeX文件"""
        pass


class IHttpClient(ABC):
    """HTTP客户端接口"""
    
    @abstractmethod
    async def get(self, url: str, headers: Dict = None, timeout: int = 30) -> Any:
        """发送GET请求"""
        pass
    
    @abstractmethod
    async def post(self, url: str, json: Dict = None, headers: Dict = None, timeout: int = 30) -> Any:
        """发送POST请求"""
        pass