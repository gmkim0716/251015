from __future__ import annotations

import enum
from typing import Optional

from pydantic import BaseModel, Field, validator


class Difficulty(enum.Enum):
    MAKE = "make"
    MAKE_MODEL = "make_model"
    MAKE_MODEL_YEAR = "make_model_year"

    @classmethod
    def from_str(cls, value: str) -> "Difficulty":
        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError(f"지원하지 않는 난이도: {value}") from exc


class CarEntry(BaseModel):
    id: str
    make: str
    model: str
    year: str
    relative_path: str


class QuizOption(BaseModel):
    make: str
    model: Optional[str] = None
    year: Optional[str] = None
    label: str

    @validator("label")
    def _label_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("옵션 라벨은 비어 있을 수 없습니다.")
        return value


class QuestionPayload(BaseModel):
    qid: str
    difficulty: Difficulty
    image_url: str = Field(..., alias="imageUrl")
    prompt: str
    correct: QuizOption
    options: list[QuizOption]
    timeout: int

    class Config:
        allow_population_by_field_name = True


class QuestionAnswer(BaseModel):
    qid: str
    difficulty: Difficulty
    answer: QuizOption
    player: Optional[str] = None
    timeout: bool = False


class AnswerResponse(BaseModel):
    correct: bool
    correct_answer: QuizOption = Field(..., alias="correctAnswer")
    message: str
    score: Optional["PlayerScore"] = None

    class Config:
        allow_population_by_field_name = True


class PlayerScore(BaseModel):
    player: str
    points: int
    streak: int
    total_correct: int
    total_attempts: int

    @property
    def accuracy(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.total_correct / self.total_attempts


class LeaderboardEntry(BaseModel):
    player: str
    points: int
    accuracy: float


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntry]


class LeaderboardReset(BaseModel):
    cleared: int


AnswerResponse.update_forward_refs(PlayerScore=PlayerScore)
