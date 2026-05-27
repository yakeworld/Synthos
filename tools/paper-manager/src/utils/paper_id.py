import re
import hashlib
import json
import os


def normalize_paper_id(pid: str) -> str:
    """
    归一化论文ID
    
    支持多种格式：
    - arXiv: 1234.5678, arXiv:1234.5678, 10.48550/arXiv.1234.5678
    - DOI: 10.1234/test, DOI:10.1234/test
    - CorpusID: 12345678, CorpusID:12345678
    - PMID: 12345678, PMID:12345678
    - PMC: PMC1234567, PMC1234567
    - S2 PaperId: 40位hex
    - 原始ID
    
    Args:
        pid: 论文ID
        
    Returns:
        归一化后的论文ID
    """
    if not pid:
        return ''
    
    pid = pid.strip()
    
    # arXiv DOI (10.48550/arXiv.xxx)
    m = re.match(r'10\.48550/arXiv\.(\d{4}\.\d{4,5}(v\d+)?)', pid)
    if m:
        return f"ARXIV:{m.group(1)}"
    
    # arXiv DOI (https://arxiv.org/abs/xxx)
    m = re.match(r'(?:https?://)?arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5}(v\d+)?)', pid)
    if m:
        return f"ARXIV:{m.group(1)}"
    
    # arXiv ID直接格式
    if re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', pid):
        return f"ARXIV:{pid}"
    
    # arXiv前缀格式
    m = re.match(r'^(?:arXiv|ARXIV)[:\s]+(.+)$', pid, re.IGNORECASE)
    if m and re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', m.group(1).strip()):
        return f"ARXIV:{m.group(1).strip()}"
    
    # CorpusID
    m = re.match(r'^(?:CorpusID|corpusid)[:\s]+(\d+)$', pid, re.IGNORECASE)
    if m:
        return f"CorpusID:{m.group(1)}"
    if pid.isdigit() and len(pid) >= 6:
        return f"CorpusID:{pid}"
    
    # PMID
    m = re.match(r'^(?:PMID|pmid)[:\s]+(\d+)$', pid, re.IGNORECASE)
    if m:
        return f"PMID:{m.group(1)}"
    
    # PMC
    m = re.match(r'^(?:PMC|pmc)(\d+)$', pid)
    if m:
        return f"PMC:{m.group(1)}"
    
    # DOI
    m = re.match(r'(?:DOI|doi)[:\s]*([1-9]\d*/[-._;()/:A-Z0-9]+)$', pid, re.IGNORECASE)
    if m:
        return f"DOI:{m.group(1)}"
    
    # DOI URL (doi.org/xxx)
    m = re.match(r'(?:https?://)?doi\.org/(.+)$', pid)
    if m:
        return f"DOI:{m.group(1)}"
    
    # DOI直接格式
    if re.match(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', pid, re.IGNORECASE):
        return f"DOI:{pid}"
    
    # S2 PaperId (40位hex)
    if re.match(r'^[a-f0-9]{40}$', pid):
        return pid
    
    # 原始ID
    return pid


def extract_paper_id_from_data(data: dict) -> str:
    """
    从论文数据中提取论文ID
    
    Args:
        data: 论文数据字典
        
    Returns:
        论文ID
    """
    pid = (
        data.get('paperId') or data.get('paper_id') or 
        data.get('corpusId') or data.get('doi')
    )
    if not pid:
        # 如果没有ID，使用哈希值
        pid = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    return pid


def is_valid_arxiv_id(arxiv_id: str) -> bool:
    """
    检查是否为有效的arXiv ID
    
    Args:
        arxiv_id: arXiv ID
        
    Returns:
        是否为有效ID
    """
    patterns = [
        r'^\d{4}\.\d{4,5}(v\d+)?$',
        r'^[a-z\-]+/\d{7}$'
    ]
    return any(re.match(pattern, arxiv_id) for pattern in patterns)


def is_valid_doi(doi: str) -> bool:
    """
    检查是否为有效的DOI
    
    Args:
        doi: DOI字符串
        
    Returns:
        是否为有效DOI
    """
    return bool(re.match(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', doi, re.IGNORECASE))


def extract_seeds_from_bibtex(bibtex_file: str) -> list:
    """
    从BibTeX文件中提取种子ID
    
    Args:
        bibtex_file: BibTeX文件路径
        
    Returns:
        种子ID列表
    """
    try:
        import bibtexparser
        seeds = []
        with open(bibtex_file, 'r', encoding='utf-8') as f:
            bib_database = bibtexparser.load(f)
        
        for entry in bib_database.entries:
            pid = (
                entry.get('paperid') or entry.get('corpusid') or entry.get('id') or
                entry.get('doi') or entry.get('arxiv') or entry.get('arxivid') or entry.get('eprint')
            )
            if pid:
                seeds.append(pid)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error extracting seeds from BibTeX file {bibtex_file}: {e}")
    
    return [s for s in seeds if s]


def get_relative_pdf_path(pdf_path: str, bib_dir: str) -> str:
    """
    获取PDF文件的相对路径
    
    Args:
        pdf_path: PDF文件路径
        bib_dir: BibTeX文件所在目录
        
    Returns:
        相对路径
    """
    try:
        return os.path.relpath(pdf_path, bib_dir)
    except Exception:
        return os.path.basename(pdf_path)