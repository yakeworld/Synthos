"""
数据源注册表
"""
from .semantic_scholar import SemanticScholar
from .pubmed import PubMed
from .crossref import CrossRef
from .openalex import OpenAlex
from .arxiv import ArXiv
from .pubscholar import PubScholar
from .scihub import SciHub
from .libgen import LibGen

# Registry: source_name -> class
SOURCE_REGISTRY = {
    "semantic_scholar": SemanticScholar,
    "pubmed": PubMed,
    "crossref": CrossRef,
    "openalex": OpenAlex,
    "arxiv": ArXiv,
    "pubscholar": PubScholar,
    "scihub": SciHub,
    "libgen": LibGen,
}

# Default sources to query
DEFAULT_SOURCES = ["semantic_scholar", "pubmed", "crossref", "arxiv", "pubscholar"]

__all__ = ["SOURCE_REGISTRY", "DEFAULT_SOURCES", "SemanticScholar", "PubMed", "CrossRef", "OpenAlex", "ArXiv", "PubScholar", "SciHub", "LibGen"]