import os
import asyncio
import logging
import pandas as pd
from tkinter import messagebox
from threading import Thread

from src.core.config import ExpansionOptions
from src.utils.paper_id import normalize_paper_id
from src.utils.file_ops import save_papers_to_csv

logger = logging.getLogger(__name__)

class EventHandlers:
    """GUI事件处理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def start_search(self):
        """开始搜索"""
        query = self.main_window.query_entry.get()
        base_dir = self.main_window.dir_entry.get()
        download_pdfs = self.main_window.search_option.get() == "search_and_download"
        
        if not query:
            messagebox.showerror("Error", "Please enter a search query")
            return
        
        if not base_dir:
            messagebox.showerror("Error", "Please select an output directory")
            return
        
        self.main_window.search_button.config(state="disabled")
        self.main_window.progress["value"] = 0
        self.main_window.status_label.config(text="Searching...")
        self.main_window.update()
        self.main_window.is_running = True
        
        def run_search():
            query_dir = os.path.join(base_dir, query.replace(" ", "_").replace("/", "_"))
            try:
                result_dir = asyncio.run(
                    self.main_window.manager.search_and_download(
                        query, query_dir, download_pdfs, callback=self.main_window.update_progress
                    )
                )
                self.main_window.after(0, lambda: self.main_window.status_label.config(text="Complete"))
                self.main_window.after(0, lambda: messagebox.showinfo("Success", f"Operation complete!\nResults saved to: {result_dir}"))
            except Exception as e:
                logger.exception("Error during search operation")
                self.main_window.after(0, lambda: self.main_window.status_label.config(text="Error"))
                self.main_window.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            finally:
                self.main_window.after(0, lambda: self.main_window.search_button.config(state="normal"))
                self.main_window.is_running = False
                import gc
                gc.collect()
        
        self.main_window.executor.submit(run_search)
    
    def start_combined_operation(self):
        """开始BibTeX下载和增强操作"""
        bibtex_file = self.main_window.combined_bibtex_entry.get()
        output_dir = self.main_window.combined_dir_entry.get()
        enhanced_bibtex_file = self.main_window.enhanced_bibtex_entry.get()
        
        if not bibtex_file or not os.path.exists(bibtex_file):
            messagebox.showerror("Error", "Please select a valid BibTeX file")
            return
        
        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory")
            return
        
        if not enhanced_bibtex_file:
            base_name = os.path.splitext(os.path.basename(bibtex_file))[0]
            enhanced_bibtex_file = os.path.join(output_dir, f"{base_name}_enhanced.bib")
            self.main_window.enhanced_bibtex_entry.delete(0, tk.END)
            self.main_window.enhanced_bibtex_entry.insert(0, enhanced_bibtex_file)
        
        os.makedirs(output_dir, exist_ok=True)
        self.main_window.combined_button.config(state="disabled")
        self.main_window.progress["value"] = 0
        self.main_window.status_label.config(text="Starting process...")
        self.main_window.update()
        self.main_window.is_running = True
        
        def run_combined():
            try:
                success, total, enhanced_file = asyncio.run(
                    self.main_window.manager.download_and_enhance_bibtex(
                        bibtex_file, output_dir, enhanced_bibtex_file, callback=self.main_window.update_progress
                    )
                )
                self.main_window.after(0, lambda: self.main_window.status_label.config(text="Complete"))
                self.main_window.after(0, lambda: messagebox.showinfo("Success", 
                                   f"Operation complete!\n"
                                   f"Downloaded {success} of {total} PDFs\n"
                                   f"PDFs saved to: {os.path.join(output_dir, 'pdfs')}\n"
                                   f"Enhanced BibTeX saved to: {enhanced_file}"))
            except Exception as e:
                logger.exception("Error during combined operation")
                self.main_window.after(0, lambda: self.main_window.status_label.config(text="Error"))
                self.main_window.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            finally:
                self.main_window.after(0, lambda: self.main_window.combined_button.config(state="normal"))
                self.main_window.is_running = False
                import gc
                gc.collect()
        
        self.main_window.executor.submit(run_combined)
    
    def start_expand(self):
        """开始文献扩展"""
        raw = self.main_window.expand_seed_text.get("1.0", tk.END)
        seeds = []
        for line in raw.strip().splitlines():
            for part in line.strip().split(","):
                s = part.strip()
                if s: 
                    seeds.append(s)
        
        bibfile = self.main_window.expand_bibfile_var.get().strip()
        if bibfile:
            seeds += extract_seeds_from_bibtex(bibfile)
        
        if not seeds:
            messagebox.showerror("错误", "请至少输入一个paperId/DOI/arXiv，或选择一个BibTeX文件")
            return
        
        depth = self.main_window.expand_depth_var.get()
        expand_ref = self.main_window.expand_ref_var.get()
        expand_cite = self.main_window.expand_cite_var.get()
        expand_recommend = self.main_window.expand_recommend_var.get()
        expand_author = self.main_window.expand_author_var.get()
        csv_path = self.main_window.expand_csv_entry.get().strip()
        bib_path = self.main_window.expand_bib_entry.get().strip()
        
        if not csv_path and not bib_path:
            messagebox.showerror("错误", "请至少输入一个输出文件名")
            return
        
        self.main_window.expand_button.config(state="disabled")
        self.main_window.progress["value"] = 0
        self.main_window.status_label.config(text="正在扩展文献...")
        self.main_window.update()
        self.main_window.is_running = True
        
        def run_expand():
            try:
                # 创建扩展选项
                options = ExpansionOptions()
                options.depth = depth
                options.expand_references = expand_ref
                options.expand_citations = expand_cite
                options.expand_recommend = expand_recommend
                options.expand_authors = expand_author
                options.limit_per_query = 30
                
                # 执行扩展
                result = asyncio.run(
                    self.main_window.expansion_service.expand_papers(
                        seeds, options, callback=self.main_window.update_progress
                    )
                )
                
                # 保存结果
                if csv_path:
                    papers_data = [paper.__dict__ for paper in result.expanded_papers]
                    save_papers_to_csv(papers_data, csv_path)
                
                if bib_path:
                    # 这里需要实现保存为BibTeX的逻辑
                    pass
                
                self.main_window.after(0, lambda: self.main_window.status_label.config(text=f"扩展完成，共{len(result.expanded_papers)}篇文献"))
                self.main_window.after(0, lambda: messagebox.showinfo("扩展完成", f"共扩展出{len(result.expanded_papers)}篇文献\n已保存到输出文件。"))
            
            except Exception as e:
                logger.exception("文献扩展时出错")
                self.main_window.after(0, lambda: self.main_window.status_label.config(text="扩展出错"))
                self.main_window.after(0, lambda: messagebox.showerror("扩展出错", f"错误：{str(e)}"))
            finally:
                self.main_window.after(0, lambda: self.main_window.expand_button.config(state="normal"))
                self.main_window.is_running = False
                import gc
                gc.collect()
        
        Thread(target=run_expand, daemon=True).start()