"""Paper Workflow Skill — End-to-end orchestration combining search, download, and citation.

Usage as LLM tool:
```json
{
    "name": "paper_workflow",
    "arguments": {
        "query": "graph neural networks for molecular property prediction",
        "year": "2020-2024",
        "download_pdfs": true,
        "output_dir": "./research/gnn",
        "generate_citations": true,
        "expand_depth": 1
    }
}
```
"""

import os
from dataclasses import dataclass, field
from typing import Any

from src.api.semantic_scholar import SemanticScholarClient
from src.downloader.pdf_downloader import PDFDownloader
from src.converter.bibtex_converter import BibTexConverter
from src.manager.expansion_service import PaperExpansionService
from src.core.config import Config


@dataclass
class WorkflowSummary:
    papers: list[dict[str, Any]] = field(default_factory=list)
    pdfs_downloaded: int = 0
    bibtex_entries: list[str] = field(default_factory=list)
    expanded_papers: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    csv_path: str = ""
    bib_path: str = ""


class PaperWorkflowSkill:
    """Orchestrate end-to-end academic paper research workflows as an AI skill.

    Combines search, PDF download, BibTeX generation, and literature expansion
    into composable pipeline steps. Each step can be skipped via boolean flags.
    """

    NAME = "paper_workflow"
    DESCRIPTION = "End-to-end academic literature research pipeline. Searches Semantic Scholar, downloads PDFs, generates BibTeX citations, and expands literature graphs. All steps are independently skippable via boolean flags."
    PARAMETERS = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for Semantic Scholar. The primary research topic.",
            },
            "year": {
                "type": "string",
                "description": "Year filter. Format: 'YYYY' or 'YYYY-YYYY'. Leave empty for no filter.",
            },
            "limit": {
                "type": "integer",
                "description": "Max search results. Default: 5.",
                "minimum": 1,
                "maximum": 50,
            },
            "output_dir": {
                "type": "string",
                "description": "Base output directory. Subdirectories: pdfs/, results/, citations.bib created automatically.",
            },
            "download_pdfs": {
                "type": "boolean",
                "description": "Whether to download PDF full-texts for found papers. Default: true.",
            },
            "generate_citations": {
                "type": "boolean",
                "description": "Whether to generate BibTeX citations for found papers. Default: true.",
            },
            "expand_depth": {
                "type": "integer",
                "description": "Literature expansion recursion depth. 0 = skip expansion. Default: 1.",
                "minimum": 0,
                "maximum": 3,
            },
            "expand_include_cite": {
                "type": "boolean",
                "description": "Include citations (later work) in expansion. Default: true.",
            },
            "expand_include_ref": {
                "type": "boolean",
                "description": "Include references (preceding work) in expansion. Default: true.",
            },
            "expand_include_recommend": {
                "type": "boolean",
                "description": "Include recommendations (similar papers) in expansion. Default: true.",
            },
            "top_papers_to_download": {
                "type": "integer",
                "description": "Only download PDFs for the top N papers by relevance. 0 = all papers. Default: 0.",
                "minimum": 0,
            },
        },
        "required": ["query", "output_dir"],
    }

    def __init__(self) -> None:
        config = Config()
        self._s2_client = SemanticScholarClient(config)
        self._downloader = PDFDownloader(config)
        self._converter = BibTexConverter()
        self._expansion = PaperExpansionService(self._s2_client)

    def execute(self, **kwargs: Any) -> WorkflowSummary:
        """Execute a full research pipeline: search → (optional) download → cite → (optional) expand.

        Steps execute only when enabled. The result contains summaries of all
        completed steps in a single object.
        """
        query: str = kwargs.get("query", "")
        output_dir: str = kwargs.get("output_dir", "./research")
        year: str = kwargs.get("year", "")
        limit: int = kwargs.get("limit", 5)
        download_pdfs: bool = kwargs.get("download_pdfs", True)
        generate_citations: bool = kwargs.get("generate_citations", True)
        expand_depth: int = kwargs.get("expand_depth", 1)
        top_n: int = kwargs.get("top_papers_to_download", 0)

        if not query or not query.strip():
            return WorkflowSummary(errors=["query cannot be empty."])
        if not output_dir or not output_dir.strip():
            return WorkflowSummary(errors=["output_dir cannot be empty."])

        summary = WorkflowSummary()

        # Step 1: Search
        try:
            papers = self._s2_client.search(query, year=year, limit=limit)
            summary.papers = [p.model_dump() for p in papers]
        except Exception as exc:
            summary.errors.append(f"Search failed: {exc}")

        if not summary.papers:
            return summary

        # Step 2: Download PDFs (optional)
        if download_pdfs:
            try:
                pdf_dir = os.path.join(output_dir, "pdfs")
                ids = [p.paperId for p in papers if p.paperId]
                if top_n > 0:
                    ids = ids[:top_n]
                results = self._downloader.download_batch_pdf(ids, pdf_dir)
                summary.pdfs_downloaded = sum(1 for r in results if r.success)
                failed = [r.error for r in results if r.error]
                if failed:
                    summary.errors.extend(f"PDF download failed: {r}" for r in failed)

                # Save paper-info JSON alongside PDFs (for AI context)
                import json
                for r in results:
                    if r.success and r.paper_id:
                        info_path = os.path.splitext(str(r.file_path))[0] + ".json"
                        # find matching paper
                        paper_info = None
                        for p in papers:
                            if p.paperId == r.paper_id:
                                paper_info = p.model_dump()
                                break
                        if paper_info:
                            with open(info_path, "w") as f:
                                json.dump(paper_info, f, indent=2, ensure_ascii=False)
            except Exception as exc:
                summary.errors.append(f"PDF download failed: {exc}")

        # Step 3: Generate BibTeX (optional)
        if generate_citations:
            try:
                bib_path = os.path.join(output_dir, "citations.bib")
                for p in papers:
                    authors = [a.name for a in p.authors] if p.authors else []
                    entry = self._converter.create_bibtex_entry(
                        title=p.title,
                        authors=authors,
                        year=p.year or 0,
                        venue=p.venue or "",
                        doi=p.externalIds.get("DOI", "") if p.externalIds else "",
                        arxiv_id=p.externalIds.get("ArXiv", "") if p.externalIds else "",
                        abstract=p.tldr or (p.abstract or ""),
                    )
                    summary.bibtex_entries.append(entry.to_string())
                # Also save to file
                with open(bib_path, "w") as f:
                    f.write("\n\n".join(summary.bibtex_entries))
                summary.bib_path = bib_path
            except Exception as exc:
                summary.errors.append(f"BibTeX generation failed: {exc}")

        # Step 4: Literature Expansion (optional)
        if expand_depth > 0 and summary.papers:
            try:
                seed_ids = [p.paperId for p in summary.papers[:3] if p.paperId]
                if seed_ids:
                    exp_result = self._expansion.expand_papers(
                        seeds=seed_ids,
                        depth=expand_depth,
                        include_ref=kwargs.get("expand_include_ref", True),
                        include_cite=kwargs.get("expand_include_cite", True),
                        include_recommend=kwargs.get("expand_include_recommend", True),
                    )
                    summary.expanded_papers = [p.model_dump() for p in exp_result.papers]
                    if exp_result.error:
                        summary.errors.append(f"Expansion error: {exp_result.error}")
            except Exception as exc:
                summary.errors.append(f"Literature expansion failed: {exc}")

        # Save CSV results
        try:
            import pandas as pd
            all_papers = summary.papers + [
                p for p in summary.expanded_papers
                if p.get("title") not in [sp.get("title") for sp in summary.papers]
            ]
            if all_papers:
                csv_path = os.path.join(output_dir, "results.csv")
                df = pd.DataFrame(all_papers)
                df.to_csv(csv_path, index=False)
                summary.csv_path = csv_path
        except Exception:
            pass  # CSV save is non-critical

        summary.errors = summary.errors or []
        return summary
