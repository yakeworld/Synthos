"""
PDF文本提取工具

使用pdfminer.six进行PDF文本提取
支持：
- 全文文本提取
- 指定页码提取
- 表格提取
- 页面布局分析
"""

import os
import logging
from typing import Optional, List, Dict, Any, Tuple
from io import BytesIO

from pdfminer.high_level import extract_text, extract_pages
from pdfminer.layout import LTTextBox, LTTextLine, LTImage, LTFigure, LTTextBox, LTTextContainer

logger = logging.getLogger(__name__)


def extract_text_from_pdf(
    pdf_path: str,
    page_numbers: Optional[List[int]] = None,
    password: str = '',
    max_pages: int = 100,
    strip: bool = True
) -> str:
    """
    从PDF文件提取文本
    
    Args:
        pdf_path: PDF文件路径
        page_numbers: 要提取的页码列表（从0开始）
        password: PDF密码
        max_pages: 最大提取页数
        strip: 是否去除空白
        
    Returns:
        提取的文本
    """
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return ""
        
        # 检查文件大小
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            logger.error(f"Empty PDF file: {pdf_path}")
            return ""
        
        if file_size < 100:
            logger.error(f"PDF too small to be valid: {pdf_path} ({file_size} bytes)")
            return ""
        
        # 检查PDF文件头
        with open(pdf_path, 'rb') as f:
            header = f.read(5)
            if not header.startswith(b'%PDF-'):
                logger.error(f"Not a valid PDF file: {pdf_path}")
                return ""
        
        # 设置提取参数
        if page_numbers is None:
            start_page = 0
            end_page = max_pages
        else:
            start_page = page_numbers[0] if page_numbers else 0
            end_page = (page_numbers[-1] + 1) if page_numbers else max_pages
        
        text = extract_text(
            pdf_file=pdf_path,
            page_numbers=page_numbers,
            maxpages=max_pages,
            password=password,
            caching=True
        )
        
        if text and strip:
            # 清理空白字符
            lines = text.split('\n')
            cleaned_lines = [line.rstrip() for line in lines if line.strip()]
            text = '\n'.join(cleaned_lines)
        
        logger.info(f"Extracted {len(text)} characters from {pdf_path}")
        return text or ""
    
    except Exception as e:
        logger.error(f"Text extraction failed for {pdf_path}: {e}")
        return ""


def extract_text_from_pdf_bytes(
    pdf_bytes: bytes,
    page_numbers: Optional[List[int]] = None,
    max_pages: int = 100,
    strip: bool = True
) -> str:
    """
    从PDF字节数据提取文本
    
    Args:
        pdf_bytes: PDF字节数据
        page_numbers: 要提取的页码列表
        max_pages: 最大提取页数
        strip: 是否去除空白
        
    Returns:
        提取的文本
    """
    try:
        text = extract_text(
            fileobj=BytesIO(pdf_bytes),
            page_numbers=page_numbers,
            maxpages=max_pages,
            caching=True,
            out_type='text'
        )
        
        if text and strip:
            lines = text.split('\n')
            cleaned_lines = [line.rstrip() for line in lines if line.strip()]
            text = '\n'.join(cleaned_lines)
        
        logger.info(f"Extracted {len(text)} characters from PDF bytes")
        return text or ""
    
    except Exception as e:
        logger.error(f"PDF bytes extraction failed: {e}")
        return ""


def extract_pages_layout(
    pdf_path: str,
    page_number: int = 0
) -> List[Dict]:
    """
    提取页面布局信息（文本框、图像等）
    
    Args:
        pdf_path: PDF文件路径
        page_number: 页码（从0开始）
        
    Returns:
        布局信息列表
    """
    try:
        layouts = []
        for page_layout in extract_pages(
            pdf_file=pdf_path,
            page_numbers=[page_number]
        ):
            elements = []
            for element in page_layout:
                elem_info = {
                    'type': type(element).__name__,
                    'width': getattr(element, 'width', 0),
                    'height': getattr(element, 'height', 0),
                    'left': getattr(element, 'x0', 0),
                    'bottom': getattr(element, 'y0', 0),
                }
                
                if isinstance(element, (LTTextBox, LTTextContainer)):
                    text = ''
                    for text_line in element:
                        if isinstance(text_line, LTTextLine):
                            text += text_line.get_text()
                    elem_info['text'] = text
                    elem_info['font_size'] = getattr(text_line, 'size', 0) if 'text_line' in locals() else 0
                
                elements.append(elem_info)
            
            layouts.append({
                'page': page_number,
                'elements': elements,
                'width': page_layout.width,
                'height': page_layout.height
            })
        
        return layouts
    
    except Exception as e:
        logger.error(f"Layout extraction failed for {pdf_path}: {e}")
        return []


def extract_tables_from_pdf(
    pdf_path: str,
    page_number: int = 0
) -> List[List[List[str]]]:
    """
    从PDF提取表格
    
    Args:
        pdf_path: PDF文件路径
        page_number: 页码
        
    Returns:
        表格数据（二维列表的列表）
    """
    try:
        from pdfminer.high_level import extract_table
        
        tables = extract_table(
            pdf_file=pdf_path,
            page_numbers=[page_number]
        )
        
        return tables or []
    
    except Exception as e:
        logger.error(f"Table extraction failed for {pdf_path}: {e}")
        return []


def classify_pdf_content(text: str) -> Dict[str, Any]:
    """
    分类PDF内容类型
    
    Args:
        text: 提取的文本
        
    Returns:
        内容类型分类
    """
    result = {
        'type': 'unknown',
        'sections': [],
        'has_figure': False,
        'has_table': False,
        'word_count': 0,
        'confidence': 0.0
    }
    
    if not text or len(text) < 100:
        return result
    
    # 统计词数
    result['word_count'] = len(text.split())
    
    # 检测图片
    image_patterns = ['figure', 'fig.', 'image', '图片', '图']
    for pattern in image_patterns:
        if pattern.lower() in text.lower():
            result['has_figure'] = True
            break
    
    # 检测表格
    table_patterns = ['table', 'tab.', '表格', '表']
    for pattern in table_patterns:
        if pattern.lower() in text.lower():
            result['has_table'] = True
            break
    
    # 检测论文类型
    if any(pattern in text.lower() for pattern in ['abstract', 'introduction', 'method', 'result', 'discussion', 'conclusion']):
        result['type'] = 'academic_paper'
        result['confidence'] = 0.9
    
    elif any(pattern in text.lower() for pattern in ['introduction', 'background', 'methodology', 'conclusion', 'references']):
        result['type'] = 'research_paper'
        result['confidence'] = 0.85
    
    elif any(pattern in text.lower() for pattern in ['how to', 'tutorial', 'guide', '步骤', '教程']):
        result['type'] = 'tutorial'
        result['confidence'] = 0.8
    
    elif result['word_count'] > 500:
        result['type'] = 'document'
        result['confidence'] = 0.5
    
    # 提取章节标题
    import re
    section_pattern = r'^(#{1,3}\s+|\\section\{|\\chapter\{|[A-Z][A-Z\s]{5,30}|[一二三四五六七八九十]+[、.、]\s)[^\n]+'
    sections = re.findall(section_pattern, text, re.MULTILINE)
    result['sections'] = [s.strip()[:100] for s in sections[:20]]
    
    return result


def summarize_text(text: str, max_length: int = 500) -> str:
    """
    简单文本摘要（基于最高频句子）
    
    Args:
        text: 输入文本
        max_length: 最大摘要长度
        
    Returns:
        摘要文本
    """
    if not text or len(text) < max_length:
        return text
    
    # 按句子分割
    import re
    sentences = re.split(r'(?<=[.!?。！？])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if not sentences:
        return text[:max_length]
    
    # 取前几个句子作为摘要
    summary_parts = []
    total_length = 0
    
    for sentence in sentences:
        if total_length + len(sentence) > max_length:
            break
        summary_parts.append(sentence)
        total_length += len(sentence)
    
    return ' '.join(summary_parts)


def extract_metadata(pdf_path: str) -> Dict[str, Any]:
    """
    提取PDF元数据
    
    Args:
        pdf_path: PDF文件路径
        
    Returns:
        元数据字典
    """
    result = {
        'title': '',
        'author': '',
        'subject': '',
        'creator': '',
        'producer': '',
        'creation_date': '',
        'modification_date': '',
        'page_count': 0
    }
    
    try:
        import pikepdf
        
        if not os.path.exists(pdf_path):
            return result
        
        doc = pikepdf.open(pdf_path)
        
        # Get document info
        docinfo = doc.docinfo
        if docinfo:
            for key in ('/Title', '/Author', '/Subject', '/Creator', '/Producer'):
                val = docinfo.get(key, '')
                if val:
                    clean_key = key.lstrip('/').lower()
                    result[clean_key] = str(val).strip()
        
        result['page_count'] = len(doc.pages)
        result['pdf_version'] = str(doc.pdf_version)
        
        doc.close()
    
    except Exception as e:
        logger.error(f"Metadata extraction failed for {pdf_path}: {e}")
    
    return result


def validate_pdf(pdf_path: str) -> Tuple[bool, str]:
    """
    验证PDF文件是否有效
    
    Args:
        pdf_path: PDF文件路径
        
    Returns:
        (是否有效, 错误消息)
    """
    try:
        if not os.path.exists(pdf_path):
            return False, "File not found"
        
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            return False, "File is empty"
        
        if file_size < 100:
            return False, "File too small to be valid PDF"
        
        with open(pdf_path, 'rb') as f:
            header = f.read(5)
            if not header.startswith(b'%PDF-'):
                return False, "Invalid PDF header"
        
        # 尝试读取
        try:
            import pikepdf
            with pikepdf.open(pdf_path) as pdf:
                pass  # If it opens without error, it's valid
    
        except Exception as e:
            return False, f"Cannot read PDF: {str(e)}"
        
        return True, "Valid PDF"
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"