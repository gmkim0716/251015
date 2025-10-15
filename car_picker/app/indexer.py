from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, Optional

from .models import CarEntry

LOGGER = logging.getLogger(__name__)


def parse_filename(path: Path) -> Optional[CarEntry]:
    """파일명을 파싱하여 CarEntry를 생성."""
    name = path.stem
    parts = name.split("_")
    if len(parts) < 4:
        LOGGER.debug("무시: 필드 수 부족 (%s)", path.name)
        return None

    make, model, year = parts[0], parts[1], parts[2]
    if not make or not model:
        LOGGER.debug("무시: 제조사/모델 정보 부족 (%s)", path.name)
        return None
    if len(year) != 4 or not year.isdigit():
        LOGGER.debug("무시: 연식이 4자리 숫자가 아님 (%s)", path.name)
        return None

    relative_path = path.name
    entry_id = name

    return CarEntry(
        id=entry_id,
        make=make,
        model=model,
        year=year,
        relative_path=relative_path,
    )


class CarDataset:
    """이미지 데이터셋 인덱스."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.entries: List[CarEntry] = []
        self.by_make: DefaultDict[str, List[CarEntry]] = defaultdict(list)
        self.by_model: DefaultDict[str, List[CarEntry]] = defaultdict(list)
        self.make_model_map: DefaultDict[tuple[str, str], List[CarEntry]] = defaultdict(list)
        self._load()

    def _load(self) -> None:
        LOGGER.info("데이터 디렉터리 스캔 중: %s", self.data_dir)
        for path in sorted(self.data_dir.glob("*.jpg")):
            entry = parse_filename(path)
            if entry is None:
                continue
            self.entries.append(entry)
            self.by_make[entry.make].append(entry)
            self.by_model[entry.model].append(entry)
            self.make_model_map[(entry.make, entry.model)].append(entry)

        LOGGER.info("총 %d개의 항목 로드", len(self.entries))

    @property
    def unique_makes(self) -> List[str]:
        return list(self.by_make.keys())

    @property
    def unique_models(self) -> List[str]:
        return list(self.by_model.keys())

    def random_entries(self) -> Iterable[CarEntry]:
        import random

        shuffled = self.entries[:]
        random.shuffle(shuffled)
        return shuffled

    def get_entries_by_make(self, make: str) -> List[CarEntry]:
        return self.by_make.get(make, [])

    def get_entries_by_model(self, model: str) -> List[CarEntry]:
        return self.by_model.get(model, [])

    def get_entries_by_make_model(self, make: str, model: str) -> List[CarEntry]:
        return self.make_model_map.get((make, model), [])

    def resolve_path(self, entry: CarEntry) -> Path:
        return self.data_dir / entry.relative_path

