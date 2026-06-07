"""Ponto de entrada da aplicação FastAPI Banking API."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import agencias


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicação FastAPI.

    Cria todas as tabelas no banco de dados na inicialização e libera
    recursos ao encerrar.

    Args:
        app: Instância da aplicação FastAPI.

    Yields:
        None: Controle retorna à aplicação durante sua execução.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Banking API",
    description="API REST para gerenciamento de agências bancárias.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(agencias.router)


@app.get("/")
def root() -> Dict[str, str]:
    """Endpoint raiz da aplicação.

    Returns:
        Mensagem de status e link para a documentação interativa.
    """
    return {"message": "Banking API está no ar", "docs": "/docs"}
