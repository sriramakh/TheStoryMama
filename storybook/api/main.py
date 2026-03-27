from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from api.routers import health, stories
from api.routers import library, auth, payments, users
from api.db.engine import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup (graceful if DB unavailable)."""
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Warning: Database not available ({e}). Running in filesystem-only mode.")
    yield


app = FastAPI(
    title="TheStoryMama API",
    description="API for TheStoryMama — AI-generated children's storybooks",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://thestorymama.com",
        "https://www.thestorymama.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing routers
app.include_router(health.router)
app.include_router(stories.router)

# New routers
app.include_router(library.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(payments.router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
