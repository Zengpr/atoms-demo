from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_tables
from app.routers import auth, projects, chat, preview


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="Atoms Demo - AI Agent Code Generation Platform",
    description="Backend API for an AI agent-driven code generation platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(chat.router)
app.include_router(preview.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "atoms-demo-backend"}


@app.get("/")
async def root():
    return {
        "service": "Atoms Demo Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "frontend": "http://localhost:3000",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
