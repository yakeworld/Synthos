"""Skill registry — metadata and factory for all registered skills."""

from typing import Any, Callable

from src.skills.paper_search_skill import PaperSearchSkill
from src.skills.pdf_download_skill import PDFDownloadSkill
from src.skills.bibtex_convert_skill import BibTeXConvertSkill
from src.skills.literature_expand_skill import LiteratureExpandSkill
from src.skills.paper_workflow_skill import PaperWorkflowSkill


_REGISTERED: dict[str, type] = {}


def _register(cls: type) -> type:
    """Decorate a skill class to register it in the global registry."""
    _REGISTERED[cls.NAME] = cls
    return cls


@_register
class _PaperSearch(PaperSearchSkill):
    pass


@_register
class _PDFDownload(PDFDownloadSkill):
    pass


@_register
class _BibTeXConvert(BibTeXConvertSkill):
    pass


@_register
class _LiteratureExpand(LiteratureExpandSkill):
    pass


@_register
class _PaperWorkflow(PaperWorkflowSkill):
    pass


# Re-export the canonical (non-duplicated) classes
PaperSearchSkill = _PaperSearch
PDFDownloadSkill = _PDFDownload
BibTeXConvertSkill = _BibTeXConvert
LiteratureExpandSkill = _LiteratureExpand
PaperWorkflowSkill = _PaperWorkflow


def _get_metadata(name: str) -> dict[str, Any]:
    """Return skill metadata: name, description, parameters."""
    cls = _REGISTERED.get(name)
    if not cls:
        return {}
    instance = cls()
    return {
        "name": cls.NAME,
        "description": cls.DESCRIPTION,
        "parameters": cls.PARAMETERS,
    }


class SkillRegistry:
    """Central registry mapping skill names to callable skill instances.

    Example:
        registry = SkillRegistry()
        skill = registry.get("paper_search")
        result = skill.execute(query="GNN", limit=10)
    """

    def __init__(self) -> None:
        self._skills: dict[str, Any] = {}
        for name, cls in _REGISTERED.items():
            self._skills[name] = cls()

    def get(self, name: str) -> Any | None:
        """Get a skill instance by name, or None if not found."""
        return self._skills.get(name)

    def list_skills(self) -> list[dict[str, Any]]:
        """Return metadata for all registered skills."""
        return [_get_metadata(name) for name in self._skills]

    def invoke(self, name: str, **kwargs: Any) -> Any:
        """Get a skill and immediately execute it with the given kwargs."""
        skill = self._skills.get(name)
        if skill is None:
            raise KeyError(f"Unknown skill: '{name}'. Available: {list(self._skills.keys())}")
        return skill.execute(**kwargs)

    @property
    def available(self) -> list[str]:
        """List of all registered skill names."""
        return list(self._skills.keys())


skill_registry = SkillRegistry()
