from sqlmodel import SQLModel, Field, Relationship  # type: ignore[import]
from typing import Optional, List, TYPE_CHECKING
from models.enums import StatusPartida, ResultadoPartida
from datetime import datetime

if TYPE_CHECKING:
    from models.aposta import Aposta


class Partida(SQLModel, table=True):
    __tablename__ = "partida"

    id: Optional[int] = Field(default=None, primary_key=True)
    time_a: str = Field(max_length=100)
    time_b: str = Field(max_length=100)
    data_partida: datetime
    resultado: Optional[ResultadoPartida] = Field(default=None)
    status: StatusPartida = Field(default=StatusPartida.agendada)

    apostas: List["Aposta"] = Relationship(back_populates="partida")
