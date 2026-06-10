import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from api.routers import upload, schema, clean, dashboard, insights, report, history, nlq, llm_settings, pii, lineage, sharing, scheduler, exports, plugins


class NoCacheMiddleware(BaseHTTPMiddleware):
    """Prevent browser from caching HTML/JS/CSS files during development."""
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        path = request.url.path.lower()
        if path.startswith('/api/') or path.endswith(('.html', '.js', '.css')) or path == '/':
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


app = FastAPI(
    title="AI Business Analyst API",
    description="Multi-agent business intelligence REST API",
    version="2.0.0",
)

# No-cache middleware (must be added before CORS)
app.add_middleware(NoCacheMiddleware)

# Allow the frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8081",
        "http://127.0.0.1:8081"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(schema.router, prefix="/api", tags=["Schema"])
app.include_router(clean.router, prefix="/api", tags=["Cleaning"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(insights.router, prefix="/api", tags=["Insights"])
app.include_router(report.router, prefix="/api", tags=["Report"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(nlq.router, prefix="/api", tags=["Query"])
app.include_router(llm_settings.router, prefix="/api", tags=["LLM Settings"])
app.include_router(pii.router, prefix="/api", tags=["PII"])
app.include_router(lineage.router, prefix="/api", tags=["Lineage"])
app.include_router(sharing.router, prefix="/api", tags=["Sharing"])
app.include_router(scheduler.router, prefix="/api", tags=["Scheduler"])
app.include_router(exports.router, prefix="/api", tags=["Export"])
app.include_router(plugins.router, prefix="/api", tags=["Plugins"])

# Start background scheduler daemon
from api.scheduler_daemon import start_scheduler
start_scheduler(app)

# Serve the HTML/CSS/JS frontend as static files at the root
WEB_DIR = os.path.join(os.path.dirname(__file__), "..", "web")
if os.path.exists(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
