from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pytest

from car_picker.app import settings as app_settings
from car_picker.app.main import create_app


SAMPLE_CARS = [
    ("Audi", "A5", "2013", "AAA"),
    ("Audi", "A5", "2014", "AAB"),
    ("Audi", "A4", "2013", "AAC"),
    ("BMW", "3Series", "2015", "BBA"),
    ("BMW", "X5", "2016", "BBB"),
    ("Hyundai", "Sonata", "2018", "HYA"),
    ("Kia", "Morning", "2017", "KIA"),
    ("Ford", "Focus", "2015", "FOA"),
    ("Toyota", "Camry", "2019", "TOA"),
    ("Honda", "Civic", "2020", "HOA"),
    ("Mercedes-Benz", "C300", "2018", "MBA"),
    ("Nissan", "Altima", "2016", "NIA"),
    ("Lexus", "RX350", "2021", "LEX"),
]


def _write_sample_image(directory: Path, make: str, model: str, year: str, suffix: str) -> None:
    filename = f"{make}_{model}_{year}_40_18_200_20_4_70_55_180_30_FWD_5_4_Sedan_{suffix}.jpg"
    (directory / filename).write_bytes(b"\xff\xd8\xff")  # JPEG header bytes


@pytest.fixture(scope="session")
def sample_data_dir(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    data_dir = tmp_path_factory.mktemp("car_data")
    for make, model, year, suffix in SAMPLE_CARS:
        _write_sample_image(data_dir, make, model, year, suffix)

    yield data_dir


@pytest.fixture(autouse=True)
def configure_settings(monkeypatch: pytest.MonkeyPatch, sample_data_dir: Path) -> Iterator[None]:
    monkeypatch.setenv("CAR_PICKER_DATA_DIR", str(sample_data_dir))
    app_settings.get_settings.cache_clear()
    yield
    app_settings.get_settings.cache_clear()


@pytest.fixture
def fastapi_app():
    return create_app()
