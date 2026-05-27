"""BibTeX Conversion Skill — AI-callable wrapper around BibTexConverter."""

from dataclasses import dataclass, field
from typing import Any

from src.converter.bibtex_converter import BibTexConverter


@dataclass(frozen=True)
class ConvertParams:
    title: str
    authors: list[str]
    year: int = 0
    venue: str = ""
    doi: str = ""
    arxiv_id: str = ""
    abstract: str = ""


@dataclass(frozen=True)
class BibTeXSkillResult:
    success: bool
    bibtex: str = ""
    error: str = ""
    entry_key: str = ""


class BibTeXConvertSkill:
    """Generate and manipulate BibTeX entries for academic papers as an AI skill.

    Usage as LLM tool:
    ```json
    {
        "name": "bibtex_convert",
        "arguments": {
            "title": "Attention Is All You Need",
            "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
            "year": 2017,
            "venue": "NeurIPS",
            "action": "create",
            "doi": "10.5555/example"
        }
    }
    ```
    """

    NAME = "bibtex_convert"
    DESCRIPTION = "Generate BibTeX citation entries from paper metadata, parse BibTeX files/strings, convert CSV metadata to BibTeX, and format citations. Supports article, inproceedings, and other entry types."
    PARAMETERS = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "parse_string", "parse_file", "csv_to_bib"],
                "description": "Operation to perform: 'create' generates BibTeX from metadata fields; 'parse_string' parses a BibTeX string; 'parse_file' reads and parses a .bib file; 'csv_to_bib' converts CSV paper metadata to BibTeX.",
            },
            "title": {"type": "string", "description": "Paper title (required for 'create' action)."},
            "authors": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of author names (required for 'create' action).",
            },
            "year": {
                "type": "integer",
                "description": "Publication year (optional for 'create').",
            },
            "venue": {"type": "string", "description": "Journal/conference name (optional for 'create')."},
            "doi": {"type": "string", "description": "Digital Object Identifier (optional for 'create')."},
            "arxiv_id": {"type": "string", "description": "arXiv identifier (optional for 'create')."},
            "abstract": {"type": "string", "description": "Paper abstract text (optional for 'create')."},
            "bib_text": {
                "type": "string",
                "description": "Raw BibTeX string to parse (required for 'parse_string' action).",
            },
            "file_path": {
                "type": "string",
                "description": "Path to BibTeX file to parse (required for 'parse_file' action).",
            },
            "csv_path": {
                "type": "string",
                "description": "Path to CSV file with paper metadata (required for 'csv_to_bib' action).",
            },
            "output_path": {
                "type": "string",
                "description": "Path to write BibTeX output file (for 'csv_to_bib' action).",
            },
            "entry_type": {
                "type": "string",
                "enum": ["article", "inproceedings", "misc"],
                "description": "BibTeX entry type for 'create' action. Default: 'article'.",
            },
        },
        "required": ["action"],
    }

    def __init__(self) -> None:
        self._converter = BibTexConverter()

    def create_entry(
        self,
        title: str,
        authors: list[str],
        year: int = 0,
        venue: str = "",
        doi: str = "",
        arxiv_id: str = "",
        abstract: str = "",
        entry_type: str = "article",
    ) -> BibTeXSkillResult:
        """Create a BibTeX entry from structured paper metadata.

        This is the main flow for generating citations after a paper search.
        """
        if not title or not title.strip():
            return BibTeXSkillResult(success=False, error="title cannot be empty.")
        if not authors:
            return BibTeXSkillResult(success=False, error="authors cannot be empty list.")

        try:
            entry = self._converter.create_bibtex_entry(
                title=title,
                authors=authors,
                year=year if year else 0,
                venue=venue if venue else "",
                doi=doi if doi else "",
                arxiv_id=arxiv_id if arxiv_id else "",
                abstract=abstract if abstract else "",
                entry_type=entry_type,
            )
            return BibTeXSkillResult(
                success=True,
                bibtex=entry.to_string(),
                entry_key=entry.key,
            )
        except Exception as exc:
            return BibTeXSkillResult(success=False, error=str(exc))

    def parse_string(self, bib_text: str) -> BibTeXSkillResult:
        """Parse a BibTeX string and return structured entries.

        Args:
            bib_text: Raw BibTeX text containing one or more entries.

        Returns:
            BibTeXSkillResult with all parsed entries as a combined BibTeX string.
        """
        if not bib_text or not bib_text.strip():
            return BibTeXSkillResult(success=False, error="bib_text cannot be empty.")

        try:
            entries = self._converter.parse_bibtex_string(bib_text)
            output = "\n\n".join(e.to_string() for e in entries)
            return BibTeXSkillResult(
                success=True,
                bibtex=output,
                entry_key=f"{len(entries)} entries parsed",
            )
        except Exception as exc:
            return BibTeXSkillResult(success=False, error=str(exc))

    def parse_file(self, file_path: str) -> BibTeXSkillResult:
        """Parse a BibTeX file and return all entries.

        Args:
            file_path: Path to a .bib file.

        Returns:
            BibTeXSkillResult with parsed entries.
        """
        if not file_path or not file_path.strip():
            return BibTeXSkillResult(success=False, error="file_path cannot be empty.")

        try:
            entries = self._converter.parse_bibtex_file(str(file_path))
            output = "\n\n".join(e.to_string() for e in entries)
            return BibTeXSkillResult(
                success=True,
                bibtex=output,
                entry_key=f"{len(entries)} entries parsed from {file_path}",
            )
        except Exception as exc:
            return BibTeXSkillResult(success=False, error=str(exc))

    def csv_to_bib(self, csv_path: str, output_path: str = "") -> BibTeXSkillResult:
        """Convert CSV paper metadata to a BibTeX file.

        Args:
            csv_path: Path to CSV file with paper metadata (title, authors, year, etc.).
            output_path: Path to write the output BibTeX file. If empty, returns in memory.

        Returns:
            BibTeXSkillResult with the generated BibTeX content.
        """
        if not csv_path or not csv_path.strip():
            return BibTeXSkillResult(success=False, error="csv_path cannot be empty.")

        try:
            content = self._converter.convert_csv_to_bib(str(csv_path), str(output_path) if output_path else "")
            return BibTeXSkillResult(
                success=True,
                bibtex=content,
                entry_key=f"CSV converted: {csv_path}",
            )
        except Exception as exc:
            return BibTeXSkillResult(success=False, error=str(exc))

    def execute(self, **kwargs: Any) -> BibTeXSkillResult:
        """Unified entry point — dispatches to the appropriate method based on 'action'.

        Maps actions: create, parse_string, parse_file, csv_to_bib.
        """
        action: str = kwargs.get("action", "")

        if action == "create":
            return self.create_entry(
                title=kwargs.get("title", ""),
                authors=kwargs.get("authors", []),
                year=kwargs.get("year", 0),
                venue=kwargs.get("venue", ""),
                doi=kwargs.get("doi", ""),
                arxiv_id=kwargs.get("arxiv_id", ""),
                abstract=kwargs.get("abstract", ""),
                entry_type=kwargs.get("entry_type", "article"),
            )
        elif action == "parse_string":
            return self.parse_string(kwargs.get("bib_text", ""))
        elif action == "parse_file":
            return self.parse_file(kwargs.get("file_path", ""))
        elif action == "csv_to_bib":
            return self.csv_to_bib(
                csv_path=kwargs.get("csv_path", ""),
                output_path=kwargs.get("output_path", ""),
            )
        else:
            return BibTeXSkillResult(
                success=False,
                error=f"Unknown action: '{action}'. Valid: create, parse_string, parse_file, csv_to_bib.",
            )
