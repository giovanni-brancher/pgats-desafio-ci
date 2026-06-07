"""Router de agências bancárias com endpoints CRUD."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agencia import Agencia
from app.schemas.agencia import AgenciaCreate, AgenciaResponse, AgenciaUpdate

router = APIRouter(prefix="/agencias", tags=["agencias"])

DbDep = Annotated[Session, Depends(get_db)]


@router.get("/")
def list_agencias(
    skip: int = 0,
    limit: int = 100,
    *,
    db: DbDep,
) -> List[AgenciaResponse]:
    """Lista todas as agências bancárias com suporte a paginação.

    Args:
        skip: Número de registros a ignorar (offset). Padrão 0.
        limit: Número máximo de registros a retornar. Padrão 100.
        db: Sessão do banco de dados injetada via dependência.

    Returns:
        Lista de agências bancárias.
    """
    agencias = db.query(Agencia).offset(skip).limit(limit).all()
    return agencias


@router.get("/{agencia_id}")
def get_agencia(
    agencia_id: int,
    *,
    db: DbDep,
) -> AgenciaResponse:
    """Retorna uma agência bancária pelo seu ID.

    Args:
        agencia_id: Identificador único da agência.
        db: Sessão do banco de dados injetada via dependência.

    Returns:
        Dados da agência bancária encontrada.

    Raises:
        HTTPException: 404 se a agência não for encontrada.
    """
    agencia = db.query(Agencia).filter(Agencia.id == agencia_id).first()
    if agencia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agência com id {agencia_id} não encontrada.",
        )
    return agencia


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_agencia(
    agencia: AgenciaCreate,
    *,
    db: DbDep,
) -> AgenciaResponse:
    """Cria uma nova agência bancária.

    Args:
        agencia: Dados da agência a ser criada.
        db: Sessão do banco de dados injetada via dependência.

    Returns:
        Dados da agência bancária recém-criada.

    Raises:
        HTTPException: 409 se o código da agência já estiver cadastrado.
    """
    existing = db.query(Agencia).filter(Agencia.codigo == agencia.codigo).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe uma agência com o código '{agencia.codigo}'.",
        )

    db_agencia = Agencia(**agencia.model_dump())
    db.add(db_agencia)
    db.commit()
    db.refresh(db_agencia)
    return db_agencia


@router.put("/{agencia_id}")
def update_agencia(
    agencia_id: int,
    agencia: AgenciaUpdate,
    *,
    db: DbDep,
) -> AgenciaResponse:
    """Atualiza parcialmente uma agência bancária existente.

    Args:
        agencia_id: Identificador único da agência a ser atualizada.
        agencia: Campos a serem atualizados (apenas os fornecidos são alterados).
        db: Sessão do banco de dados injetada via dependência.

    Returns:
        Dados atualizados da agência bancária.

    Raises:
        HTTPException: 404 se a agência não for encontrada.
    """
    db_agencia = db.query(Agencia).filter(Agencia.id == agencia_id).first()
    if db_agencia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agência com id {agencia_id} não encontrada.",
        )

    update_data = agencia.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_agencia, field, value)

    db.commit()
    db.refresh(db_agencia)
    return db_agencia


@router.delete("/{agencia_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agencia(
    agencia_id: int,
    *,
    db: DbDep,
) -> Response:
    """Remove uma agência bancária pelo seu ID.

    Args:
        agencia_id: Identificador único da agência a ser removida.
        db: Sessão do banco de dados injetada via dependência.

    Returns:
        Resposta vazia com status 204.

    Raises:
        HTTPException: 404 se a agência não for encontrada.
    """
    db_agencia = db.query(Agencia).filter(Agencia.id == agencia_id).first()
    if db_agencia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agência com id {agencia_id} não encontrada.",
        )

    db.delete(db_agencia)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
