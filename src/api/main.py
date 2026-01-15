"""FastAPI application for Torah Analysis API."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db.base import init_db
from src.api.routers import books, names, search, gematria, stats, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    init_db()
    yield


app = FastAPI(
    title="Torah Analysis API",
    description="REST API for Torah text analysis, name extraction, and gematria calculations",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(books.router, prefix="/api/v1")
app.include_router(names.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(gematria.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "name": "Torah Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "books": "/api/v1/books",
            "names": "/api/v1/names",
            "search": "/api/v1/search",
            "gematria": "/api/v1/gematria",
            "stats": "/api/v1/stats",
            "admin": "/api/v1/admin",
        }
    }


@app.get("/api/v1")
def api_root():
    """API v1 root."""
    return {"version": "1.0.0", "status": "active"}
