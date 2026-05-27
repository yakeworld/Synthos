#!/usr/bin/env python3
"""
Research Paper Manager - 研究论文管理器
模块化重构版本 - 增强优化版
Version: 2.0.1 - Fixed API 403 and empty result handling
"""

import argparse
import asyncio
import os
import sys
import logging
import json
import re
import signal
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import traceback

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 尝试导入可选依赖
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

from src.core.config import Config
from src.manager.paper_manager import ResearchPaperManager
from src.api.semantic_scholar import SemanticScholarClient
from src.api.multi_database_search import MultiDatabaseSearchClient
from src.downloader.pdf_downloader import PDFDownloader
from src.downloader.pmctext_downloader import PMCFullTextDownloader
from src.converter.bibtex_converter import BibTexConverter
from src.manager.expansion_service import PaperExpansionService
from src.utils.paper_id import normalize_paper_id, extract_seeds_from_bibtex
from src.ui.main_window import ResearchGUI
from src.skills.registry import skill_registry

# 版本信息
__version__ = "2.0.1"
__author__ = "Research Paper Manager Team"

# 配置日志
def setup_logging(verbose: bool = False, debug: bool = False, log_file: str = 'research_paper_manager.log'):
    """可配置的日志设置"""
    level = logging.DEBUG if debug else (logging.INFO if not verbose else logging.WARNING)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    # 清除已有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # 减少第三方库的日志噪音
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    return root_logger

logger = logging.getLogger(__name__)


class DownloadResumeManager:
    """管理中断的下载任务恢复"""
    
    def __init__(self, state_file: str = 'download_state.json'):
        self.state_file = Path(state_file)
        self.state = self.load_state()
    
    def load_state(self) -> Dict:
        """加载保存的状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load state file: {e}")
        return {}
    
    def save_state(self, paper_id: str, status: str, path: Optional[str] = None, metadata: Dict = None):
        """保存下载状态"""
        self.state[paper_id] = {
            'status': status,
            'path': path,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def get_pending_downloads(self) -> List[str]:
        """获取未完成的下载任务"""
        return [pid for pid, info in self.state.items() 
                if info.get('status') in ['pending', 'failed']]
    
    def clear_state(self):
        """清空状态"""
        self.state = {}
        if self.state_file.exists():
            self.state_file.unlink()


class RateLimiter:
    """API请求速率限制器"""
    
    def __init__(self, requests_per_second: float = 5.0):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """获取请求许可"""
        async with self._lock:
            now = asyncio.get_event_loop().time()
            time_since_last = now - self.last_request_time
            if time_since_last < self.min_interval:
                await asyncio.sleep(self.min_interval - time_since_last)
            self.last_request_time = asyncio.get_event_loop().time()


def validate_api_key(key: str) -> bool:
    """验证API密钥格式"""
    return bool(key and len(key) > 10 and not any(c in key for c in ' \t\n'))


def sanitize_path(path: str) -> str:
    """防止路径遍历攻击"""
    # 规范化路径
    normalized = os.path.normpath(path)
    # 检查路径遍历
    if os.path.basename(normalized) != normalized and '..' in normalized:
        raise ValueError(f"Invalid path: {path}")
    # 清理文件名中的非法字符
    dirname = os.path.dirname(normalized)
    basename = os.path.basename(normalized)
    clean_basename = re.sub(r'[<>:"|?*\\/]', '_', basename)
    return os.path.join(dirname, clean_basename)


def validate_config(config: Config) -> None:
    """验证配置有效性"""
    if config.max_concurrent_downloads < 1:
        raise ValueError("Concurrency must be at least 1")
    if config.max_concurrent_downloads > 50:
        logger.warning(f"High concurrency {config.max_concurrent_downloads} may cause rate limiting")
    if config.download_timeout < 10:
        raise ValueError("Timeout must be at least 10 seconds")
    if config.download_timeout > 600:
        logger.warning(f"Long timeout {config.download_timeout} seconds may cause delays")
    
    # 验证输出目录
    if hasattr(config, 'output_dir') and config.output_dir:
        output_path = Path(config.output_dir)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot create output directory {config.output_dir}: {e}")


class ProgressTracker:
    """长时间操作的进度跟踪器"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1, message: str = ""):
        """更新进度"""
        self.current += increment
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if self.total > 0:
            percentage = (self.current / self.total) * 100
            eta = (elapsed / self.current) * (self.total - self.current) if self.current > 0 else 0
            progress_str = f"\r{self.description}: {self.current}/{self.total} ({percentage:.1f}%)"
            if eta > 0:
                progress_str += f" - ETA: {eta:.1f}s"
            if message:
                progress_str += f" - {message}"
            print(progress_str, end="", flush=True)
        else:
            print(f"\r{self.description}: {self.current} - {message}", end="", flush=True)
    
    def finish(self, message: str = "Complete"):
        """完成进度"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"\n{self.description}: {message} in {elapsed:.1f}s")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.finish()
        else:
            self.finish(f"Failed: {exc_val}")


async def health_check(api_client: SemanticScholarClient) -> Dict[str, Any]:
    """检查所有服务是否正常"""
    checks = {
        'timestamp': datetime.now().isoformat(),
        'version': __version__,
        'config': 'OK',
        'api_client': 'Unknown',
        'dependencies': {}
    }
    
    # 检查依赖
    checks['dependencies']['pandas'] = 'Available' if PANDAS_AVAILABLE else 'Not installed'
    checks['dependencies']['python-dotenv'] = 'Available' if DOTENV_AVAILABLE else 'Not installed'
    
    # 测试API连接
    try:
        # 简单的测试查询
        test_result = await api_client.search_papers("machine learning", limit=1)
        if test_result and len(test_result) > 0:
            checks['api_client'] = 'OK'
        else:
            checks['api_client'] = 'Warning: Empty response'
    except Exception as e:
        checks['api_client'] = f'Failed: {str(e)}'
    
    return checks


def load_environment():
    """加载环境变量"""
    if DOTENV_AVAILABLE:
        # 尝试加载.env文件
        env_files = ['.env', '.env.local', 'config/.env']
        for env_file in env_files:
            if Path(env_file).exists():
                load_dotenv(env_file)
                logger.info(f"Loaded environment from {env_file}")
                break
        else:
            load_dotenv()  # 默认查找
    
    # 检查必要的环境变量
    api_key = os.environ.get('SEMANTIC_SCHOLAR_API_KEY')
    if not api_key:
        logger.warning("SEMANTIC_SCHOLAR_API_KEY not set. API calls may be rate limited.")


def parse_args():
    """解析命令行参数（增强版）"""
    parser = argparse.ArgumentParser(
        description='Research Paper Manager - Comprehensive Academic Paper Management System',
        epilog=f'Version {__version__} | Author: {__author__}'
    )
    
    # 全局参数
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--api-key', type=str, help='Semantic Scholar API Key（优先于环境变量）')
    parser.add_argument('--concurrency', type=int, default=5, help='最大并发下载数 (1-50)')
    parser.add_argument('--timeout', type=int, default=120, help='下载超时时间（秒）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--debug', action='store_true', help='调试模式（更详细的输出）')
    parser.add_argument('--config', type=str, help='配置文件路径（JSON格式）')
    parser.add_argument('--no-api', action='store_true', help='不使用API（离线模式）')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # GUI命令
    gui_parser = subparsers.add_parser('gui', help='启动图形界面')
    
    # 健康检查命令
    health_parser = subparsers.add_parser('health', help='检查系统健康状态')
    
    # 扩展命令
    expand_parser = subparsers.add_parser('expand', help='文献追踪扩展')
    expand_parser.add_argument('--seed', nargs='+', help='起始paperId, DOI, arXiv等')
    expand_parser.add_argument('--seed-bib', help='起始BibTeX文件，自动批量提取seed')
    expand_parser.add_argument('--depth', type=int, default=1, help='递归深度 (1-3)')
    expand_parser.add_argument('--csv', help='保存为CSV文件')
    expand_parser.add_argument('--json', help='保存为JSON文件')
    expand_parser.add_argument('--bib', help='保存为BibTeX文件')
    expand_parser.add_argument('--no-ref', action='store_true', help='不扩展引用')
    expand_parser.add_argument('--no-cite', action='store_true', help='不扩展被引')
    expand_parser.add_argument('--no-recommend', action='store_true', help='不扩展推荐')
    expand_parser.add_argument('--author', action='store_true', help='扩展作者论文')
    expand_parser.add_argument('--limit', type=int, default=30, help='每个接口最多获取数')
    expand_parser.add_argument('--resume', action='store_true', help='从上次中断处恢复')
    
    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索论文')
    search_parser.add_argument('query', help='搜索查询')
    search_parser.add_argument('--output', default='./research', help='输出目录')
    search_parser.add_argument('--no-download', action='store_true', help='不下载PDF')
    search_parser.add_argument('--limit', type=int, default=20, help='最大结果数')
    search_parser.add_argument('--year', type=int, help='限定年份')
    
    # 多数据库搜索命令
    multi_search_parser = subparsers.add_parser('multi-search', help='多数据库搜索')
    multi_search_parser.add_argument('query', help='搜索查询')
    multi_search_parser.add_argument('--output', default='./research_multi', help='输出目录')
    multi_search_parser.add_argument('--no-download', action='store_true', help='不下载PDF')
    multi_search_parser.add_argument('--sources', nargs='+', 
                                    choices=['semantic_scholar', 'pubmed', 'crossref', 'openalex', 'arxiv'],
                                    help='要搜索的数据库')
    multi_search_parser.add_argument('--limit', type=int, default=20, help='每个数据库最大结果数')
    multi_search_parser.add_argument('--parallel', action='store_true', help='并行搜索所有数据库')
    
    # PMC全文下载命令
    pmc_parser = subparsers.add_parser('pmc', help='PMC全文下载')
    pmc_parser.add_argument('pmcid', help='PMC ID (可带或不带PMC前缀)')
    pmc_parser.add_argument('--output', default='./pmc_output', help='输出目录')
    pmc_parser.add_argument('--extract-text', action='store_true', help='提取文本')
    pmc_parser.add_argument('--format', choices=['pdf', 'xml', 'txt', 'all'], default='all', 
                           help='输出格式')
    
    # 批量处理命令
    batch_parser = subparsers.add_parser('batch', help='批量处理（从文件读取查询）')
    batch_parser.add_argument('input_file', help='输入文件（每行一个查询或JSON格式）')
    batch_parser.add_argument('--output', default='./batch_output', help='输出目录')
    batch_parser.add_argument('--format', choices=['txt', 'json'], default='txt', help='输入文件格式')
    
    # Skills命令
    skills_parser = subparsers.add_parser('skill', help='直接调用AI技能')
    skills_parser.add_argument('--list', action='store_true', help='列出所有可用技能')
    skills_parser.add_argument('--info', help='显示特定技能的详细信息')
    skills_parser.add_argument('name', nargs='?', default=None, help='技能名称')
    skills_parser.add_argument('args_json', nargs='?', default='{}', help='技能参数（JSON字符串）')
    
    # 导出命令
    export_parser = subparsers.add_parser('export', help='导出论文数据')
    export_parser.add_argument('input', help='输入文件（JSON、CSV或BibTeX）')
    export_parser.add_argument('--format', choices=['csv', 'json', 'bib', 'ris'], required=True, 
                              help='输出格式')
    export_parser.add_argument('--output', required=True, help='输出文件路径')
    
    # 增强BibTeX命令
    enhance_parser = subparsers.add_parser('enhance', help='增强BibTeX：元数据补全+PDF下载')
    enhance_parser.add_argument('bibtex_file', help='输入BibTeX文件 (.bib)')
    enhance_parser.add_argument('--output', '-o', default='./enhanced', help='输出目录')
    enhance_parser.add_argument('--output-bib', help='输出增强BibTeX文件路径（默认: {output}/enhanced.bib）')
    enhance_parser.add_argument('--no-download', action='store_true', help='不下载PDF')
    enhance_parser.add_argument('--limit', type=int, default=0, 
                                help='最多处理前N条（0=全部）')
    
    return parser.parse_args()


async def batch_process(args, manager: ResearchPaperManager, config: Config):
    """批量处理多个查询"""
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file {args.input_file} not found")
        return
    
    # 读取查询
    queries = []
    if args.format == 'json':
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                queries = data
            elif isinstance(data, dict) and 'queries' in data:
                queries = data['queries']
            else:
                queries = [data]
    else:  # txt格式
        with open(input_path, 'r', encoding='utf-8') as f:
            queries = [line.strip() for line in f if line.strip()]
    
    print(f"Processing {len(queries)} queries...")
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Processing: {query}")
        try:
            result = await manager.search_and_download(
                query,
                str(output_dir / f"query_{i}"),
                download_pdfs=not args.no_download if hasattr(args, 'no_download') else True
            )
            results.append({
                'query': query,
                'success': True,
                'total_count': result.total_count if hasattr(result, 'total_count') else 0,
                'output_dir': str(result.output_dir) if hasattr(result, 'output_dir') else str(output_dir)
            })
        except Exception as e:
            logger.error(f"Failed to process query '{query}': {e}")
            results.append({
                'query': query,
                'success': False,
                'error': str(e)
            })
    
    # 保存批处理报告
    report_path = output_dir / 'batch_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_queries': len(queries),
            'successful': sum(1 for r in results if r.get('success')),
            'failed': sum(1 for r in results if not r.get('success')),
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nBatch processing complete. Report saved to {report_path}")


async def export_data(args):
    """导出论文数据为不同格式"""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file {args.input} not found")
        return
    
    # 读取数据
    data = []
    if input_path.suffix == '.json':
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'papers' in data:
                data = data['papers']
            elif not isinstance(data, list):
                data = [data]
    elif input_path.suffix == '.csv':
        if not PANDAS_AVAILABLE:
            print("Error: pandas required for CSV import. Install with: pip install pandas")
            return
        try:
            df = pd.read_csv(input_path)
            data = df.to_dict('records')
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return
    elif input_path.suffix in ['.bib', '.bibtex']:
        print("BibTeX import not yet implemented")
        return
    else:
        print(f"Unsupported input format: {input_path.suffix}")
        return
    
    if not data:
        print("No data to export")
        return
    
    # 导出为目标格式
    output_path = Path(args.output)
    if args.format == 'json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    elif args.format == 'csv':
        if not PANDAS_AVAILABLE:
            print("Error: pandas required for CSV export. Install with: pip install pandas")
            return
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding='utf-8')
    elif args.format == 'ris':
        # 实现RIS格式导出
        with open(output_path, 'w', encoding='utf-8') as f:
            for paper in data:
                f.write("TY  - JOUR\n")
                if 'title' in paper:
                    f.write(f"TI  - {paper['title']}\n")
                if 'authors' in paper:
                    authors = paper['authors'] if isinstance(paper['authors'], list) else [paper['authors']]
                    for author in authors:
                        f.write(f"AU  - {author}\n")
                if 'year' in paper:
                    f.write(f"PY  - {paper['year']}\n")
                if 'doi' in paper:
                    f.write(f"DO  - {paper['doi']}\n")
                f.write("ER  - \n\n")
    elif args.format == 'bib':
        print("BibTeX export not yet implemented")
        return
    
    print(f"Exported {len(data)} papers to {output_path}")


async def main_async(args):
    """异步主函数（增强版）"""
    
    # 设置日志
    logger = setup_logging(verbose=args.verbose, debug=args.debug)
    
    # 加载环境变量
    load_environment()
    
    # 设置API密钥
    if getattr(args, 'api_key', None):
        if validate_api_key(args.api_key):
            os.environ['SEMANTIC_SCHOLAR_API_KEY'] = args.api_key
            logger.info("API key set from command line")
        else:
            logger.error("Invalid API key format")
            return
    
    # 加载配置文件
    config = Config()
    if getattr(args, 'config', None) and Path(args.config).exists():
        try:
            with open(args.config, 'r') as f:
                config_data = json.load(f)
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
            logger.info(f"Loaded configuration from {args.config}")
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
    
    # 应用命令行参数覆盖
    config.max_concurrent_downloads = min(max(getattr(args, 'concurrency', 5), 1), 50)
    config.download_timeout = getattr(args, 'timeout', 120)
    
    # 验证配置
    try:
        validate_config(config)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    
    # 创建客户端和管理器
    try:
        api_client = SemanticScholarClient(config) if not getattr(args, 'no_api', False) else None
        downloader = PDFDownloader(config)
        converter = BibTexConverter()
        manager = ResearchPaperManager(api_client, downloader, converter, config)
        expansion_service = PaperExpansionService(api_client) if api_client else None
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        if "403" in str(e) or "Forbidden" in str(e):
            print("\n" + "="*60)
            print("API Access Error (403 Forbidden)")
            print("="*60)
            print("\nPossible solutions:")
            print("1. Get a free API key from: https://www.semanticscholar.org/product/api")
            print("2. Set the API key: export SEMANTIC_SCHOLAR_API_KEY='your_key_here'")
            print("3. Or use command line: --api-key YOUR_KEY")
            print("4. Or run in offline mode: --no-api")
            print("\nNote: Semantic Scholar API has changed. You may need to:")
            print("- Use a different API endpoint")
            print("- Check the official documentation for updates")
            print("="*60)
        return
    
    # 添加速率限制器（如果API客户端存在）
    if api_client:
        rate_limiter = RateLimiter(requests_per_second=5)
        api_client.rate_limiter = rate_limiter
    
    # 添加恢复管理器
    resume_manager = DownloadResumeManager()
    
    # 健康检查
    if args.command == 'health':
        if api_client:
            health_status = await health_check(api_client)
            print(json.dumps(health_status, indent=2, ensure_ascii=False))
            if health_status['api_client'] != 'OK':
                sys.exit(1)
        else:
            print(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'version': __version__,
                'api_client': 'Disabled (offline mode)',
                'dependencies': {
                    'pandas': 'Available' if PANDAS_AVAILABLE else 'Not installed',
                    'python-dotenv': 'Available' if DOTENV_AVAILABLE else 'Not installed'
                }
            }, indent=2, ensure_ascii=False))
        return
    
    # 导出命令
    if args.command == 'export':
        await export_data(args)
        return
    
    # 增强BibTeX命令
    if args.command == 'enhance':
        if not os.path.exists(args.bibtex_file):
            print(f"Error: BibTeX file not found: {args.bibtex_file}")
            return
        
        output_dir = args.output
        os.makedirs(output_dir, exist_ok=True)
        
        download_pdfs = not args.no_download
        
        print(f"📖 Enhancing BibTeX: {args.bibtex_file}")
        print(f"📂 Output dir: {output_dir}")
        print(f"⬇️  Download PDFs: {'YES' if download_pdfs else 'NO'}")
        
        try:
            # 如果指定了limit，截断BibTeX文件
            if args.limit and args.limit > 0:
                entries = manager.converter.parse_bibtex_file_for_enhancement(args.bibtex_file)
                if len(entries) > args.limit:
                    print(f"  Limiting to first {args.limit} of {len(entries)} entries")
                    # Create temp .bib with only the first N entries
                    temp_bib = os.path.join(output_dir, '_limit_temp.bib')
                    manager.converter.save_enhanced_bibtex(entries[:args.limit], temp_bib)
                    effective_bib = temp_bib
                else:
                    effective_bib = args.bibtex_file
            else:
                effective_bib = args.bibtex_file
            
            success, total, out_path = await manager.download_and_enhance_bibtex(
                effective_bib,
                output_dir,
                enhanced_bibtex_file=args.output_bib,
                download_pdfs=download_pdfs,
            )
            
            # 如果用了limit模式但没指定输出，先重命名再清理
            if args.limit and args.limit > 0 and not args.output_bib:
                default_out = os.path.join(output_dir, 'enhanced.bib')
                if os.path.exists(default_out):
                    os.remove(default_out)
                os.rename(out_path, default_out)
                out_path = default_out
            
            # 清理临时文件
            temp_paths = [
                os.path.join(output_dir, '_limit_temp.bib'),
                os.path.join(output_dir, '_limit_temp_enhanced.bib'),
            ]
            for p in temp_paths:
                if os.path.exists(p):
                    os.remove(p)
            
            print(f"\n✅ Enhanced {total} entries, downloaded {success} PDFs")
            print(f"📄 Enhanced BibTeX: {out_path}")
        except Exception as e:
            logger.error(f"Enhance failed: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            print(f"❌ Error: {e}")
        return
    
    # 批处理命令
    if args.command == 'batch':
        if not api_client and not getattr(args, 'no_api', False):
            print("Error: Batch processing requires API access. Use --no-api to disable API (limited functionality)")
            return
        await batch_process(args, manager, config)
        return
    
    # Skills命令
    if args.command == 'skill':
        if getattr(args, 'list', False):
            skills = skill_registry.list_skills()
            print(json.dumps(skills, indent=2, ensure_ascii=False))
            return
        
        if getattr(args, 'info', None):
            skill_info = skill_registry.get_skill_info(args.info)
            if skill_info:
                print(json.dumps(skill_info, indent=2, ensure_ascii=False))
            else:
                print(f"Skill '{args.info}' not found")
            return

        skill_name = args.name
        if not skill_name:
            print("Please specify a skill name or use --list")
            return
            
        try:
            kwargs = json.loads(args.args_json) if args.args_json else {}
        except json.JSONDecodeError as exc:
            print(f"Error: Invalid JSON arguments: {exc}")
            return

        result = skill_registry.invoke(skill_name, **kwargs)

        # 打印结果
        if hasattr(result, 'model_dump'):
            import pprint
            pprint.pprint(result.model_dump())
        elif isinstance(result, dict):
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            print(result)
        return
    
    # 扩展命令
    if args.command == 'expand':
        if not api_client:
            print("Error: Paper expansion requires API access. Remove --no-api or get an API key.")
            return
        
        seeds = args.seed if args.seed else []
        if getattr(args, 'seed_bib', None):
            seeds += extract_seeds_from_bibtex(args.seed_bib)
        
        if not seeds:
            print("请提供 --seed 或 --seed-bib")
            return
        
        seeds = [normalize_paper_id(s) for s in seeds]
        
        # 恢复未完成的任务
        if args.resume:
            pending = resume_manager.get_pending_downloads()
            if pending:
                print(f"Resuming {len(pending)} pending downloads")
                seeds.extend(pending)
        
        print(f"Starting literature expansion... (共{len(seeds)}个seed)")
        
        from src.core.config import ExpansionOptions
        options = ExpansionOptions()
        options.depth = min(max(args.depth, 1), 3)  # 限制深度1-3
        options.expand_references = not args.no_ref
        options.expand_citations = not args.no_cite
        options.expand_recommend = not args.no_recommend
        options.expand_authors = args.author
        options.limit_per_query = min(args.limit, 100)  # 限制最大100
        
        with ProgressTracker(len(seeds), "Expanding papers") as tracker:
            result = await expansion_service.expand_papers(seeds, options)
            tracker.update(len(seeds), f"Found {len(result.expanded_papers)} papers")
        
        print(f"Total papers expanded: {len(result.expanded_papers)}")
        
        # 保存结果
        if args.csv:
            if not PANDAS_AVAILABLE:
                print("Warning: pandas not installed. CSV export disabled.")
            else:
                papers_data = [paper.__dict__ for paper in result.expanded_papers]
                df = pd.DataFrame(papers_data)
                df.to_csv(args.csv, index=False, encoding='utf-8')
                print(f"Saved to {args.csv}")
        
        if args.json:
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump([paper.__dict__ for paper in result.expanded_papers], 
                         f, indent=2, ensure_ascii=False, default=str)
            print(f"Saved to {args.json}")
        
        if args.bib:
            bib_entries = []
            for paper in result.expanded_papers:
                try:
                    bib_entry = converter.paper_to_bibtex(paper)
                    bib_entries.append(bib_entry)
                except Exception as e:
                    logger.warning(f"Failed to convert paper {paper.id}: {e}")
            
            if bib_entries:
                with open(args.bib, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(bib_entries))
                print(f"Saved {len(bib_entries)} BibTeX entries to {args.bib}")
        
        # 保存状态以供恢复
        resume_manager.save_state('expansion_complete', 'completed', 
                                 metadata={'total_papers': len(result.expanded_papers)})
    
    # 搜索命令
    elif args.command == 'search':
        if not api_client and not getattr(args, 'no_api', False):
            print("Error: Search requires API access. Use --no-api to disable API (limited functionality)")
            return
        
        print(f"Searching for: {args.query}")
        download_pdfs = not args.no_download
        
        # 添加年份过滤
        if hasattr(args, 'year') and args.year:
            args.query = f"{args.query} year:{args.year}"
        
        try:
            with ProgressTracker(1, "Searching") as tracker:
                result = await manager.search_and_download(
                    args.query, 
                    args.output, 
                    download_pdfs,
                    max_results=getattr(args, 'limit', 20)
                )
                tracker.update(1, f"Found {result.total_count if hasattr(result, 'total_count') else 0} papers")
            
            if hasattr(result, 'output_dir') and result.output_dir:
                print(f"Results saved to: {result.output_dir}")
            else:
                print("Search completed but no results were saved.")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Search failed: {error_msg}")
            
            if "403" in error_msg or "Forbidden" in error_msg:
                print("\n" + "="*60)
                print("API Access Denied (403 Forbidden)")
                print("="*60)
                print("\nThe Semantic Scholar API requires authentication.")
                print("\nTo fix this issue:")
                print("1. Get a free API key from: https://www.semanticscholar.org/product/api")
                print("2. Set environment variable: export SEMANTIC_SCHOLAR_API_KEY='your_key'")
                print("3. Or use command line: --api-key YOUR_KEY")
                print("\nAlternatively, use other databases with --multi-search")
                print("="*60)
            else:
                print(f"Search error: {error_msg}")
            
            # 不要退出，让GUI可以继续运行
            if not hasattr(args, 'gui_mode'):
                sys.exit(1)

    # 多数据库搜索
    elif args.command == 'multi-search':
        # 多数据库搜索不需要Semantic Scholar API key
        print(f"Multi-database searching for: {args.query}")
        download_pdfs = not args.no_download
        
        sources = getattr(args, 'sources', None)
        limit_per_source = min(getattr(args, 'limit', 20), 50)
        
        print(f"Searching sources: {sources or 'all available'}")
        
        try:
            with ProgressTracker(1, "Multi-search") as tracker:
                result = await manager.multi_database_search(
                    args.query,
                    sources,
                    limit_per_source,
                    download_pdfs,
                    args.output,
                    parallel=getattr(args, 'parallel', False)
                )
                tracker.update(1, f"Found {result.get('total_papers', 0)} papers")
            
            # 显示统计信息
            if 'statistics' in result:
                print("\nSearch Statistics:")
                print(json.dumps(result['statistics'], indent=2))
            
            print(f"Results saved to: {args.output}")
        except Exception as e:
            logger.error(f"Multi-search failed: {e}")
            print(f"Multi-search error: {e}")

    # PMC全文下载
    elif args.command == 'pmc':
        pmcid = args.pmcid.replace('PMC', '').strip()
        print(f"Downloading PMC full-text for: {pmcid}")
        
        pmc_downloader = PMCFullTextDownloader(config)
        output_dir = sanitize_path(args.output)
        
        try:
            result = await pmc_downloader.download_and_extract(
                pmcid,
                output_dir,
                filename=None
            )
            
            print(f"\nPMC {pmcid} download completed:")
            if result.get('pdf_path') and args.format in ['pdf', 'all']:
                print(f"  PDF: {result['pdf_path']}")
            if result.get('xml_path') and args.format in ['xml', 'all']:
                print(f"  XML: {result['xml_path']}")
            if result.get('text_path') and args.format in ['txt', 'all']:
                print(f"  Text: {result['text_path']}")
                print(f"  Text length: {len(result.get('text', ''))} characters")
            
            # 保存元数据
            metadata_path = Path(output_dir) / f"PMC{pmcid}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            print(f"  Metadata: {metadata_path}")
            
        except Exception as e:
            logger.error(f"PMC download failed: {e}")
            print(f"Error: {e}")
            sys.exit(1)


def signal_handler(signum, frame):
    """处理中断信号"""
    print("\n\n⚠️  Interrupted by user. Cleaning up...")
    logger.info("Process interrupted by user")
    sys.exit(0)


def main():
    """主函数（增强版）"""
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    args = parse_args()
    
    # 如果没有命令，默认启动GUI
    if not args.command:
        args.command = 'gui'
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    # 显示警告信息关于API变化
    if not getattr(args, 'no_api', False) and args.command != 'gui':
        print("⚠️  Note: Semantic Scholar API may require authentication")
        print("   Get a free API key at: https://www.semanticscholar.org/product/api")
        print("   Or use --multi-search for alternative databases\n")
    
    if args.command == 'gui':
        # 启动GUI
        concurrency = min(max(getattr(args, 'concurrency', 5), 1), 50)
        timeout = getattr(args, 'timeout', 120)
        
        print(f"""
╔══════════════════════════════════════════════════════════╗
║     Research Paper Manager v{__version__}                         ║
║     Comprehensive Academic Paper Management System      ║
╚══════════════════════════════════════════════════════════╝
        """)
        print(f"🚀 Starting GUI...")
        print(f"⚙️  Configuration: Concurrency={concurrency}, Timeout={timeout}s")
        print("💡 Tip: If you see API errors, use Multi-Database Search instead\n")
        
        try:
            # 设置GUI模式标志
            args.gui_mode = True
            app = ResearchGUI(
                max_concurrent_downloads=concurrency,
                download_timeout=timeout
            )
            app.mainloop()
        except TypeError as e:
            # 如果还是失败，尝试不传递任何参数
            logger.warning(f"Failed to pass parameters to GUI: {e}")
            print("⚠️  Trying to start GUI with default settings...")
            try:
                app = ResearchGUI()
                app.mainloop()
            except Exception as e2:
                logger.error(f"GUI failed to start: {e2}")
                print(f"❌ Error starting GUI: {e2}")
                print("\nTroubleshooting:")
                print("1. Check if all dependencies are installed: pip install -r requirements.txt")
                print("2. Try running without GUI: python main.py --help")
                print("3. Check for missing UI components in src/ui/")
                sys.exit(1)
        except Exception as e:
            logger.error(f"GUI failed to start: {e}")
            print(f"❌ Error starting GUI: {e}")
            print("\nTroubleshooting:")
            print("1. Check if tkinter is installed: sudo apt-get install python3-tk")
            print("2. Try running without GUI: python main.py --help")
            sys.exit(1)
    else:
        # 执行命令行操作
        try:
            asyncio.run(main_async(args))
        except KeyboardInterrupt:
            print("\n⚠️  Operation cancelled by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if args.debug:
                traceback.print_exc()
            print(f"❌ Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
