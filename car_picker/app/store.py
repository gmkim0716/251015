from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from threading import Lock
from typing import Dict, Optional

from .models import Difficulty, QuizOption


@dataclass
class StoredQuestion:
    qid: str
    difficulty: Difficulty
    correct: QuizOption
    created_at: float


class QuestionStore:
    """최근 출제된 문제 정보를 유지하여 서버 채점에 활용."""

    def __init__(self, limit: int = 512, ttl_seconds: int = 600) -> None:
        self._limit = limit
        self._ttl_seconds = ttl_seconds
        self._lock = Lock()
        self._store: Dict[str, StoredQuestion] = {}

    def issue(
        self,
        difficulty: Difficulty,
        correct: QuizOption,
    ) -> StoredQuestion:
        qid = uuid.uuid4().hex
        stored = StoredQuestion(
            qid=qid,
            difficulty=difficulty,
            correct=correct,
            created_at=time.time(),
        )
        with self._lock:
            if len(self._store) >= self._limit:
                self._evict_oldest()
            self._store[qid] = stored
        return stored

    def resolve(self, qid: str) -> Optional[StoredQuestion]:
        with self._lock:
            stored = self._store.pop(qid, None)
        if stored and (time.time() - stored.created_at) > self._ttl_seconds:
            return None
        return stored

    def _evict_oldest(self) -> None:
        oldest_key = None
        oldest_time = float("inf")
        for key, value in self._store.items():
            if value.created_at < oldest_time:
                oldest_time = value.created_at
                oldest_key = key
        if oldest_key is not None:
            self._store.pop(oldest_key, None)

