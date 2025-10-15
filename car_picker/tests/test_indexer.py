from __future__ import annotations

from pathlib import Path

import pytest

from car_picker.app.indexer import CarDataset, parse_filename


def test_parse_filename_valid(tmp_path: Path):
    file_path = tmp_path / "Audi_A5_2013_40_18_200_20_4_70_55_180_30_FWD_5_4_Sedan_ABC.jpg"
    file_path.write_bytes(b"\xff\xd8\xff")

    entry = parse_filename(file_path)
    assert entry is not None
    assert entry.make == "Audi"
    assert entry.model == "A5"
    assert entry.year == "2013"
    assert entry.relative_path == file_path.name


def test_parse_filename_invalid_year(tmp_path: Path):
    file_path = tmp_path / "Audi_A5_20x3_rest_ABC.jpg"
    file_path.write_bytes(b"\xff\xd8\xff")

    entry = parse_filename(file_path)
    assert entry is None


def test_dataset_loads_entries(sample_data_dir: Path):
    dataset = CarDataset(sample_data_dir)
    assert len(dataset.entries) == len(list(sample_data_dir.glob("*.jpg")))
    assert dataset.by_make["Audi"]
    assert dataset.by_make["BMW"]
