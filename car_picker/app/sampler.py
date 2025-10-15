from __future__ import annotations

import random
from typing import List, Set

from .indexer import CarDataset
from .models import CarEntry, Difficulty, QuizOption


def build_question(
    dataset: CarDataset,
    difficulty: Difficulty,
    exclude_ids: Set[str] | None = None,
) -> tuple[CarEntry, QuizOption, List[QuizOption]]:
    """질문과 보기 목록을 생성한다."""
    exclude_ids = exclude_ids or set()
    candidates = [entry for entry in dataset.entries if entry.id not in exclude_ids]
    if not candidates:
        raise ValueError("사용 가능한 항목이 없습니다.")

    correct_entry = random.choice(candidates)
    correct_option = _make_option(correct_entry, difficulty)
    options = _generate_options(dataset, correct_entry, difficulty)
    return correct_entry, correct_option, options


def _generate_options(
    dataset: CarDataset,
    correct: CarEntry,
    difficulty: Difficulty,
    option_count: int = 10,
) -> List[QuizOption]:
    option_map: dict[str, QuizOption] = {}

    def add_option(entry: CarEntry) -> None:
        option = _make_option(entry, difficulty)
        if option.label in option_map:
            return
        option_map[option.label] = option

    add_option(correct)

    if difficulty is Difficulty.MAKE:
        _fill_make_options(dataset, correct.make, option_map, option_count)
    elif difficulty is Difficulty.MAKE_MODEL:
        _fill_make_model_options(dataset, correct, option_map, option_count)
    else:
        _fill_make_model_year_options(dataset, correct, option_map, option_count)

    options = list(option_map.values())
    if len(options) < option_count:
        raise ValueError("충분한 보기 생성에 실패했습니다.")

    random.shuffle(options)
    return options[:option_count]


def _fill_make_options(
    dataset: CarDataset,
    correct_make: str,
    option_map: dict[str, QuizOption],
    option_count: int,
) -> None:
    makes = dataset.unique_makes[:]
    random.shuffle(makes)
    for make in makes:
        if make == correct_make:
            continue
        entries = dataset.get_entries_by_make(make)
        if not entries:
            continue
        entry = random.choice(entries)
        option = _make_option(entry, Difficulty.MAKE)
        if option.label not in option_map:
            option_map[option.label] = option
        if len(option_map) >= option_count:
            break


def _fill_make_model_options(
    dataset: CarDataset,
    correct: CarEntry,
    option_map: dict[str, QuizOption],
    option_count: int,
) -> None:
    same_make_entries = dataset.get_entries_by_make(correct.make)
    shuffled = same_make_entries[:]
    random.shuffle(shuffled)
    for entry in shuffled:
        if entry.model == correct.model:
            continue
        option = _make_option(entry, Difficulty.MAKE_MODEL)
        if option.label not in option_map:
            option_map[option.label] = option
        if len(option_map) >= option_count:
            return

    _fill_random_entries(dataset, option_map, option_count, Difficulty.MAKE_MODEL)


def _fill_make_model_year_options(
    dataset: CarDataset,
    correct: CarEntry,
    option_map: dict[str, QuizOption],
    option_count: int,
) -> None:
    variants = dataset.get_entries_by_make_model(correct.make, correct.model)
    shuffled = variants[:]
    random.shuffle(shuffled)
    for entry in shuffled:
        if entry.year == correct.year:
            continue
        option = _make_option(entry, Difficulty.MAKE_MODEL_YEAR)
        if option.label not in option_map:
            option_map[option.label] = option
        if len(option_map) >= option_count:
            return

    same_make = dataset.get_entries_by_make(correct.make)
    shuffled_same_make = same_make[:]
    random.shuffle(shuffled_same_make)
    for entry in shuffled_same_make:
        if entry.model == correct.model and entry.year == correct.year:
            continue
        option = _make_option(entry, Difficulty.MAKE_MODEL_YEAR)
        if option.label not in option_map:
            option_map[option.label] = option
        if len(option_map) >= option_count:
            return

    _fill_random_entries(dataset, option_map, option_count, Difficulty.MAKE_MODEL_YEAR)


def _fill_random_entries(
    dataset: CarDataset,
    option_map: dict[str, QuizOption],
    option_count: int,
    difficulty: Difficulty,
) -> None:
    entries = dataset.entries[:]
    random.shuffle(entries)
    for entry in entries:
        option = _make_option(entry, difficulty)
        if option.label in option_map:
            continue
        option_map[option.label] = option
        if len(option_map) >= option_count:
            return


def _format_label(entry: CarEntry, difficulty: Difficulty) -> str:
    if difficulty is Difficulty.MAKE:
        return entry.make
    if difficulty is Difficulty.MAKE_MODEL:
        return f"{entry.make} {entry.model}"
    return f"{entry.make} {entry.model} {entry.year}"


def _make_option(entry: CarEntry, difficulty: Difficulty) -> QuizOption:
    label = _format_label(entry, difficulty)
    if difficulty is Difficulty.MAKE:
        return QuizOption(make=entry.make, label=label)
    if difficulty is Difficulty.MAKE_MODEL:
        return QuizOption(make=entry.make, model=entry.model, label=label)
    return QuizOption(make=entry.make, model=entry.model, year=entry.year, label=label)
