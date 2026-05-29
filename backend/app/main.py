from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import health, chat

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Backend for the Agentic Real Estate platform."
    )

    # Configure CORS so the React frontend can talk to this API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Change this to your frontend URL in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register the routers
    app.include_router(health.router)
    app.include_router(chat.router, prefix="/api/v1")

    return app

app = create_app()

