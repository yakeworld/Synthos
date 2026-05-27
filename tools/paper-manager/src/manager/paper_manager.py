import os
import asyncio
import logging
import pandas as pd
from typing import List, Dict, Optional, Tuple, Callable, Any
from concurrent.futures import ThreadPoolExecutor

from src.core.interfaces import IPaperProvider, IDownloader, IBibtexConverter
from src.core.config import Config, ExpansionOptions, DownloadOptions
from src.core.models import Paper, SearchResult, ExpansionResult, DownloadResult
from src.utils.paper_id import normalize_paper_id, extract_seeds_from_bibtex
from src.utils.file_ops import save_papers_to_csv, ensure_directory_exists
from src.utils.async_helpers import batch_process, progress_callback_wrapper
from src.api.multi_database_search import MultiDatabaseSearchClient, UnifiedPaper

logger = logging.getLogger(__name__)


class ResearchPaperManager:
    """研究论文管理器 - 增强版，支持多数据库搜索"""
    
    def __init__(self, 
                 paper_provider: IPaperProvider,
                 downloader: IDownloader,
                 converter: IBibtexConverter,
                 config: Config = None):
        self.paper_provider = paper_provider
        self.downloader = downloader
        self.converter = converter
        self.config = config or Config()
        # 创建多数据库搜索客户端
        self.multi_search = MultiDatabaseSearchClient(config)
    
    async def search_and_download(
        self,
        query: str,
        output_dir: str,
        download_pdfs: bool = True,
        callback: Callable[[int, int, str], None] = None,
        max_results: int = 20
    ) -> SearchResult:
        """
        搜索并下载论文
        
        Args:
            query: 搜索查询
            output_dir: 输出目录
            download_pdfs: 是否下载PDF
            callback: 进度回调
            
        Returns:
            搜索结果
        """
        ensure_directory_exists(output_dir)
        
        if callback:
            callback(0, 1, "Searching papers...")
        
        papers_data = await self.paper_provider.search_papers(query, limit=min(max_results, 100))
        papers = [Paper.from_dict(data) for data in papers_data]
        
        # 保存到CSV
        csv_file = os.path.join(output_dir, 'results.csv')
        save_papers_to_csv(papers_data, csv_file)
        
        pdf_dir = ""
        if download_pdfs and papers:
            pdf_dir = os.path.join(output_dir, 'pdfs')
            ensure_directory_exists(pdf_dir)
            
            await self.downloader.create_session()
            
            async def download_paper_wrapper(paper: Paper, index: int, total: int) -> DownloadResult:
                if callback:
                    callback(index, total, f"Downloading: {paper.title}")
                
                external_ids = paper.external_ids
                doi = external_ids.get('DOI', '')
                # Semantic Scholar uses 'ArXiv' (capital A, V)
                arxiv_id = external_ids.get('ArXiv') or external_ids.get('arXiv', '')
                
                if not doi and not arxiv_id:
                    logger.warning(f"No DOI or arXiv ID found for paper: {paper.title}")
                    return DownloadResult(success=False, error_message="No identifier found")
                
                # 使用BibTeX键作为文件名
                key, _ = self.converter.create_bibtex_entry(paper.__dict__)
                filename = f"{key}.pdf"
                file_path = os.path.join(pdf_dir, filename)
                
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    logger.info(f"PDF file already exists at {file_path}")
                    return DownloadResult(success=True, file_path=file_path)
                
                if doi:
                    downloaded_path = await self.downloader.get_paper_pdf(doi, pdf_dir, filename, paper.open_access_pdf)
                    if downloaded_path:
                        return DownloadResult(success=True, file_path=downloaded_path)
                
                if arxiv_id:
                    downloaded_path = await self.downloader.get_paper_pdf(f"arXiv:{arxiv_id}", pdf_dir, filename, paper.open_access_pdf)
                    if downloaded_path:
                        return DownloadResult(success=True, file_path=downloaded_path)
                
                return DownloadResult(success=False, error_message="Download failed")
            
            download_results = await progress_callback_wrapper(
                papers, download_paper_wrapper, callback
            )
            
            await self.downloader.close_session()
            
            successful_downloads = sum(1 for result in download_results if result.success)
            logger.info(f"Successfully downloaded {successful_downloads} of {len(papers)} PDFs")
        
        # 生成BibTeX文件
        bib_file = os.path.join(output_dir, 'references.bib')
        try:
            self.converter.convert_csv_to_bib(csv_file, bib_file, pdf_dir)
        except Exception as e:
            logger.error(f"Error during BibTeX conversion: {e}")
            if callback:
                raise Exception(f"Error during BibTeX conversion: {e}")
        
        return SearchResult(
            query=query,
            papers=papers,
            total_count=len(papers),
            output_dir=output_dir
        )
    
    async def multi_database_search(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        limit_per_source: int = 20,
        download_pdfs: bool = True,
        output_dir: str = './research',
        callback: Optional[Callable[[int, int, str], None]] = None,
        parallel: bool = False
    ) -> Dict[str, Any]:
        """
        多数据库搜索
        
        Args:
            query: 搜索查询
            sources: 要搜索的数据库列表
            limit_per_source: 每个数据库返回结果数
            download_pdfs: 是否下载PDF
            output_dir: 输出目录
            callback: 进度回调函数
            
        Returns:
            包含所有结果的字典
        """
        ensure_directory_exists(output_dir)
        
        if callback:
            callback(0, 1, "Multi-database searching...")
        
        # 多数据库搜索
        papers = await self.multi_search.search_all(
            query, sources, limit_per_source, deduplicate=True
        )
        
        if callback:
            callback(len(papers), len(papers), f"Found {len(papers)} papers")
        
        # 转换为标准格式
        papers_data = [p.to_dict() for p in papers]
        
        # 保存到CSV
        csv_file = os.path.join(output_dir, 'results_multi.csv')
        save_papers_to_csv(papers_data, csv_file)
        
        # 下载PDF
        download_results = []
        if download_pdfs:
            pdf_dir = os.path.join(output_dir, 'pdfs')
            ensure_directory_exists(pdf_dir)
            
            await self.downloader.create_session()
            
            download_results = []
            for i, paper in enumerate(papers):
                if callback:
                    callback(i, len(papers), f"Downloading: {paper.title}")
                
                filename = f"{i+1}_{paper.title[:50]}.pdf"
                file_path = os.path.join(pdf_dir, filename)
                
                # 尝试从多个来源下载
                success = False
                
                # 1. 直接PDF URL
                if paper.pdf_url:
                    success = await self.downloader.download_file(paper.pdf_url, file_path)
                
                # 2. 通过DOI下载
                if not success and paper.doi:
                    success = await self.downloader.download_pdf(paper.doi, file_path)
                
                # 3. 通过arXiv ID下载
                arxiv_id = paper.external_ids.get('ArXiv') or paper.external_ids.get('arXiv')
                if not success and arxiv_id:
                    arxiv_pdf = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    success = await self.downloader.download_file(arxiv_pdf, file_path)
                
                download_results.append({
                    'title': paper.title,
                    'success': success,
                    'path': file_path if success else ''
                })
            
            await self.downloader.close_session()
            
            successful = sum(1 for r in download_results if r['success'])
            logger.info(f"Multi-database download: {successful}/{len(download_results)} PDFs downloaded")
        
        return {
            'total_papers': len(papers),
            'papers_data': papers_data,
            'download_results': download_results,
            'csv_file': csv_file
        }
    
    async def download_and_enhance_bibtex(
        self,
        bibtex_file: str,
        output_dir: str,
        enhanced_bibtex_file: str = None,
        callback: Callable[[int, int, str], None] = None
    ) -> Tuple[int, int, str]:
        """
        下载并增强BibTeX文件
        
        Args:
            bibtex_file: 输入BibTeX文件
            output_dir: 输出目录
            enhanced_bibtex_file: 增强的BibTeX文件路径
            callback: 进度回调
            
        Returns:
            (成功下载数, 总条目数, 增强文件路径)
        """
        if enhanced_bibtex_file is None:
            base_name = os.path.splitext(os.path.basename(bibtex_file))[0]
            enhanced_bibtex_file = os.path.join(output_dir, f"{base_name}_enhanced.bib")
        
        ensure_directory_exists(output_dir)
        logger.info(f"Enhancing BibTeX entries from {bibtex_file}")
        
        if callback:
            callback(0, 1, "Loading BibTeX entries...")
        
        entries = self.converter.parse_bibtex_file_for_enhancement(bibtex_file)
        total_entries = len(entries)
        enhanced_entries = [None] * total_entries
        success_downloads = 0
        pdf_dir = os.path.join(output_dir, 'pdfs')
        ensure_directory_exists(pdf_dir)
        
        await self.downloader.create_session()
        
        # 高速批量异步增强
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=32) as pool:
            fetch_tasks = [
                loop.run_in_executor(pool, self._fetch_semantic_scholar_data_sync, entry) 
                for entry in entries
            ]
            enhanced_batch = await asyncio.gather(*fetch_tasks)
        
        for idx, enhanced in enumerate(enhanced_batch):
            enhanced_entries[idx] = enhanced
        
        # 高速批量异步下载PDF
        async def process_pdf(idx: int, enhanced_entry: Dict) -> Dict:
            nonlocal success_downloads
            if callback:
                callback(idx, total_entries, f"Processing {idx+1}/{total_entries}: {enhanced_entry.get('ID', 'Unknown')}")
            
            pdf_downloaded = False
            pdf_url = enhanced_entry.get('pdf_url', '')
            
            if isinstance(pdf_url, str) and pdf_url.startswith(('http://', 'https://')):
                pdf_filename = os.path.join(pdf_dir, f"{enhanced_entry.get('ID', f'paper_{idx}')}.pdf")
                if self.downloader.download_paper_sync(pdf_url, pdf_filename):
                    logger.info(f"Successfully downloaded paper to {pdf_filename}")
                    pdf_downloaded = True
                    success_downloads += 1
                    rel_pdf_path = os.path.relpath(pdf_filename, os.path.dirname(enhanced_bibtex_file))
                    enhanced_entry['file'] = f":{rel_pdf_path}:PDF"
            elif pdf_url:
                logger.warning(f"pdf_url exists but is not a valid http(s) link: '{pdf_url}'")
            
            if not pdf_downloaded:
                paper = {
                    'key': enhanced_entry.get('ID', f'paper_{idx}'),
                    'doi': enhanced_entry.get('doi', ''),
                    'arxiv': enhanced_entry.get('eprint', '') if enhanced_entry.get('archiveprefix', '').lower() == 'arxiv' else '',
                    'title': enhanced_entry.get('title', '')
                }
                if paper['doi'] or paper['arxiv']:
                    pdf_path = await self._download_paper_async(paper, pdf_dir)
                    if pdf_path and os.path.exists(pdf_path):
                        success_downloads += 1
                        pdf_downloaded = True
                        rel_pdf_path = os.path.relpath(pdf_path, os.path.dirname(enhanced_bibtex_file))
                        enhanced_entry['file'] = f":{rel_pdf_path}:PDF"
            
            return enhanced_entry
        
        batch_size = 32
        for batch_start in range(0, total_entries, batch_size):
            batch_end = min(batch_start + batch_size, total_entries)
            batch_tasks = [process_pdf(i, enhanced_entries[i]) for i in range(batch_start, batch_end)]
            results = await asyncio.gather(*batch_tasks)
            for i, res in enumerate(results):
                enhanced_entries[batch_start + i] = res
            await asyncio.sleep(0.05)
            
            if batch_end % 100 == 0 or batch_end == total_entries:
                try:
                    temp_file = os.path.join(output_dir, f"temp_enhanced_{batch_end}.bib")
                    self.converter.save_enhanced_bibtex(enhanced_entries[:batch_end], temp_file)
                    logger.info(f"Saved intermediate results through entry {batch_end}")
                except Exception as e:
                    logger.error(f"Error saving intermediate results: {e}")
        
        self.converter.save_enhanced_bibtex(enhanced_entries, enhanced_bibtex_file)
        await self.downloader.close_session()
        
        # 清理临时文件
        for file in os.listdir(output_dir):
            if file.startswith("temp_enhanced_") and file.endswith(".bib"):
                try:
                    os.remove(os.path.join(output_dir, file))
                except Exception:
                    pass
        
        logger.info(f"Enhanced BibTeX saved to {enhanced_bibtex_file}")
        logger.info(f"Downloaded {success_downloads} of {total_entries} PDFs")
        return success_downloads, total_entries, enhanced_bibtex_file
    
    def _fetch_semantic_scholar_data_sync(self, entry: Dict) -> Dict:
        """同步获取Semantic Scholar数据"""
        return entry
    
    async def _download_paper_async(self, paper: Dict, pdf_dir: str) -> Optional[str]:
        """异步下载论文"""
        try:
            if paper['doi']:
                return await self.downloader.get_paper_pdf(paper['doi'], pdf_dir, f"{paper['key']}.pdf")
            elif paper['arxiv']:
                return await self.downloader.get_paper_pdf(f"arXiv:{paper['arxiv']}", pdf_dir, f"{paper['key']}.pdf")
        except Exception as e:
            logger.error(f"Error downloading paper {paper['title']}: {e}")
        return None