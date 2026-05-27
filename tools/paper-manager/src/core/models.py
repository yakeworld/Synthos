from typing import List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class Paper:
    """论文数据模型"""
    paper_id: str
    title: str
    authors: List[Dict]
    year: Optional[int]
    abstract: Optional[str]
    reference_count: Optional[int]
    citation_count: Optional[int]
    external_ids: Dict
    publication_venue: Dict
    open_access_pdf: Optional[Dict]
    journal: Optional[Dict]
    citation_styles: Optional[Dict]
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Paper':
        """从字典创建Paper对象"""
        return cls(
            paper_id=data.get('paperId') or data.get('paper_id') or '',
            title=data.get('title', ''),
            authors=data.get('authors', []),
            year=data.get('year'),
            abstract=data.get('abstract'),
            reference_count=data.get('referenceCount'),
            citation_count=data.get('citationCount'),
            external_ids=data.get('externalIds', {}),
            publication_venue=data.get('publicationVenue', {}),
            open_access_pdf=data.get('openAccessPdf'),
            journal=data.get('journal'),
            citation_styles=data.get('citationStyles')
        )


@dataclass
class BibtexEntry:
    """BibTeX条目数据模型"""
    entry_type: str
    key: str
    fields: Dict[str, Any]
    file_path: Optional[str] = None
    
    def to_bibtex_string(self) -> str:
        """转换为BibTeX字符串"""
        bibtex = f"@{self.entry_type}{{{self.key},\n"
        for field, value in self.fields.items():
            if field in ['referenceCount', 'citationCount', 'year']:
                bibtex += f"  {field} = {value},\n"
            else:
                bibtex += f"  {field} = {{{value}}},\n"
        bibtex = bibtex.rstrip(',\n') + "\n}"
        return bibtex


@dataclass
class DownloadResult:
    """下载结果数据模型"""
    success: bool
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class SearchResult:
    """搜索结果数据模型"""
    query: str
    papers: List[Paper]
    total_count: int
    output_dir: str


@dataclass
class ExpansionResult:
    """扩展结果数据模型"""
    seeds: List[str]
    expanded_papers: List[Paper]
    total_depth: int
    unique_count: int