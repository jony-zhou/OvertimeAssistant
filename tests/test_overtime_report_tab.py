"""OvertimeReportTab UI 邏輯測試"""

import pytest
import customtkinter as ctk
from tkinter import TclError

from src.models import OvertimeSubmissionRecord
from src.services.template_manager import TemplateManager
from ui.components.overtime_report_tab import OvertimeReportTab


@pytest.fixture
def tk_root():
    """建立 Tk 根節點,測試結束後銷毀"""
    try:
        root = ctk.CTk()
    except TclError:
        pytest.skip("Tkinter 環境不可用,略過 UI 測試")
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def template_manager(tmp_path):
    """提供測試用的範本管理器"""
    storage_path = tmp_path / "templates.json"
    return TemplateManager(
        storage_path=storage_path,
        default_templates=("專案開發", "系統維護"),
    )


def _build_tab_with_records(root, records, template_manager):
    tab = OvertimeReportTab(root, template_manager=template_manager)
    tab.submission_records = records
    tab._refresh_records_ui()
    root.update_idletasks()
    return tab


def test_template_applies_to_selected_records(tk_root, template_manager):
    """套用範本時,僅更新勾選的記錄"""
    records = [
        OvertimeSubmissionRecord(
            date="2025/11/25",
            description="",
            overtime_hours=1.5,
            is_selected=True,
        ),
        OvertimeSubmissionRecord(
            date="2025/11/26",
            description="舊有內容",
            overtime_hours=2.0,
            is_selected=False,
        ),
    ]

    tab = _build_tab_with_records(tk_root, records, template_manager)

    tab._apply_template_to_records("專案開發")

    assert records[0].description == "專案開發"
    assert records[1].description == "舊有內容"

    entry = tab.record_content_entries.get(id(records[0]))
    assert entry is not None
    assert entry.get() == "專案開發"


def test_template_applies_when_no_selection(tk_root, template_manager):
    """未勾選任何記錄時,範本套用至全部未送出記錄"""
    records = [
        OvertimeSubmissionRecord(
            date="2025/11/27",
            description="",
            overtime_hours=1.0,
            is_selected=False,
        ),
        OvertimeSubmissionRecord(
            date="2025/11/28",
            description="",
            overtime_hours=0.5,
            is_selected=False,
        ),
    ]

    tab = _build_tab_with_records(tk_root, records, template_manager)

    tab._apply_template_to_records("系統維護")

    for record in records:
        assert record.description == "系統維護"
        entry = tab.record_content_entries.get(id(record))
        assert entry is not None
        assert entry.get() == "系統維護"


def test_template_menu_updates_with_saved_values(tk_root, template_manager):
    """確保範本選單能夠反映最新儲存的範本"""
    tab = OvertimeReportTab(tk_root, template_manager=template_manager)
    tk_root.update_idletasks()

    template_manager.save_templates(["自訂範本A", "自訂範本B"])
    tab._refresh_template_menu()

    assert tab.template_menu is not None
    values = tuple(tab.template_menu.cget("values"))
    assert values == ("套用範本", "自訂範本A", "自訂範本B")
    assert tab.template_menu.cget("state") == "normal"

    template_manager.save_templates([])
    tab._refresh_template_menu()
    assert tab.template_menu is not None
    assert tuple(tab.template_menu.cget("values")) == ("套用範本",)
    assert tab.template_menu.cget("state") == "disabled"
