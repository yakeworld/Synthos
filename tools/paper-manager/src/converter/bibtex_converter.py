import os
import re
import json
import ast
import logging
import pandas as pd
import numpy as np
import bibtexparser
from typing import List, Dict, Optional, Tuple, Any
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

from src.core.interfaces import IBibtexConverter
from src.utils.paper_id import get_relative_pdf_path
from src.utils.file_ops import ensure_directory_exists

logger = logging.getLogger(__name__)

class BibTexConverter(IBibtexConverter):
    """BibTeX转换器"""
    
    @staticmethod
    def _is_na(value):
        if value is None:
            return True
        if isinstance(value, (np.ndarray, list)):
            return len(value) == 0
        if isinstance(value, (np.integer, np.floating)):
            return np.isnan(value) if value.dtype.kind == 'f' else False
        try:
            return pd.isna(value)
        except Exception:
            return False

    @staticmethod
    def clean_text(text):
        if text is None:
            return ""
        if isinstance(text, (list, np.ndarray)):
            if len(text) == 0:
                return ""
            text = text[0]
        if BibTexConverter._is_na(text):
            return ""
        return re.sub(r'\s+', ' ', str(text)).strip()

    @staticmethod
    def format_authors(authors):
        if authors is None:
            return ""
        if isinstance(authors, (np.ndarray,)):
            if authors.size == 0:
                return ""
            authors = authors[0] if authors.size > 0 else ""
        if BibTexConverter._is_na(authors):
            return ""
        try:
            if isinstance(authors, str):
                author_list = ast.literal_eval(authors)
            else:
                author_list = authors

            if not isinstance(author_list, list):
                return str(authors)

            return ' and '.join([author.get('name', '') for author in author_list if 'name' in author])
        except (ValueError, SyntaxError):
            return str(authors) if authors else ""
        except Exception:
            return str(authors) if authors else ""

    @staticmethod
    def parse_journal(journal_str):
        if BibTexConverter._is_na(journal_str) or journal_str == "":
            return {'name': '', 'volume': '', 'pages': ''}
            return {'name': '', 'volume': '', 'pages': ''}
        try:
            if isinstance(journal_str, str):
                return ast.literal_eval(journal_str)
            return journal_str
        except (ValueError, SyntaxError):
            return {'name': journal_str, 'volume': '', 'pages': ''}
        except Exception:
            return {'name': journal_str, 'volume': '', 'pages': ''}
    
    @staticmethod
    def parse_external_ids(external_ids):
        """解析外部ID"""
        if pd.isna(external_ids) or external_ids == "":
            return {}
        try:
            if isinstance(external_ids, str):
                return ast.literal_eval(external_ids)
            return external_ids
        except (ValueError, SyntaxError):
            return {'DOI': external_ids} if isinstance(external_ids, str) else {}
        except Exception:
            return {'DOI': external_ids} if isinstance(external_ids, str) else {}
    
    @staticmethod
    def create_key(authors, year, title):
        """创建BibTeX键"""
        if authors:
            author_parts = authors.split(' and ')[0].split()
            first_author = author_parts[-1].lower() if author_parts else 'unknown'
        else:
            first_author = 'unknown'
        
        year = str(year) if year else 'unknown'
        
        if title:
            title_words = title.split()
            first_word = ''.join(filter(str.isalnum, title_words[0])).lower() if title_words else 'unknown'
        else:
            first_word = 'unknown'
        
        return f"{first_author}{year}{first_word}"
    
    @staticmethod
    def parse_json_field(field):
        """解析JSON字段"""
        if pd.isna(field) or field == "":
            return {}
        try:
            if isinstance(field, str):
                return json.loads(field.replace("'", "\""))
            return field
        except json.JSONDecodeError:
            try:
                if isinstance(field, str):
                    return ast.literal_eval(field)
                return field
            except (ValueError, SyntaxError):
                return field if isinstance(field, dict) else {}
            except Exception:
                return field if isinstance(field, dict) else {}
        except Exception:
            return field if isinstance(field, dict) else {}
    
    def create_bibtex_entry(self, row: Dict, pdf_dir: str = "", bib_dir: str = None) -> tuple:
        """创建BibTeX条目"""
        # bib_dir: BibTeX文件所在目录，用于生成相对路径
        entry_type = 'article'
        title = self.clean_text(row.get('title', ''))
        authors = self.format_authors(row.get('authors', ''))
        year = ''
        if 'year' in row and row['year'] is not None and not pd.isna(row['year']):
            try:
                year = int(float(row['year']))
            except (ValueError, TypeError):
                year = ''
        key = self.create_key(authors, year, title)
        journal_info = self.parse_journal(row.get('journal', ''))
        external_ids = self.parse_external_ids(row.get('externalIds', ''))
        citation_styles = self.parse_json_field(row.get('citationStyles', ''))
        publication_venue = self.parse_json_field(row.get('publicationVenue', ''))
        open_access_pdf = self.parse_json_field(row.get('openAccessPdf', ''))
        fields = []
        if title:
            fields.append(('title', title))
        if authors:
            fields.append(('author', authors))
        if year:
            fields.append(('year', year))
        journal_name = self.clean_text(journal_info.get('name', ''))
        if journal_name:
            fields.append(('journal', journal_name))
        journal_volume = self.clean_text(journal_info.get('volume', ''))
        if journal_volume:
            fields.append(('volume', journal_volume))
        journal_pages = self.clean_text(journal_info.get('pages', ''))
        if journal_pages:
            fields.append(('pages', journal_pages))
        abstract = self.clean_text(row.get('abstract', ''))
        if abstract:
            fields.append(('abstract', abstract))
        doi = external_ids.get('DOI', '')
        if doi:
            fields.append(('doi', doi))
        dblp = external_ids.get('DBLP', '')
        if dblp:
            fields.append(('dblp', dblp))
        mag = external_ids.get('MAG', '')
        if mag:
            fields.append(('mag', mag))
        arxiv_id = external_ids.get('arXiv', '')
        if arxiv_id:
            fields.append(('arxivId', arxiv_id))
        pdf_url = open_access_pdf.get('url', '')
        if pdf_url:
            fields.append(('openAccessPdf', pdf_url))
        corpus_id = external_ids.get('CorpusId', '')
        if corpus_id:
            fields.append(('corpusid', corpus_id))
        pubmed = external_ids.get('PubMed', '')
        if pubmed:
            fields.append(('pubmed', pubmed))
        ref_count = row.get('referenceCount')
        if ref_count is not None:
            fields.append(('referenceCount', ref_count))
        cite_count = row.get('citationCount')
        if cite_count is not None:
            fields.append(('citationCount', cite_count))
        if isinstance(publication_venue, dict):
            issn = self.clean_text(publication_venue.get('issn', ''))
            if issn:
                fields.append(('issn', issn))
            publisher = self.clean_text(publication_venue.get('name', ''))
            if publisher:
                fields.append(('publisher', publisher))
        
        pdf_path = ""
        if pdf_dir:
            if doi:
                pdf_path = os.path.join(pdf_dir, f'{doi.replace("/", "_").replace(".","-")}.pdf')
            if not doi or not os.path.exists(pdf_path):
                if arxiv_id:
                    arxiv_pdf_path = os.path.join(pdf_dir, f'arxiv_{arxiv_id}.pdf')
                    if os.path.exists(arxiv_pdf_path):
                        pdf_path = arxiv_pdf_path
            if not os.path.exists(pdf_path):
                key_pdf_path = os.path.join(pdf_dir, f'{key}.pdf')
                if os.path.exists(key_pdf_path):
                    pdf_path = key_pdf_path
        
        bibtex = f"@{entry_type}{{{key},\n"
        for field, value in fields:
            if field in ['referenceCount', 'citationCount', 'year']:
                bibtex += f"  {field} = {value},\n"
            else:
                bibtex += f"  {field} = {{{value}}},\n"
        
        if pdf_path and os.path.exists(pdf_path):
            if bib_dir is None:
                bib_dir = os.getcwd()
            rel_pdf_path = get_relative_pdf_path(pdf_path, bib_dir)
            bibtex += f"  file = {{:{rel_pdf_path}:PDF}},\n"
        
        bibtex = bibtex.rstrip(',\n') + "\n}"
        return key, bibtex
    
    def convert_csv_to_bib(self, csv_file: str, output_file: str, pdf_dir: str = "") -> str:
        """转换CSV到BibTeX"""
        try:
            df = pd.read_csv(csv_file)
            bibtex_entries = []
            output_dir = os.path.dirname(os.path.abspath(output_file))
            ensure_directory_exists(output_dir)
            for _, row in df.iterrows():
                try:
                    _, entry = self.create_bibtex_entry(row, pdf_dir, bib_dir=output_dir)
                    bibtex_entries.append(entry)
                except Exception as e:
                    logger.error(f"Error processing row: {row.get('title', 'Unknown title')}")
                    logger.error(f"Error message: {str(e)}")
            self.save_to_bib_file(bibtex_entries, output_file)
            logger.info(f"BibTeX entries have been saved to {output_file}")
            return output_file
        except pd.errors.EmptyDataError:
            logger.error(f"CSV file is empty: {csv_file}")
            raise ValueError(f"CSV file is empty: {csv_file}")
        except Exception as e:
            logger.exception(f"Error converting CSV to BibTeX:")
            raise
    
    def save_to_bib_file(self, entries: List[str], filename: str):
        """保存BibTeX条目到文件"""
        ensure_directory_exists(os.path.dirname(os.path.abspath(filename)))
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(entries))
    
    def parse_bibtex_file(self, bibtex_file: str) -> List[Dict]:
        """解析BibTeX文件"""
        try:
            with open(bibtex_file, 'r', encoding='utf-8') as bibtex_file:
                bib_database = bibtexparser.load(bibtex_file)
            
            papers = []
            for entry in bib_database.entries:
                paper = {
                    'key': entry.get('ID', ''),
                    'doi': entry.get('doi', ''),
                    'arxiv': entry.get('arxivid', entry.get('eprint', '')),
                    'title': entry.get('title', '')
                }
                papers.append(paper)
            
            return papers
        except FileNotFoundError:
            logger.error(f"BibTeX file not found: {bibtex_file}")
            return []
        except Exception as e:
            logger.error(f"Error parsing BibTeX file: {e}")
            return []
    
    def parse_bibtex_file_for_enhancement(self, file_path):
        """解析BibTeX文件用于增强"""
        try:
            with open(file_path, 'r', encoding='utf-8') as bibtex_file:
                bib_database = bibtexparser.load(bibtex_file)
            return bib_database.entries
        except FileNotFoundError:
            logger.error(f"BibTeX file not found: {file_path}")
            raise FileNotFoundError(f"BibTeX file not found: {file_path}")
        except Exception as e:
            logger.error(f"Error parsing BibTeX file: {e}")
            raise
    
    def save_enhanced_bibtex(self, entries, output_file):
        """保存增强的BibTeX条目"""
        try:
            for entry in entries:
                for k in list(entry.keys()):
                    if isinstance(entry[k], (dict, list)):
                        if k.lower() in {"externalids", "citationstyles", "publicationvenue", "openaccesspdf"}:
                            del entry[k]
                        else:
                            entry[k] = json.dumps(entry[k], ensure_ascii=False)
                    elif not isinstance(entry[k], str):
                        entry[k] = str(entry[k])
            
            ensure_directory_exists(os.path.dirname(os.path.abspath(output_file)))
            db = BibDatabase()
            db.entries = entries
            writer = BibTexWriter()
            with open(output_file, 'w', encoding='utf-8') as bibtex_file:
                bibtex_file.write(writer.write(db))
        except Exception as e:
            logger.error(f"Error saving enhanced BibTeX: {e}")
            raise