import os
import re
import asyncio
import logging
from typing import Optional, List, Dict, Any

import aiohttp
import requests
from pdfminer.high_level import extract_text

from src.downloader.base_downloader import BaseDownloader
from src.core.config import Config
from src.utils.file_ops import ensure_directory_exists
from src.utils.async_helpers import async_retry

logger = logging.getLogger(__name__)


class PMCFullTextDownloader(BaseDownloader):
    """
    PubMed Central 全文下载器
    
    支持：
    1. PMC ID 全文XML获取
    2. 全文PDF下载
    3. 全文文本提取
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
    
    async def search_pmc(self, query: str, limit: int = 20) -> List[Dict]:
        """搜索PMC文章"""
        try:
            url = (
                f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
                f"db=pmc&term={query}&retmax={limit}&sort=relevance&retmode=json"
            )
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            id_list = data.get('esearchresult', {}).get('idlist', [])
            results = []
            
            # 获取摘要信息
            if id_list:
                summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id={','.join(id_list)}&retmode=json"
                resp = requests.get(summary_url, timeout=15)
                if resp.status_code == 200:
                    summary_data = resp.json().get('result', {})
                    for pmcid in id_list:
                        item = summary_data.get(str(pmcid), {})
                        if item:
                            results.append({
                                'pmcid': pmcid,
                                'title': item.get('title', ''),
                                'authors': item.get('authorlist', {}).get('author', []),
                                'journal': item.get('source', ''),
                                'year': item.get('pubdate', '').split(' ')[0] if item.get('pubdate') else None,
                                'url': f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/",
                                'pdf_url': f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/pdf/",
                                'abstract': item.get('abstract', '')
                            })
            
            return results[:limit]
        except Exception as e:
            logger.error(f"PMC search failed: {e}")
            return []
    
    async def download_full_text_xml(self, pmcid: str, save_path: str) -> str:
        """
        下载PMC全文XML
        
        Args:
            pmcid: PMC ID (不带"PMC"前缀)
            save_path: 保存路径
            
        Returns:
            保存的文件路径，失败返回空字符串
        """
        try:
            ensure_directory_exists(os.path.dirname(save_path))
            
            url = (
                f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
                f"db=pmc&id={pmcid}&retmode=xml"
            )
            
            async with self.session.get(url, headers={'User-Agent': 'ResearchPaperManager/1.0'}, timeout=120) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    if len(content) > 1000:
                        with open(save_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        logger.info(f"PMC full-text XML downloaded: {save_path} ({len(content)} chars)")
                        return save_path
            
            return ""
        except Exception as e:
            logger.error(f"PMC XML download failed for {pmcid}: {e}")
            return ""
    
    async def download_full_text_pdf(self, pmcid: str, save_path: str) -> str:
        """
        下载PMC全文PDF
        
        Args:
            pmcid: PMC ID (不带"PMC"前缀)
            save_path: 保存路径
            
        Returns:
            保存的文件路径，失败返回空字符串
        """
        try:
            ensure_directory_exists(os.path.dirname(save_path))
            
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/pdf/"
            
            async with self.session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=120) as resp:
                if resp.status == 200:
                    content_type = resp.headers.get('Content-Type', '')
                    if 'pdf' in content_type.lower():
                        with open(save_path, 'wb') as f:
                            while True:
                                chunk = await resp.content.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                        logger.info(f"PMC full-text PDF downloaded: {save_path}")
                        return save_path
                    else:
                        # 可能返回的是HTML，尝试直接下载PDF
                        text = await resp.text()
                        # 查找PDF链接
                        pdf_match = re.search(r'href=["\'](/pmc/articles/PMC\w+/bin/[^"\'>]+\.pdf)', text)
                        if pdf_match:
                            pdf_url = f"https://www.ncbi.nlm.nih.gov{pdf_match.group(1)}"
                            return await self.download_file(pdf_url, save_path)
            
            return ""
        except Exception as e:
            logger.error(f"PMC PDF download failed for {pmcid}: {e}")
            return ""
    
    async def extract_text_from_pdf(self, pdf_path: str, page_limit: int = 10) -> str:
        """
        从PDF提取文本
        
        Args:
            pdf_path: PDF文件路径
            page_limit: 最大提取页数
            
        Returns:
            提取的文本
        """
        try:
            if not os.path.exists(pdf_path):
                logger.error(f"PDF not found: {pdf_path}")
                return ""
            
            text = extract_text(pdf_path, page_numbers=range(page_limit))
            logger.info(f"Extracted {len(text)} characters from {pdf_path}")
            return text or ""
        except Exception as e:
            logger.error(f"Text extraction failed for {pdf_path}: {e}")
            return ""
    
    async def download_and_extract(self, pmcid: str, save_dir: str, filename: str = None) -> Dict:
        """下载PMC全文并提取文本"""
        if filename is None:
            filename = f"PMC{pmcid}"
        
        pdf_path = os.path.join(save_dir, f"{filename}.pdf")
        xml_path = os.path.join(save_dir, f"{filename}.xml")
        txt_path = os.path.join(save_dir, f"{filename}.txt")
        
        result = {'pmcid': pmcid, 'pdf_path': '', 'xml_path': '', 'text': ''}
        
        # 创建会话
        await self.create_session()
        
        # 尝试下载PDF
        pdf_result = await self.download_full_text_pdf(pmcid, pdf_path)
        if pdf_result:
            result['pdf_path'] = pdf_result
            # 提取文本
            text = await self.extract_text_from_pdf(pdf_result)
            if text:
                result['text'] = text
                ensure_directory_exists(os.path.dirname(txt_path))
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                result['text_path'] = txt_path
                logger.info(f"Text extracted to: {txt_path}")
        
        # 如果PDF失败，尝试XML
        if not pdf_result:
            xml_result = await self.download_full_text_xml(pmcid, xml_path)
            if xml_result:
                result['xml_path'] = xml_result
                # 从XML提取文本
                try:
                    import lxml.etree as ET
                    with open(xml_path, 'r', encoding='utf-8') as f:
                        xml_content = f.read()
                    root = ET.fromstring(xml_content.encode())
                    
                    text_parts = []
                    for abstract in root.findall('.//abstract//para'):
                        if abstract.text:
                            text_parts.append(abstract.text)
                    
                    if text_parts:
                        text = '\n\n'.join(text_parts)
                        result['text'] = text
                        ensure_directory_exists(os.path.dirname(txt_path))
                        with open(txt_path, 'w', encoding='utf-8') as f:
                            f.write(text)
                        result['text_path'] = txt_path
                except Exception as e:
                    logger.error(f"XML text extraction failed: {e}")
        
        return result