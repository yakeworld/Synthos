"""
Skills package — AI-callable skill wrappers for Research Paper Manager.

Each skill is a self-contained class with a clear input/output contract
designed for LLM function-calling integration.
"""

from src.skills.paper_search_skill import PaperSearchSkill
from src.skills.pdf_download_skill import PDFDownloadSkill
from src.skills.bibtex_convert_skill import BibTeXConvertSkill
from src.skills.literature_expand_skill import LiteratureExpandSkill
from src.skills.paper_workflow_skill import PaperWorkflowSkill
from src.skills.registry import SkillRegistry, skill_registry

__all__ = [
    "PaperSearchSkill",
    "PDFDownloadSkill",
    "BibTeXConvertSkill",
    "LiteratureExpandSkill",
    "PaperWorkflowSkill",
    "SkillRegistry",
    "skill_registry",
]
