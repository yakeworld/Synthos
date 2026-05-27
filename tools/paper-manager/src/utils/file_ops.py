import os
import pandas as pd
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def ensure_directory_exists(directory: str) -> bool:
    """
    确保目录存在
    
    Args:
        directory: 目录路径
        
    Returns:
        是否成功创建目录
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False


def save_papers_to_csv(papers: List[Dict], csv_file: str) -> bool:
    """
    保存论文列表到CSV文件
    
    Args:
        papers: 论文数据列表
        csv_file: CSV文件路径
        
    Returns:
        是否保存成功
    """
    try:
        ensure_directory_exists(os.path.dirname(csv_file))
        df = pd.DataFrame(papers)
        df.to_csv(csv_file, index=False)
        logger.info(f"Saved {len(papers)} papers to {csv_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving papers to CSV {csv_file}: {e}")
        return False


def load_papers_from_csv(csv_file: str) -> List[Dict]:
    """
    从CSV文件加载论文数据
    
    Args:
        csv_file: CSV文件路径
        
    Returns:
        论文数据列表
    """
    try:
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return []
        
        df = pd.read_csv(csv_file)
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"Error loading papers from CSV {csv_file}: {e}")
        return []


def safe_file_write(content: str, filename: str, encoding: str = 'utf-8') -> bool:
    """
    安全写入文件
    
    Args:
        content: 文件内容
        filename: 文件名
        encoding: 编码格式
        
    Returns:
        是否写入成功
    """
    try:
        ensure_directory_exists(os.path.dirname(filename))
        with open(filename, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing to file {filename}: {e}")
        return False


def safe_file_read(filename: str, encoding: str = 'utf-8') -> str:
    """
    安全读取文件
    
    Args:
        filename: 文件名
        encoding: 编码格式
        
    Returns:
        文件内容
    """
    try:
        with open(filename, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
        return ""


def get_file_size(filename: str) -> int:
    """
    获取文件大小
    
    Args:
        filename: 文件名
        
    Returns:
        文件大小（字节），如果文件不存在返回-1
    """
    try:
        return os.path.getsize(filename) if os.path.exists(filename) else -1
    except Exception as e:
        logger.error(f"Error getting file size for {filename}: {e}")
        return -1


def file_exists_and_valid(filename: str, min_size: int = 100) -> bool:
    """
    检查文件是否存在且有效
    
    Args:
        filename: 文件名
        min_size: 最小文件大小（字节）
        
    Returns:
        文件是否存在且有效
    """
    if not os.path.exists(filename):
        return False
    
    try:
        size = os.path.getsize(filename)
        return size >= min_size
    except Exception:
        return False


def clean_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    # 移除非法字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # 限制文件名长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext
    
    return filename


def create_unique_filename(base_filename: str) -> str:
    """
    创建唯一的文件名
    
    Args:
        base_filename: 基础文件名
        
    Returns:
        唯一的文件名
    """
    if not os.path.exists(base_filename):
        return base_filename
    
    name, ext = os.path.splitext(base_filename)
    counter = 1
    while True:
        new_filename = f"{name}_{counter}{ext}"
        if not os.path.exists(new_filename):
            return new_filename
        counter += 1