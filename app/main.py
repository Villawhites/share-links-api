from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models import User, Connection, Collection, Item
from app.routes import auth, connections, collections, items, sync

@asynccontextmanager
async def lifespan(app):
    # Startup: crear tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: cerrar conexiones
    await engine.dispose()

app = FastAPI(
    title="Share Links API",
    description="API para compartir y sincronizar enlaces",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(connections.router, prefix="/api/connections", tags=["connections"])
app.include_router(collections.router, prefix="/api/collections", tags=["collections"])
app.include_router(items.router, prefix="/api/items", tags=["items"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])

@app.get("/")
async def root():
    return {
        "message": "Share Links API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)