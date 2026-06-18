from sqlmodel import SQLModel, Field, Relationship # type: ignore[import]
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from models.enums import Palpite, StatusAposta

if TYPE_CHECKING:
    from models.usuario import Usuario
    from models.partida import Partida

class Aposta(SQLModel, table=True):

    __tablename__ = "aposta"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id")
    id_partida: int = Field(foreign_key="partida.id")
    palpite: Palpite
    multiplicador: float = Field(default=1.0)
    pontos_apostados: float
    status: StatusAposta = Field(default=StatusAposta.pendente)
    data_criacao: datetime = Field(default_factory=datetime.utcnow)

    usuario: Optional[Usuario] = Relationship(back_populates="apostas")
    partida: Optional[Partida] = Relationship(back_populates="apostas")