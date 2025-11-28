"""範本管理服務"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable, List, Optional

logger = logging.getLogger(__name__)


class TemplateManager:
    """管理加班內容範本清單"""

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        default_templates: Optional[Iterable[str]] = None,
    ) -> None:
        self.storage_path = (
            Path(storage_path)
            if storage_path
            else Path("cache") / "overtime_templates.json"
        )
        self.default_templates = [t for t in (default_templates or ()) if t]

    def get_templates(self) -> List[str]:
        """讀取範本清單,若無檔案則回傳預設值"""
        if not self.storage_path.exists():
            return list(self.default_templates)

        try:
            with self.storage_path.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
        except (OSError, json.JSONDecodeError) as error:
            logger.warning("讀取範本檔案失敗,使用預設值: %s", error)
            return list(self.default_templates)

        if not isinstance(data, list):
            return list(self.default_templates)

        templates = [
            str(item).strip() for item in data if isinstance(item, str) and item.strip()
        ]
        return templates

    def save_templates(self, templates: Iterable[str]) -> List[str]:
        """儲存範本清單,回傳整理後的結果"""
        cleaned = [str(item).strip() for item in templates if str(item).strip()]

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.storage_path.open("w", encoding="utf-8") as fp:
            json.dump(cleaned, fp, ensure_ascii=False, indent=2)

        logger.info("已更新加班範本,共 %d 筆", len(cleaned))
        return cleaned

    def reset_to_default(self) -> List[str]:
        """將範本還原為預設值"""
        return self.save_templates(self.default_templates)
