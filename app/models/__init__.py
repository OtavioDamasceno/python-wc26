# app/models/__init__.py
from app.models.enums import (
    StatusUsuario,
    StatusAposta,
    StatusPartida,
    Palpite,
    ResultadoPartida,
)

from app.models.usuario import Usuario
from app.models.partida import Partida
from app.models.aposta import Aposta

#entrada/saída da API
from datetime import date, datetime
from typing import Optional, List
from sqlmodel import SQLModel


class UsuarioCriar(SQLModel):
    """Schema para criação de novo usuário (POST /auth/cadastro)."""
    nome: str
    email: str
    cpf: str
    data_nascimento: date
    login: str
    senha: str


class UsuarioResposta(SQLModel):
    """Schema de resposta — nunca expõe a senha."""
    id: int
    nome: str
    email: str
    cpf: str
    login: str
    pontos: float
    status: StatusUsuario
    is_adm: bool

    model_config = {"from_attributes": True}


class UsuarioAtualizarSenha(SQLModel):
    """Schema para troca de senha."""
    senha_atual: str
    nova_senha: str


class PartidaCriar(SQLModel):
    """Schema para criação de partida (admin)."""
    time_a: str
    time_b: str
    data_partida: datetime


class PartidaResposta(SQLModel):
    """Schema de resposta de partida com odds calculadas."""
    id: int
    time_a: str
    time_b: str
    data_partida: datetime
    resultado: Optional[ResultadoPartida] = None
    status: StatusPartida
    odd_time_a: Optional[float] = None
    odd_time_b: Optional[float] = None
    odd_empate: Optional[float] = None
    total_apostadores: Optional[int] = None

    model_config = {"from_attributes": True}


class PartidaFinalizarSchema(SQLModel):
    """Schema para finalizar uma partida (admin)."""
    resultado: ResultadoPartida


class ApostaCriar(SQLModel):
    """Schema para criação de aposta."""
    id_partida: int
    palpite: Palpite
    pontos_apostados: float


class ApostaMultiplicar(SQLModel):
    """Schema para multiplicar uma aposta existente."""
    multiplicador: int  


class ApostaResposta(SQLModel):
    """Schema de resposta de aposta."""
    id: int
    id_partida: int
    palpite: Palpite
    multiplicador: float
    pontos_apostados: float
    status: StatusAposta
    data_criacao: datetime

    model_config = {"from_attributes": True}


class LoginSchema(SQLModel):
    """Schema para autenticação."""
    login: str
    senha: str


class TokenResposta(SQLModel):
    """Schema de resposta do token JWT."""
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResposta


class RankingItem(SQLModel):
    """Item do ranking de apostadores."""
    posicao: int
    nome: str
    pontos: float
    acertos: int