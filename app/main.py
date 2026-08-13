import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from app.database import criar_tabelas
from app.controller.usuarios import router_auth, router_usuarios
from app.controller.partidas import router as router_partidas
from app.controller.apostas import router as router_apostas

# Esquema de segurança Bearer — "Authorize"
bearer_scheme = HTTPBearer()

app = FastAPI(
    title="Sistema de Apostas — Copa do Mundo 2026",
    description=(
        "API para o sistema de apostas nos jogos da Copa do Mundo 2026. "
        "Desenvolvido com FastAPI + SQLModel + MySQL."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

CORS_ORIGINS = [
    origem.strip()
    for origem in os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")
    if origem.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_auth)
app.include_router(router_usuarios)
app.include_router(router_partidas)
app.include_router(router_apostas)


@app.on_event("startup")
def on_startup():
    criar_tabelas()
    print("✅ Tabelas criadas/verificadas com sucesso.")


@app.get("/", tags=["Status"])
def root():
    return {
        "status": "online",
        "app": "Sistema de Apostas WC26",
        "docs": "/docs"
    }
