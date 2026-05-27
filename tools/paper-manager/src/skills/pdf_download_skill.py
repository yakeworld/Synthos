"""PDF Download Skill — AI-callable wrapper around PDFDownloader."""

from dataclasses import dataclass, field
from typing import Any

from src.downloader.pdf_downloader import PDFDownloader
from src.core.config import Config


@dataclass(frozen=True)
class DownloadParams:
    source_id: str
    output_dir: str = "./research/pdfs"
    title_prefix: str = ""


@dataclass(frozen=True)
class DownloadSkillResult:
    success: bool
    file_path: str = ""
    error: str = ""
    paper_id: str = ""
    title: str = ""


class PDFDownloadSkill:
    """Download full-text PDFs of academic papers from arXiv/Sci-Hub as an AI skill.

    Usage as LLM tool:
    ```json
    {
        "name": "pdf_download",
        "arguments": {
            "source_id": "2403.12345",
            "output_dir": "./literature/pdfs",
            "title_prefix": "GNN-review"
        }
    }
    """

    NAME = "pdf_download"
    DESCRIPTION = "Download PDF full-text of a paper from arXiv or Sci-Hub. Resolves paper IDs (arXiv, DOI, CorpusID) and saves PDF to a specified directory with auto-generated filenames."
    PARAMETERS = {
        "type": "object",
        "properties": {
            "source_id": {
                "type": "string",
                "description": "Paper identifier. Accepts arXiv ID (e.g. '2403.12345', 'arXiv:2403.12345'), DOI (e.g. '10.1234/fake.2024'), or CorpusID (e.g. 'CorpusID:12345678'). Bare IDs like '2403.12345' are auto-detected as arXiv.",
            },
            "output_dir": {
                "type": "string",
                "description": "Directory path to save the downloaded PDF file. Will be created if it does not exist. Default: './research/pdfs'.",
            },
            "title_prefix": {
                "type": "string",
                "description": "Optional prefix for the saved filename. If empty, uses auto-generated name from paper info. Useful for batch organizing papers by project name.",
            },
        },
        "required": ["source_id", "output_dir"],
    }

    def __init__(self) -> None:
        self._downloader = PDFDownloader(Config())

    def execute(self, **kwargs: Any) -> DownloadSkillResult:
        """Download a single PDF and return file location.

        Download priority: Open Access URL → arXiv direct → Sci-Hub mirrors (rotated on failure).
        """
        source_id: str = kwargs.get("source_id", "")
        output_dir: str = kwargs.get("output_dir", "./research/pdfs")
        title_prefix: str = kwargs.get("title_prefix", "")

        if not source_id or not source_id.strip():
            return DownloadSkillResult(success=False, error="source_id cannot be empty.")
        if not output_dir or not output_dir.strip():
            return DownloadSkillResult(success=False, error="output_dir cannot be empty.")

        try:
            result = self._downloader.download_pdf(
                source_id=str(source_id),
                output_dir=str(output_dir),
                title_prefix=str(title_prefix) or "",
            )
            return DownloadSkillResult(
                success=result.success,
                file_path=str(result.file_path) if result.file_path else "",
                error=str(result.error),
                paper_id=str(paper_id) if (paper_id := result.paper_id) else "",
                title=str(result.title) if (title := result.title) else "",
            )
        except Exception as exc:
            return DownloadSkillResult(success=False, error=str(exc))

    def batch_download(
        self,
        source_ids: list[str],
        output_dir: str,
        title_prefix: str = "",
    ) -> DownloadSkillResult:
        """Download multiple PDFs in parallel.

        Args:
            source_ids: List of paper identifiers.
            output_dir: Directory to save PDFs.
            title_prefix: Optional filename prefix appended per paper.

        Returns:
            DownloadSkillResult summarizing success/failure counts.
        """
        if not source_ids:
            return DownloadSkillResult(success=False, error="source_ids cannot be empty.")

        try:
            prefix = str(title_prefix) or ""
            results = self._downloader.download_batch_pdf(
                source_ids=[str(sid) for sid in source_ids],
                output_dir=str(output_dir),
                title_prefix=prefix,
            )

            total = len(results)
            ok = sum(1 for r in results if r.success)

            if ok == total:
                last_path = str(results[-1].file_path) if results[-1].file_path else ""
                return DownloadSkillResult(
                    success=True,
                    file_path=last_path,
                    paper_id=str(results[-1].paper_id) if results[-1].paper_id else "",
                    title=str(results[-1].title) if results[-1].title else "",
                )
            else:
                errors = [str(r.error) for r in results if not r.success]
                return DownloadSkillResult(
                    success=False,
                    error=f"Partially successful: {ok}/{total} downloaded. Errors: {'; '.join(errors[:3])}",
                )
        except Exception as exc:
            return DownloadSkillResult(success=False, error=str(exc))
