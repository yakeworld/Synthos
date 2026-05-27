import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import gc
import logging
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from src.core.config import Config
from src.manager.paper_manager import ResearchPaperManager
from src.api.semantic_scholar import SemanticScholarClient
from src.downloader.pdf_downloader import PDFDownloader
from src.converter.bibtex_converter import BibTexConverter
from src.manager.expansion_service import PaperExpansionService
from src.utils.paper_id import extract_seeds_from_bibtex
from .event_handlers import EventHandlers

logger = logging.getLogger(__name__)

class ResearchGUI(tk.Tk):
    """研究论文管理器GUI"""
    
    def __init__(self, max_concurrent_downloads=5, download_timeout=120):
        super().__init__()
        self.title("Research Paper Manager")
        self.geometry("780x600")
        self.configure(padx=20, pady=20)
        
        self.max_concurrent_downloads = max_concurrent_downloads
        self.download_timeout = download_timeout
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.is_running = False

        self._setup_manager()
        self._setup_event_handlers()
        self._setup_components()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _setup_components(self):
        """设置UI组件"""
        # 创建标签页
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 搜索面板
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Search Papers")
        self._setup_search_frame()
        
        # BibTeX下载和增强面板
        self.combined_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.combined_frame, text="BibTeX Download & Enhance")
        self._setup_combined_frame()
        
        # 文献扩展面板
        self.expand_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.expand_frame, text="文献扩展")
        self._setup_expand_frame()
        
        # 状态栏
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(fill=tk.X, pady=10)
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        self.progress = ttk.Progressbar(self.status_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    
    def _setup_manager(self):
        """设置管理器"""
        config = Config()
        config.max_concurrent_downloads = self.max_concurrent_downloads
        config.download_timeout = self.download_timeout
        
        api_client = SemanticScholarClient(config)
        downloader = PDFDownloader(config)
        converter = BibTexConverter()
        
        self.manager = ResearchPaperManager(api_client, downloader, converter, config)
        self.expansion_service = PaperExpansionService(api_client)
    
    def _setup_event_handlers(self):
        self.event_handlers = EventHandlers(self)
    
    def _setup_search_frame(self):
        """设置搜索面板"""
        # 搜索查询
        query_frame = ttk.LabelFrame(self.search_frame, text="Search Query")
        query_frame.pack(fill=tk.X, pady=10)
        ttk.Label(query_frame, text="Enter query:").pack(pady=5)
        self.query_entry = ttk.Entry(query_frame, width=50)
        self.query_entry.pack(pady=5, padx=10, fill=tk.X)
        
        # 输出目录
        out_dir_frame = ttk.LabelFrame(self.search_frame, text="Output Directory")
        out_dir_frame.pack(fill=tk.X, pady=10)
        dir_frame = ttk.Frame(out_dir_frame)
        dir_frame.pack(fill=tk.X, pady=5, padx=10)
        self.dir_entry = ttk.Entry(dir_frame)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.dir_entry.insert(0, os.path.join(os.getcwd(), "research"))
        browse_button = ttk.Button(dir_frame, text="Browse", command=lambda: self.choose_directory(self.dir_entry))
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # 选项
        options_frame = ttk.LabelFrame(self.search_frame, text="Options")
        options_frame.pack(fill=tk.X, pady=10)
        self.search_option = tk.StringVar(value="search_and_download")
        ttk.Radiobutton(options_frame, text="Search only", variable=self.search_option, value="search_only").pack(pady=5, padx=10, anchor=tk.W)
        ttk.Radiobutton(options_frame, text="Search and download PDFs", variable=self.search_option, value="search_and_download").pack(pady=5, padx=10, anchor=tk.W)
        
        # 按钮
        button_frame = ttk.Frame(self.search_frame)
        button_frame.pack(fill=tk.X, pady=20)
        self.search_button = ttk.Button(button_frame, text="Start", command=self.event_handlers.start_search)
        self.search_button.pack(pady=10)
    
    def _setup_combined_frame(self):
        """设置BibTeX下载和增强面板"""
        # 输入BibTeX文件
        bibtex_frame = ttk.LabelFrame(self.combined_frame, text="Input BibTeX File")
        bibtex_frame.pack(fill=tk.X, pady=10)
        bib_file_frame = ttk.Frame(bibtex_frame)
        bib_file_frame.pack(fill=tk.X, pady=5, padx=10)
        self.combined_bibtex_entry = ttk.Entry(bib_file_frame)
        self.combined_bibtex_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        browse_button = ttk.Button(bib_file_frame, text="Select File",
                                  command=lambda: self.choose_file(self.combined_bibtex_entry, title="Select BibTeX File", filetypes=[("BibTeX files", "*.bib"), ("All files", "*.*")]))
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # 输出目录
        out_dir_frame = ttk.LabelFrame(self.combined_frame, text="Output Directory")
        out_dir_frame.pack(fill=tk.X, pady=10)
        bib_dir_frame = ttk.Frame(out_dir_frame)
        bib_dir_frame.pack(fill=tk.X, pady=5, padx=10)
        self.combined_dir_entry = ttk.Entry(bib_dir_frame)
        self.combined_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.combined_dir_entry.insert(0, os.path.join(os.getcwd(), "enhanced_bibtex"))
        browse_button = ttk.Button(bib_dir_frame, text="Browse", command=lambda: self.choose_directory(self.combined_dir_entry))
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # 增强的BibTeX输出文件
        enhanced_frame = ttk.LabelFrame(self.combined_frame, text="Enhanced BibTeX Output File")
        enhanced_frame.pack(fill=tk.X, pady=10)
        enhanced_file_frame = ttk.Frame(enhanced_frame)
        enhanced_file_frame.pack(fill=tk.X, pady=5, padx=10)
        self.enhanced_bibtex_entry = ttk.Entry(enhanced_file_frame)
        self.enhanced_bibtex_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        browse_button = ttk.Button(enhanced_file_frame, text="Select File",
                                  command=lambda: self.choose_file(self.enhanced_bibtex_entry, title="Select Output BibTeX File", filetypes=[("BibTeX files", "*.bib"), ("All files", "*.*")]))
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # 按钮
        button_frame = ttk.Frame(self.combined_frame)
        button_frame.pack(fill=tk.X, pady=20)
        self.combined_button = ttk.Button(button_frame, text="Download & Enhance", command=self.event_handlers.start_combined_operation)
        self.combined_button.pack(pady=10)
    
    def _setup_expand_frame(self):
        """设置文献扩展面板"""
        # 起始文献
        seed_frame = ttk.LabelFrame(self.expand_frame, text="起始文献 paperId (每行一个或逗号分隔)")
        seed_frame.pack(fill=tk.X, pady=10)
        self.expand_seed_text = tk.Text(seed_frame, height=4)
        self.expand_seed_text.pack(fill=tk.X, padx=10, pady=5)
        
        # BibTeX文件选择
        self.expand_bibfile_var = tk.StringVar()
        ttk.Label(self.expand_frame, text="或选择BibTeX文件：").pack(anchor=tk.W, pady=4, padx=5)
        bibfile_frame = ttk.Frame(self.expand_frame)
        bibfile_frame.pack(fill=tk.X, padx=10)
        self.expand_bibfile_entry = ttk.Entry(bibfile_frame, textvariable=self.expand_bibfile_var, width=60)
        self.expand_bibfile_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(bibfile_frame, text="选择文件", command=lambda: self.choose_file(self.expand_bibfile_entry, title="选择BibTeX文件", filetypes=[("BibTeX files", "*.bib")])).pack(side=tk.RIGHT, padx=5)
        
        # 扩展选项
        options_frame = ttk.LabelFrame(self.expand_frame, text="扩展选项")
        options_frame.pack(fill=tk.X, pady=10)
        self.expand_depth_var = tk.IntVar(value=1)
        ttk.Label(options_frame, text="递归深度:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(options_frame, from_=1, to=5, width=5, textvariable=self.expand_depth_var).pack(side=tk.LEFT, padx=5)
        self.expand_ref_var = tk.BooleanVar(value=True)
        self.expand_cite_var = tk.BooleanVar(value=True)
        self.expand_recommend_var = tk.BooleanVar(value=True)
        self.expand_author_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="扩展引用", variable=self.expand_ref_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="扩展被引", variable=self.expand_cite_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="扩展推荐", variable=self.expand_recommend_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="扩展作者论文", variable=self.expand_author_var).pack(side=tk.LEFT, padx=5)
        
        # 输出文件
        output_frame = ttk.LabelFrame(self.expand_frame, text="输出文件")
        output_frame.pack(fill=tk.X, pady=10)
        ttk.Label(output_frame, text="CSV文件:").pack(side=tk.LEFT, padx=5)
        self.expand_csv_entry = ttk.Entry(output_frame, width=40)
        self.expand_csv_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(output_frame, text="BibTeX文件:").pack(side=tk.LEFT, padx=5)
        self.expand_bib_entry = ttk.Entry(output_frame, width=40)
        self.expand_bib_entry.pack(side=tk.LEFT, padx=5)
        
        # 按钮
        button_frame = ttk.Frame(self.expand_frame)
        button_frame.pack(fill=tk.X, pady=20)
        self.expand_button = ttk.Button(button_frame, text="开始扩展", command=self.event_handlers.start_expand)
        self.expand_button.pack(pady=10)
    
    def choose_directory(self, entry_widget):
        """选择目录"""
        directory = filedialog.askdirectory()
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)
    
    def choose_file(self, entry_widget, title="Open File", filetypes=(("All files", "*.*"),)):
        """选择文件"""
        filename = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
            if entry_widget == self.combined_bibtex_entry:
                base_name = os.path.splitext(os.path.basename(filename))[0]
                output_dir = self.combined_dir_entry.get()
                enhanced_file = os.path.join(output_dir, f"{base_name}_enhanced.bib")
                self.enhanced_bibtex_entry.delete(0, tk.END)
                self.enhanced_bibtex_entry.insert(0, enhanced_file)
    
    def update_progress(self, current, total, message="Processing"):
        """更新进度"""
        def update():
            self.progress["maximum"] = total
            self.progress["value"] = current + 1
            self.status_label.config(text=f"{message}... {current + 1}/{total}")
        self.after(0, update)
    
    def on_closing(self):
        """关闭窗口事件"""
        if self.is_running:
            if not messagebox.askokcancel("Quit", "An operation is in progress. Quitting now may cause data loss. Continue?"):
                return
        self.executor.shutdown(wait=False)
        self.destroy()