"""Fixtures compartilhadas para os testes da Banking API."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app.main import app
from app.database import Base, get_db

engine_test = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    """Gera uma sessão de banco de dados de teste.

    Yields:
        Session: Sessão SQLAlchemy conectada ao banco de dados de teste.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Cria todas as tabelas antes do teste e as remove após.

    Yields:
        Session: Sessão SQLAlchemy com as tabelas criadas para o teste.
    """
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db_session):
    """Cria um TestClient com a dependência get_db substituída pelo banco de teste.

    Args:
        db_session: Sessão de banco de dados de teste provida pela fixture db_session.

    Yields:
        TestClient: Cliente HTTP configurado para a aplicação FastAPI de teste.
    """
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def agencia_data():
    """Retorna dados de exemplo para criação de uma agência de teste.

    Returns:
        dict: Dicionário com campos válidos para criação de uma Agencia.
    """
    return {
        "nome": "Agência Central",
        "codigo": "AG001",
        "endereco": "Rua das Flores, 100",
        "cidade": "São Paulo",
        "estado": "SP",
        "telefone": "11999999999",
    }
