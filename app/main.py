from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import Base, engine
from app.routes import auth, connections, collections, items, sync

# Crear tablas
Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(connections.router)
app.include_router(collections.router)
app.include_router(items.router)
app.include_router(sync.router)

@app.get("/", tags=["health"])
def read_root():
    return {
        "message": "Share Links API",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}