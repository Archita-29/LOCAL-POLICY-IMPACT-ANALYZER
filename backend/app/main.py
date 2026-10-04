from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router

app = FastAPI(
    title="Local Policy Impact Analyzer API",
    description="API for tracking Indian government schemes and computing model-driven Impact Scores.",
    version="0.1.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API endpoints
app.include_router(api_router, prefix="/api")

# Register RSS scraper endpoints if available
try:
    from scraper.rss.api import rss_router
    app.include_router(rss_router, prefix="/api/scraper")
except ImportError:
    pass

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Local Policy Impact Analyzer API!",
        "status": "healthy",
        "docs_url": "/docs"
    }
