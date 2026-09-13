import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api.routes import router as api_router
from backend.services.location_service import location_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown - cleanly restore GPS and close any open tunnels
    await location_service.shutdown()


app = FastAPI(
    title="iPhone Location Simulator API",
    description="Local Windows-first iPhone location simulation service via pymobiledevice3",
    version="1.0.0",
    lifespan=lifespan,
)

# Strictly restrict CORS to localhost / 127.0.0.1
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router)

# Mount frontend static assets
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    # Mount assets directory if it exists
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    async def serve_root():
        return FileResponse(frontend_dist / "index.html")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Serve manifest, service worker, icons, or fallback to index.html for client routing
        target_file = frontend_dist / full_path
        if target_file.exists() and target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(frontend_dist / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
