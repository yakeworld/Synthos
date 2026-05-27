import os
from typing import List

class Config:
    """配置管理类"""
    
    def __init__(self):
        # API配置
        self.api_key = os.environ.get('SEMANTIC_SCHOLAR_API_KEY', '')
        if not self.api_key:
            # Fallback: read from local file
            import pathlib
            _key_file = pathlib.Path(__file__).parent / '.api_key'
            if _key_file.is_file():
                self.api_key = _key_file.read_text().strip()
        self.base_url = 'https://api.semanticscholar.org/graph/v1'
        self.recommendations_url = 'https://api.semanticscholar.org/recommendations/v1'
        
        # 下载配置
        self.max_concurrent_downloads = 5
        self.download_timeout = 120
        self.batch_size = 100
        
        # Sci-Hub镜像列表 (2026-05-27 实测11个可用)
        self.sci_hub_mirrors = [
            "https://sci-hub.ee/",
            "https://sci-hub.shop/",
            "https://sci-hub.ren/",
            "https://sci-hub.ru/",
            "https://sci-hub.red/",
            "https://sci-hub.al/",
            "https://sci-hub.vg/",
            "https://sci-hub.wf/",
            "https://sci-hub.es/",
            "https://sci-hub.box/",
            "https://sci-hub.yt/",
        ]
        
        # API字段配置
        self.fields = 'title,year,abstract,referenceCount,citationCount,publicationVenue,externalIds,openAccessPdf,journal,citationStyles'
        
        # 默认输出目录
        self.default_output_dir = os.path.join(os.getcwd(), "research")
        
    @property
    def headers(self) -> dict:
        """获取API请求头"""
        return {'x-api-key': self.api_key} if self.api_key else {}
    
    def update_from_env(self):
        """从环境变量更新配置"""
        if 'SEMANTIC_SCHOLAR_API_KEY' in os.environ:
            self.api_key = os.environ['SEMANTIC_SCHOLAR_API_KEY']
        
        if 'MAX_CONCURRENT_DOWNLOADS' in os.environ:
            try:
                self.max_concurrent_downloads = int(os.environ['MAX_CONCURRENT_DOWNLOADS'])
            except ValueError:
                pass
        
        if 'DOWNLOAD_TIMEOUT' in os.environ:
            try:
                self.download_timeout = int(os.environ['DOWNLOAD_TIMEOUT'])
            except ValueError:
                pass


class ExpansionOptions:
    """文献扩展选项"""
    
    def __init__(self):
        self.expand_references = True
        self.expand_citations = True
        self.expand_recommend = True
        self.expand_authors = False
        self.depth = 1
        self.limit_per_query = 30


class DownloadOptions:
    """下载选项"""
    
    def __init__(self):
        self.download_pdfs = True
        self.enhance_bibtex = True
        self.create_csv = True