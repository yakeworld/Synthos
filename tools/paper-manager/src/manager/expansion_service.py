import hashlib
import json
import logging
from typing import List, Dict, Optional, Callable
from collections import deque

from src.core.interfaces import IPaperProvider
from src.core.config import ExpansionOptions
from src.core.models import Paper, ExpansionResult
from src.utils.paper_id import normalize_paper_id, extract_seeds_from_bibtex

logger = logging.getLogger(__name__)

class PaperExpansionService:
    """文献扩展服务"""
    
    def __init__(self, paper_provider: IPaperProvider):
        self.paper_provider = paper_provider
    
    async def expand_papers(self, 
                          seeds: List[str],
                          options: ExpansionOptions = None,
                          callback: Callable[[int, int, str], None] = None) -> ExpansionResult:
        """
        扩展论文网络
        
        Args:
            seeds: 种子论文ID列表
            options: 扩展选项
            callback: 进度回调
            
        Returns:
            扩展结果
        """
        if options is None:
            options = ExpansionOptions()
        
        seen_ids = set()
        results = []
        queue = deque()
        
        # 初始化队列
        for seed in seeds:
            norm_seed = normalize_paper_id(seed)
            if norm_seed:
                queue.append((norm_seed, 0))
                seen_ids.add(norm_seed)
        
        total_queued = len(queue)
        
        while queue:
            pid, cur_depth = queue.popleft()
            
            if callback:
                callback(len(seen_ids), total_queued, f"Expanding {pid} (depth {cur_depth})")
            
            # 获取论文详情
            paper_data = await self.paper_provider.get_paper_details(pid)
            if not paper_data or not isinstance(paper_data, dict):
                continue
            
            paper_data['paperId'] = pid
            paper = Paper.from_dict(paper_data)
            results.append(paper)
            
            if cur_depth >= options.depth:
                continue
            
            # 扩展推荐文献
            if options.expand_recommend:
                recommendations = await self.paper_provider.get_recommendations(
                    pid, limit=options.limit_per_query
                )
                for rec in recommendations:
                    rec_id = rec.get('paperId') or rec.get('paper_id')
                    if rec_id and rec_id not in seen_ids:
                        queue.append((rec_id, cur_depth + 1))
                        seen_ids.add(rec_id)
                        total_queued += 1
            
            # 扩展被引文献
            if options.expand_citations:
                citations = await self.paper_provider.get_citations(
                    pid, limit=options.limit_per_query
                )
                for cite in citations:
                    cite_id = cite.get('paperId') or cite.get('paper_id')
                    if cite_id and cite_id not in seen_ids:
                        queue.append((cite_id, cur_depth + 1))
                        seen_ids.add(cite_id)
                        total_queued += 1
            
            # 扩展引用文献
            if options.expand_references:
                references = await self.paper_provider.get_references(
                    pid, limit=options.limit_per_query
                )
                for ref in references:
                    ref_id = ref.get('paperId') or ref.get('paper_id')
                    if ref_id and ref_id not in seen_ids:
                        queue.append((ref_id, cur_depth + 1))
                        seen_ids.add(ref_id)
                        total_queued += 1
            
            # 扩展作者论文
            if options.expand_authors:
                for author in (paper_data.get("authors") or []):
                    author_id = author.get("authorId") or author.get("author_id")
                    if not author_id:
                        continue
                    
                    author_papers = await self.paper_provider.get_author_papers(
                        author_id, limit=options.limit_per_query
                    )
                    for ap in author_papers:
                        ap_id = ap.get('paperId') or ap.get('paper_id')
                        if ap_id and ap_id not in seen_ids:
                            queue.append((ap_id, cur_depth + 1))
                            seen_ids.add(ap_id)
                            total_queued += 1
        
        # 去重
        unique_papers = self._deduplicate_papers(results)
        
        return ExpansionResult(
            seeds=seeds,
            expanded_papers=unique_papers,
            total_depth=options.depth,
            unique_count=len(unique_papers)
        )
    
    def _deduplicate_papers(self, papers: List[Paper]) -> List[Paper]:
        """论文去重"""
        unique_papers = []
        seen_hashes = set()
        
        for paper in papers:
            paper_hash = self._paper_hash(paper)
            if paper_hash not in seen_hashes:
                unique_papers.append(paper)
                seen_hashes.add(paper_hash)
        
        return unique_papers
    
    def _paper_hash(self, paper: Paper) -> str:
        """生成论文哈希值用于去重"""
        for key in ("paperId", "paper_id", "corpusId", "doi"):
            value = getattr(paper, key, None)
            if value:
                return str(value).lower()
        
        # 如果没有标准ID，使用内容哈希
        paper_dict = paper.__dict__.copy()
        # 移除可能变化的字段
        paper_dict.pop('reference_count', None)
        paper_dict.pop('citation_count', None)
        paper_dict.pop('open_access_pdf', None)
        
        return hashlib.md5(json.dumps(paper_dict, sort_keys=True).encode()).hexdigest()
    
    async def expand_from_bibtex(self,
                               bibtex_file: str,
                               options: ExpansionOptions = None,
                               callback: Callable[[int, int, str], None] = None) -> ExpansionResult:
        """
        从BibTeX文件扩展论文
        
        Args:
            bibtex_file: BibTeX文件路径
            options: 扩展选项
            callback: 进度回调
            
        Returns:
            扩展结果
        """
        seeds = extract_seeds_from_bibtex(bibtex_file)
        if not seeds:
            logger.warning(f"No valid seeds found in BibTeX file: {bibtex_file}")
            return ExpansionResult(
                seeds=[],
                expanded_papers=[],
                total_depth=options.depth if options else 1,
                unique_count=0
            )
        
        logger.info(f"Found {len(seeds)} seeds in BibTeX file")
        return await self.expand_papers(seeds, options, callback)
    
    async def expand_with_custom_strategy(self,
                                        seeds: List[str],
                                        strategy: Callable[[str, int], List[str]],
                                        options: ExpansionOptions = None,
                                        callback: Callable[[int, int, str], None] = None) -> ExpansionResult:
        """
        使用自定义策略扩展论文
        
        Args:
            seeds: 种子论文ID列表
            strategy: 自定义扩展策略函数
            options: 扩展选项
            callback: 进度回调
            
        Returns:
            扩展结果
        """
        if options is None:
            options = ExpansionOptions()
        
        seen_ids = set()
        results = []
        queue = deque()
        
        # 初始化队列
        for seed in seeds:
            norm_seed = normalize_paper_id(seed)
            if norm_seed:
                queue.append((norm_seed, 0))
                seen_ids.add(norm_seed)
        
        total_queued = len(queue)
        
        while queue:
            pid, cur_depth = queue.popleft()
            
            if callback:
                callback(len(seen_ids), total_queued, f"Expanding {pid} (depth {cur_depth})")
            
            # 获取论文详情
            paper_data = await self.paper_provider.get_paper_details(pid)
            if not paper_data or not isinstance(paper_data, dict):
                continue
            
            paper_data['paperId'] = pid
            paper = Paper.from_dict(paper_data)
            results.append(paper)
            
            if cur_depth >= options.depth:
                continue
            
            # 使用自定义策略获取相关论文
            related_papers = strategy(pid, cur_depth)
            for related_id in related_papers:
                norm_id = normalize_paper_id(related_id)
                if norm_id and norm_id not in seen_ids:
                    queue.append((norm_id, cur_depth + 1))
                    seen_ids.add(norm_id)
                    total_queued += 1
        
        # 去重
        unique_papers = self._deduplicate_papers(results)
        
        return ExpansionResult(
            seeds=seeds,
            expanded_papers=unique_papers,
            total_depth=options.depth,
            unique_count=len(unique_papers)
        )