from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, status

from .models import (
    AnswerResponse,
    Difficulty,
    LeaderboardResponse,
    LeaderboardReset,
    QuestionAnswer,
    QuestionPayload,
    QuizOption,
)
from .sampler import build_question
from .settings import get_settings


router = APIRouter(prefix="/api", tags=["quiz"])


def _get_dataset(request: Request):
    dataset = getattr(request.app.state, "dataset", None)
    if dataset is None:
        raise RuntimeError("Dataset is not initialized.")
    return dataset


def _get_store(request: Request):
    store = getattr(request.app.state, "question_store", None)
    if store is None:
        raise RuntimeError("Question store is not initialized.")
    return store


def _get_scoreboard(request: Request):
    scoreboard = getattr(request.app.state, "scoreboard", None)
    if scoreboard is None:
        raise RuntimeError("Scoreboard is not initialized.")
    return scoreboard


@router.get("/question", response_model=QuestionPayload)
def get_question(
    request: Request,
    difficulty: str = Query("make_model_year"),
    exclude: Optional[List[str]] = Query(default=None),
    timer: Optional[int] = Query(default=None, ge=10, le=60),
):
    settings = get_settings()
    dataset = _get_dataset(request)
    store = _get_store(request)

    try:
        difficulty_enum = Difficulty.from_str(difficulty)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    exclude_ids = set(exclude or [])

    try:
        entry, correct_option, options = build_question(dataset, difficulty_enum, exclude_ids)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    stored = store.issue(difficulty=difficulty_enum, correct=correct_option)

    image_url = f"{settings.static_url_prefix}/{settings.cars_mount_name}/{entry.relative_path}"
    timeout_value = timer if timer is not None else settings.timeout_seconds

    return QuestionPayload(
        qid=stored.qid,
        difficulty=difficulty_enum,
        imageUrl=image_url,
        prompt="Guess the vehicle information.",
        correct=correct_option,
        options=options,
        timeout=timeout_value,
    )


@router.post("/answer", response_model=AnswerResponse)
def submit_answer(request: Request, payload: QuestionAnswer):
    store = _get_store(request)
    scoreboard = _get_scoreboard(request)

    stored = store.resolve(payload.qid)
    if stored is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid question id.")

    if stored.difficulty != payload.difficulty:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Difficulty mismatch.")

    is_correct = False
    correct_option = stored.correct

    if not payload.timeout:
        is_correct = _check_answer(correct_option, payload.answer, stored.difficulty)

    message = "Timed out." if payload.timeout else ("Correct." if is_correct else "Incorrect.")

    score_model = None
    if payload.player:
        record = scoreboard.register_attempt(payload.player, stored.difficulty, is_correct)
        score_model = record.to_model()

    return AnswerResponse(
        correct=is_correct,
        correctAnswer=correct_option,
        message=message,
        score=score_model,
    )


def _check_answer(correct: QuizOption, answer: QuizOption, difficulty: Difficulty) -> bool:
    if difficulty is Difficulty.MAKE:
        return correct.make.lower() == (answer.make or "").lower()
    if difficulty is Difficulty.MAKE_MODEL:
        return (
            correct.make.lower() == (answer.make or "").lower()
            and (correct.model or "").lower() == (answer.model or "").lower()
        )
    return (
        correct.make.lower() == (answer.make or "").lower()
        and (correct.model or "").lower() == (answer.model or "").lower()
        and (correct.year or "").lower() == (answer.year or "").lower()
    )


@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(request: Request):
    scoreboard = _get_scoreboard(request)
    entries = scoreboard.top_entries()
    return LeaderboardResponse(entries=entries)


@router.post("/leaderboard/reset", response_model=LeaderboardReset)
def reset_leaderboard(request: Request):
    scoreboard = _get_scoreboard(request)
    cleared = scoreboard.reset()
    return LeaderboardReset(cleared=cleared)
