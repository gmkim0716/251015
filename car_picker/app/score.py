from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Dict, List

from .models import Difficulty, LeaderboardEntry, PlayerScore


@dataclass
class ScoreRecord:
    player: str
    points: int = 0
    streak: int = 0
    total_correct: int = 0
    total_attempts: int = 0

    def to_model(self) -> PlayerScore:
        return PlayerScore(
            player=self.player,
            points=self.points,
            streak=self.streak,
            total_correct=self.total_correct,
            total_attempts=self.total_attempts,
        )

    @property
    def accuracy(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.total_correct / self.total_attempts


class ScoreBoard:
    """메모리 기반 리더보드."""

    def __init__(self, max_entries: int = 10) -> None:
        self._records: Dict[str, ScoreRecord] = {}
        self._lock = threading.Lock()
        self._max_entries = max_entries

    def register_attempt(
        self,
        player: str,
        difficulty: Difficulty,
        correct: bool,
    ) -> ScoreRecord:
        with self._lock:
            record = self._records.setdefault(player, ScoreRecord(player=player))
            record.total_attempts += 1
            if correct:
                record.total_correct += 1
                record.streak += 1
                points = 10 + self._difficulty_bonus(difficulty)
                if record.streak >= 3:
                    points += 5
                record.points += points
            else:
                record.streak = 0
            return record

    def reset(self) -> int:
        with self._lock:
            cleared = len(self._records)
            self._records.clear()
            return cleared

    def top_entries(self) -> List[LeaderboardEntry]:
        with self._lock:
            sorted_records = sorted(
                self._records.values(),
                key=lambda record: (record.points, record.accuracy),
                reverse=True,
            )
            return [
                LeaderboardEntry(
                    player=record.player,
                    points=record.points,
                    accuracy=round(record.accuracy, 3),
                )
                for record in sorted_records[: self._max_entries]
            ]

    @staticmethod
    def _difficulty_bonus(difficulty: Difficulty) -> int:
        if difficulty is Difficulty.MAKE:
            return 0
        if difficulty is Difficulty.MAKE_MODEL:
            return 5
        return 10

