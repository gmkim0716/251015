from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseSettings, Field, validator


DifficultyStr = Literal["make", "make_model", "make_model_year"]


class AppSettings(BaseSettings):
    """애플리케이션 전역 설정."""

    data_dir: Path = Field(default=Path(__file__).resolve().parent.parent / "data")
    static_url_prefix: str = "/static"
    cars_mount_name: str = "cars"
    timeout_seconds: int = 20
    leaderboard_size: int = 10
    question_store_limit: int = 512
    environment: Literal["development", "production", "test"] = "development"

    class Config:
        env_prefix = "CAR_PICKER_"
        env_file = ".env"
        case_sensitive = False

    @validator("data_dir")
    def _validate_data_dir(cls, value: Path) -> Path:
        if not value.exists():
            raise ValueError(f"데이터 디렉터리를 찾을 수 없습니다: {value}")
        if not value.is_dir():
            raise ValueError(f"data_dir는 디렉터리여야 합니다: {value}")
        return value


@lru_cache()
def get_settings() -> AppSettings:
    return AppSettings()

