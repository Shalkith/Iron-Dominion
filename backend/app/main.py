"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.game import start_tick_system, stop_tick_system
from app.routes import auth, game, alliances

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("Starting up...")
    await init_db()
    await start_tick_system()
    yield
    # Shutdown
    print("Shutting down...")
    await stop_tick_system()


# Create FastAPI app
app = FastAPI(
    title="War Game API",
    description="Multiplayer strategy war game backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(game.router)
app.include_router(alliances.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "War Game API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/game/status")
async def game_status():
    """Get game tick system status."""
    from app.game import tick_system
    return await tick_system.get_status()
