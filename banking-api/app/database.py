"""Configuração do banco de dados e gerenciamento de sessão SQLAlchemy."""

import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./banking.db")

engine = create_engine(DATABASE_URL, connect_args={})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessão de banco de dados SQLAlchemy.

    Yields:
        Session: Sessão ativa do banco de dados.

    Note:
        A sessão é encerrada automaticamente após o uso.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
