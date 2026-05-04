"""FastAPI application entry point for the MDR-TB prototype."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import predict_router
from api.schemas.patient import HealthResponse


APP_VERSION = "0.1.0"


def create_app() -> FastAPI:
    app = FastAPI(
        title="MDR-TB Treatment Outcomes Predictor API",
        version=APP_VERSION,
        description=(
            "Prototype API for MDR-TB treatment outcome risk screening. "
            "Not clinically validated."
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.include_router(predict_router)

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="mdr-tb-treatment-outcomes-api",
            version=APP_VERSION,
        )

    return app


app = create_app()
