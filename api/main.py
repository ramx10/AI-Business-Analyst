import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routers import upload, schema, clean, dashboard, insights, report

app = FastAPI(
    title="AI Business Analyst API",
    description="Multi-agent business intelligence REST API",
    version="2.0.0",
)

# Allow the frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# Serve the HTML/CSS/JS frontend as static files at the root
WEB_DIR = os.path.join(os.path.dirname(__file__), "..", "web")
if os.path.exists(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
