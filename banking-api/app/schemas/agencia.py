"""Schemas Pydantic para validação e serialização de Agência Bancária."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AgenciaBase(BaseModel):
    """Schema base com campos comuns de Agência Bancária."""

    model_config = ConfigDict(from_attributes=True)

    nome: str
    codigo: str
    endereco: str
    cidade: str
    estado: str
    telefone: Optional[str] = None


class AgenciaCreate(AgenciaBase):
    """Schema para criação de uma nova agência bancária."""


class AgenciaUpdate(BaseModel):
    """Schema para atualização parcial de uma agência bancária. Todos os campos são opcionais."""

    model_config = ConfigDict(from_attributes=True)

    nome: Optional[str] = None
    codigo: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    telefone: Optional[str] = None


class AgenciaResponse(AgenciaBase):
    """Schema de resposta com todos os campos de uma agência bancária."""

    id: int
    created_at: datetime
