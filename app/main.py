from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import auth, connections, collections, items, sync
from app.middleware.error_handler import register_exception_handlers
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Inicializar app
app = FastAPI(
    title="Share Links API",
    description="API para compartir enlaces",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar manejadores de excepciones
register_exception_handlers(app)

# Rutas
app.include_router(auth.router)
app.include_router(connections.router)
app.include_router(collections.router)
app.include_router(items.router)
app.include_router(sync.router)

@app.get("/", tags=["health"])
def read_root():
    return {"message": "Share Links API v1.0"}

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy"}