from app.models.enums import StatusUsuario
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from app.models.aposta import Aposta


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100)
    email: str = Field(max_length=150, unique=True, index=True)
    cpf: str = Field(max_length=14, unique=True, index=True)
    data_nascimento: date
    login: str = Field(max_length=50, unique=True, index=True)
    senha: str = Field(max_length=255)
    pontos: float = Field(default=100.0)
    status: StatusUsuario = Field(default=StatusUsuario.ativo)
    is_adm: bool = Field(default=False)

    apostas: List["Aposta"] = Relationship(back_populates="usuario")