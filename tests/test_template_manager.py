"""TemplateManager 單元測試"""

from pathlib import Path

import pytest

from src.services.template_manager import TemplateManager


@pytest.fixture
def temp_path(tmp_path: Path) -> Path:
    return tmp_path


def test_returns_default_when_file_missing(temp_path: Path):
    manager = TemplateManager(
        storage_path=temp_path / "templates.json",
        default_templates=("A", "B"),
    )

    assert manager.get_templates() == ["A", "B"]


def test_persists_custom_templates(temp_path: Path):
    manager = TemplateManager(storage_path=temp_path / "templates.json")

    saved = manager.save_templates(["Alpha", "Beta"])
    assert saved == ["Alpha", "Beta"]
    assert manager.get_templates() == ["Alpha", "Beta"]


def test_allows_empty_template_list(temp_path: Path):
    manager = TemplateManager(
        storage_path=temp_path / "templates.json", default_templates=("A",)
    )

    manager.save_templates([])
    assert manager.get_templates() == []
