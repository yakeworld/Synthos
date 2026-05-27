"""Paper Search Skill — AI-callable wrapper around SemanticScholarClient."""

import json
from dataclasses import dataclass, field
from typing import Any

from src.api.semantic_scholar import SemanticScholarClient
from src.core.config import Config


@dataclass(frozen=True)
class SearchParams:
    query: str
    year: str = ""
    limit: int = 10
    fields: list[str] = field(default_factory=list)  # e.g. ["title","abstract","venues","tldr"]


@dataclass(frozen=True)
class SearchSkillResult:
    success: bool
    papers: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""
    total_found: int = 0


class PaperSearchSkill:
    """Search academic papers via Semantic Scholar API as an AI skill.

    Usage as LLM tool:
    ```json
    {
        "name": "paper_search",
        "arguments": {
            "query": "graph neural networks for molecular property prediction",
            "year": "2020-2024",
            "limit": 20
        }
    }
    """

    NAME = "paper_search"
    DESCRIPTION = "Search academic papers on Semantic Scholar. Returns paper metadata including title, authors, year, venue, citation count, and abstract."
    PARAMETERS = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query string. Use natural language description of the research topic (e.g. 'graph neural networks for molecular property prediction').",
            },
            "year": {
                "type": "string",
                "description": "Filter by publication year range. Format: 'YYYY' or 'YYYY-YYYY' (e.g. '2020' or '2020-2024'). Leave empty for no year filter.",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return. Default: 10. Maximum recommended: 50.",
                "minimum": 1,
                "maximum": 50,
            },
            "fields": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific fields to include in response. Options: title, authors, year, venue, journal, month, volume, pages, paperId, externalIds, url, isOpenAccess, openAccessPdf, citationCount, referenceCount, publicationTypes, publicationDate, tldr, citationStyles, isRejected, isRelevancePerceived, isInfluentialCitation. If empty, returns all available fields.",
            },
        },
        "required": ["query"],
    }

    def __init__(self) -> None:
        self._client = SemanticScholarClient(Config())

    def execute(self, **kwargs: Any) -> SearchSkillResult:
        """Execute a search and return structured results suitable for LLM consumption."""
        query: str = kwargs.get("query", "")
        year: str = kwargs.get("year", "")
        limit: int = kwargs.get("limit", 10)
        fields: list[str] = kwargs.get("fields", [])

        if not query or not query.strip():
            return SearchSkillResult(success=False, error="Query cannot be empty.")

        if not isinstance(limit, int) or limit < 1 or limit > 50:
            return SearchSkillResult(success=False, error="Limit must be an integer between 1 and 50.")

        fields_list = fields if isinstance(fields, list) else []
        year_str = str(year) if year else ""

        try:
            papers = self._client.search(query, year=year_str, limit=limit, fields=fields_list)
            paper_dicts = [p.model_dump() for p in papers]
            return SearchSkillResult(
                success=True,
                papers=paper_dicts,
                total_found=len(paper_dicts),
            )
        except Exception as exc:
            return SearchSkillResult(success=False, error=str(exc))

    def get_one_paper(self, paper_id: str) -> SearchSkillResult:
        """Fetch details for a single paper by its ID.

        Args:
            paper_id: arXiv ID, DOI, or CorpusID.

        Returns:
            SearchSkillResult with a single paper in the papers list.
        """
        if not paper_id or not paper_id.strip():
            return SearchSkillResult(success=False, error="paper_id cannot be empty.")

        try:
            paper = self._client.get_paper_details(paper_id)
            if paper is None:
                return SearchSkillResult(success=False, error=f"No paper found with ID: {paper_id}")
            return SearchSkillResult(
                success=True,
                papers=[paper.model_dump()],
                total_found=1,
            )
        except Exception as exc:
            return SearchSkillResult(success=False, error=str(exc))

    def get_citations(self, paper_id: str, limit: int = 20) -> SearchSkillResult:
        """Get papers that cite a given paper.

        Args:
            paper_id: Source paper ID (arXiv, DOI, or CorpusID).
            limit: Maximum number of citing papers to return.

        Returns:
            SearchSkillResult with citing papers.
        """
        if not paper_id:
            return SearchSkillResult(success=False, error="paper_id cannot be empty.")

        try:
            papers = self._client.get_citations(str(paper_id), limit=limit)
            paper_dicts = [p.model_dump() for p in papers]
            return SearchSkillResult(
                success=True,
                papers=paper_dicts,
                total_found=len(paper_dicts),
            )
        except Exception as exc:
            return SearchSkillResult(success=False, error=str(exc))

    def get_references(self, paper_id: str, limit: int = 20) -> SearchSkillResult:
        """Get the reference list of a given paper.

        Args:
            paper_id: Source paper ID (arXiv, DOI, or CorpusID).
            limit: Maximum number of references to return.

        Returns:
            SearchSkillResult with reference papers.
        """
        if not paper_id:
            return SearchSkillResult(success=False, error="paper_id cannot be empty.")

        try:
            papers = self._client.get_references(str(paper_id), limit=limit)
            paper_dicts = [p.model_dump() for p in papers]
            return SearchSkillResult(
                success=True,
                papers=paper_dicts,
                total_found=len(paper_dicts),
            )
        except Exception as exc:
            return SearchSkillResult(success=False, error=str(exc))

    def get_recommendations(self, paper_id: str, limit: int = 10) -> SearchSkillResult:
        """Get recommended similar papers for a given paper.

        Args:
            paper_id: Source paper ID (arXiv, DOI, or CorpusID).
            limit: Maximum number of recommendations to return.

        Returns:
            SearchSkillResult with recommended papers.
        """
        if not paper_id:
            return SearchSkillResult(success=False, error="paper_id cannot be empty.")

        try:
            papers = self._client.get_recommendations(str(paper_id), limit=limit)
            paper_dicts = [p.model_dump() for p in papers]
            return SearchSkillResult(
                success=True,
                papers=paper_dicts,
                total_found=len(paper_dicts),
            )
        except Exception as exc:
            return SearchSkillResult(success=False, error=str(exc))

    def get_author_papers(self, author_name: str, limit: int = 10) -> SearchSkillResult:
        """Get recent papers by a specific author.

        Args:
            author_name: Full author name (e.g. 'Andrew Beng Seng Ng').
            limit: Maximum number of papers to return.

        Returns:
            SearchSkillResult with author's papers.
        """
        if not author_name or not author_name.strip():
            return SearchSkillResult(success=False, error="author_name cannot be empty.")

        try:
            papers = self._client.get_author_papers(str(author_name), limit=limit)
            paper_dicts = [p.model_dump() for p in papers]
            return SearchSkillResult(
                success=True,
                papers=paper_dicts,
                total_found=len(paper_dicts),
            )
        except Exception as exc:
            return SearchSkillResult(success=False, error=str(exc))

    def search_batch(self, queries: list[str]) -> SearchSkillResult:
        """Search multiple queries in parallel against Semantic Scholar.

        Args:
            queries: List of search query strings.

        Returns:
            SearchSkillResult with aggregated results (success=True if any succeeded).
        """
        if not queries:
            return SearchSkillResult(success=False, error="queries cannot be empty.")

        try:
            results_map = self._client.search_batch(queries, limit=10)
            all_papers: list[dict[str, Any]] = []
            any_error = False
            for query, result in results_map.items():
                if result.success:
                    all_papers.extend(result.papers)
                else:
                    any_error = True
            return SearchSkillResult(
                success=not any_error or bool(all_papers),
                papers=all_papers,
                error=f"Some queries failed" if any_error else "",
                total_found=len(all_papers),
            )
        except Exception as exc:
            return SearchSkillResult(success=False, error=str(exc))
