"""Literature Expansion Skill — AI-callable wrapper around PaperExpansionService."""

from dataclasses import dataclass, field
from typing import Any

from src.manager.expansion_service import PaperExpansionService
from src.api.semantic_scholar import SemanticScholarClient
from src.core.config import Config


@dataclass(frozen=True)
class ExpandParams:
    seeds: list[str]
    depth: int = 1
    include_ref: bool = True
    include_cite: bool = True
    include_recommend: bool = True
    author_expand: bool = False
    limit: int = 30
    csv_output: str = ""


@dataclass(frozen=True)
class ExpandSkillResult:
    success: bool
    papers: list[dict[str, Any]] = field(default_factory=list)
    total_unique: int = 0
    error: str = ""
    depth_reached: int = 0
    csv_path: str = ""


class LiteratureExpandSkill:
    """Expand a literature graph from seed papers via citations, references, and recommendations.

    Usage as LLM tool:
    ```json
    {
        "name": "literature_expand",
        "arguments": {
            "seeds": ["2403.12345", "10.1234/fake.2024"],
            "depth": 2,
            "include_ref": true,
            "include_cite": true,
            "csv_output": "./literature/expanded.csv"
        }
    }
    ```
    """

    NAME = "literature_expand"
    DESCRIPTION = "Expand a set of seed papers into a literature graph by following references (preceding work), citations (later work), and recommendations (similar papers). Supports recursive expansion to discover the full citation context of a research topic. Saves structured CSV and BibTeX output."
    PARAMETERS = {
        "type": "object",
        "properties": {
            "seeds": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of seed paper IDs (arXiv, DOI, CorpusID). At least one is required.",
            },
            "depth": {
                "type": "integer",
                "description": "Maximum expansion depth (recursion). 1 = only explore direct neighbors; 2 = neighbors + their neighbors. Default: 1. Max recommended: 3.",
                "minimum": 1,
                "maximum": 5,
            },
            "include_ref": {
                "type": "boolean",
                "description": "Include references (papers this paper cites / preceding work). Default: true.",
            },
            "include_cite": {
                "type": "boolean",
                "description": "Include citations (papers that cite this paper / later work). Default: true.",
            },
            "include_recommend": {
                "type": "boolean",
                "description": "Include recommendations (similar papers discovered by S2). Default: true.",
            },
            "author_expand": {
                "type": "boolean",
                "description": "Also fetch papers by the same authors of seed papers. Default: false.",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum papers per individual query (citation, reference, recommendation fetches). Default: 30.",
                "minimum": 1,
                "maximum": 100,
            },
            "csv_output": {
                "type": "string",
                "description": "Path to save results as CSV (e.g. './research/expanded.csv'). If empty, returns only in-memory results.",
            },
        },
        "required": ["seeds"],
    }

    def __init__(self) -> None:
        self._client = SemanticScholarClient(Config())
        self._service = PaperExpansionService(self._client)

    def execute(self, **kwargs: Any) -> ExpandSkillResult:
        """Execute literature graph expansion from seed papers.

        Walks references, citations, and recommendations in a BFS manner up to the
        specified depth, collecting all discovered papers.
        """
        seeds: list[str] = kwargs.get("seeds", [])
        depth: int = kwargs.get("depth", 1)
        include_ref: bool = kwargs.get("include_ref", True)
        include_cite: bool = kwargs.get("include_cite", True)
        include_recommend: bool = kwargs.get("include_recommend", True)
        author_expand: bool = kwargs.get("author_expand", False)
        limit: int = kwargs.get("limit", 30)
        csv_output: str = kwargs.get("csv_output", "")

        if not seeds:
            return ExpandSkillResult(success=False, error="seeds cannot be empty.")
        if not isinstance(seeds, list) or not seeds:
            return ExpandSkillResult(success=False, error="seeds must be a non-empty list.")

        try:
            result = self._service.expand_papers(
                seeds=[str(s) for s in seeds],
                depth=int(depth),
                include_ref=bool(include_ref),
                include_cite=bool(include_cite),
                include_recommend=bool(include_recommend),
                author_expand=bool(author_expand),
                limit=int(limit),
                csv_output=str(csv_output) if csv_output else "",
            )

            paper_dicts = [paper.model_dump() for paper in result.papers]
            return ExpandSkillResult(
                success=not result.paper_ids.failed_ids or len(result.papers) > 0,
                papers=paper_dicts,
                total_unique=len(result.paper_ids.seen_ids) if result.paper_ids else 0,
                error=str(result.error) if result.error else "",
                depth_reached=result.depth,
                csv_path=str(result.csv_path) if result.csv_path else "",
            )
        except Exception as exc:
            return ExpandSkillResult(success=False, error=str(exc))

    def expand_author_graph(
        self,
        author_name: str,
        depth: int = 1,
        limit: int = 30,
        csv_output: str = "",
    ) -> ExpandSkillResult:
        """Expand a literature graph centered on a specific author.

        Fetches all papers by `author_name`, then expands those papers'
        citations, references, and recommendations recursively.

        Args:
            author_name: Full name of the researcher (e.g. 'Andrew Beng Seng Ng').
            depth: Expansion recursion depth.
            limit: Max papers per query.
            csv_output: Save path for CSV results.

        Returns:
            ExpandSkillResult with all discovered papers.
        """
        if not author_name or not author_name.strip():
            return ExpandSkillResult(success=False, error="author_name cannot be empty.")

        try:
            return self.execute(
                seeds=[str(author_name)],
                depth=depth,
                include_ref=True,
                include_cite=True,
                include_recommend=True,
                author_expand=True,
                limit=limit,
                csv_output=csv_output,
            )
        except Exception as exc:
            return ExpandSkillResult(success=False, error=str(exc))

    def expand_from_bibtex(
        self,
        bib_path: str,
        depth: int = 1,
        csv_output: str = "",
    ) -> ExpandSkillResult:
        """Extract seed paper IDs from a BibTeX file and expand from them.

        Args:
            bib_path: Path to a .bib file containing reference entries.
            depth: Expansion recursion depth.
            csv_output: Save path for CSV results.

        Returns:
            ExpandSkillResult with the expanded literature graph.
        """
        if not bib_path or not bib_path.strip():
            return ExpandSkillResult(success=False, error="bib_path cannot be empty.")

        try:
            result = self._service.expand_from_bibtex(
                bib_path=str(bib_path),
                depth=int(depth),
                csv_output=str(csv_output) if csv_output else "",
            )

            paper_dicts = [paper.model_dump() for paper in result.papers]
            return ExpandSkillResult(
                success=not result.paper_ids.failed_ids or len(result.papers) > 0,
                papers=paper_dicts,
                total_unique=len(result.paper_ids.seen_ids) if result.paper_ids else 0,
                error=str(result.error) if result.error else "",
                depth_reached=result.depth,
                csv_path=str(result.csv_path) if result.csv_path else "",
            )
        except Exception as exc:
            return ExpandSkillResult(success=False, error=str(exc))
