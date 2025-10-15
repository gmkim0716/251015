from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .indexer import CarDataset
from .routes import router as api_router
from .score import ScoreBoard
from .settings import get_settings
from .store import QuestionStore

LOGGER = logging.getLogger("car_picker.app")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title="Car Picker Quiz", version="1.0.0")

    static_root = Path(__file__).resolve().parent.parent / "static"
    templates_root = Path(__file__).resolve().parent.parent / "templates"
    templates_root.mkdir(parents=True, exist_ok=True)

    app.mount(
        f"{settings.static_url_prefix}/assets",
        StaticFiles(directory=str(static_root)),
        name="assets",
    )
    app.mount(
        f"{settings.static_url_prefix}/{settings.cars_mount_name}",
        StaticFiles(directory=str(settings.data_dir)),
        name=settings.cars_mount_name,
    )

    templates = Jinja2Templates(directory=str(templates_root))

    @app.on_event("startup")
    async def startup_event() -> None:
        LOGGER.info("Application startup - loading dataset")
        dataset = CarDataset(settings.data_dir)
        app.state.dataset = dataset
        app.state.scoreboard = ScoreBoard(settings.leaderboard_size)
        app.state.question_store = QuestionStore(limit=settings.question_store_limit)
        app.state.templates = templates

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    app.include_router(api_router)

    return app


app = create_app()
