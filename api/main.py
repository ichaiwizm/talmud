"""FastAPI backend for Torah Analysis."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import verses, divine_names, stats, constellation, scroll, voice_chamber, gematria, emotional_topology

app = FastAPI(title="Torah Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(verses.router, prefix="/api/verses", tags=["verses"])
app.include_router(divine_names.router, prefix="/api/divine-names", tags=["divine-names"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(constellation.router, prefix="/api/constellation", tags=["constellation"])
app.include_router(scroll.router, prefix="/api/scroll", tags=["scroll"])
app.include_router(voice_chamber.router, prefix="/api/voice-chamber", tags=["voice-chamber"])
app.include_router(gematria.router, prefix="/api/gematria", tags=["gematria"])
app.include_router(emotional_topology.router, prefix="/api/emotional-topology", tags=["emotional-topology"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
