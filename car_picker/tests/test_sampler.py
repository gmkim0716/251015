from __future__ import annotations

from car_picker.app.indexer import CarDataset
from car_picker.app.models import Difficulty
from car_picker.app.sampler import build_question


def test_build_question_make(sample_data_dir):
    dataset = CarDataset(sample_data_dir)
    _, correct, options = build_question(dataset, Difficulty.MAKE)

    assert len(options) == 10
    labels = {option.label for option in options}
    assert len(labels) == 10
    assert correct.label in labels


def test_build_question_make_model_year(sample_data_dir):
    dataset = CarDataset(sample_data_dir)
    _, correct, options = build_question(dataset, Difficulty.MAKE_MODEL_YEAR)

    assert len(options) == 10
    assert any(option.label == correct.label for option in options)
