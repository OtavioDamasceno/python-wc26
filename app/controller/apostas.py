from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.database import get_session
from app.models import (
    ApostaCriar, ApostaMultiplicar, ApostaResposta, Usuario
)
from app.services.auth import get_usuario_atual
from app.services import aposta_service

router = APIRouter(prefix="/apostas", tags=["Apostas"])


@router.post(
    "/",
    response_model=ApostaResposta,
    status_code=status.HTTP_201_CREATED,
    summary="HU2 - Registrar aposta"
)
def criar_aposta(
    dados: ApostaCriar,
    usuario: Usuario = Depends(get_usuario_atual),
    session: Session = Depends(get_session)
):
    """
    Registra uma nova aposta para o usuário autenticado.
    Os pontos são descontados imediatamente do saldo.
    """
    return aposta_service.criar_aposta(dados, usuario, session)


@router.get(
    "/",
    response_model=List[ApostaResposta],
    summary="HU8 - Listar minhas apostas"
)
def listar_apostas(
    usuario: Usuario = Depends(get_usuario_atual),
    session: Session = Depends(get_session)
):
    """Lista todas as apostas do usuário autenticado."""
    return aposta_service.listar_apostas_usuario(usuario, session)


@router.get(
    "/{id_aposta}",
    response_model=ApostaResposta,
    summary="HU3 - Ver status de uma aposta"
)
def ver_aposta(
    id_aposta: int,
    usuario: Usuario = Depends(get_usuario_atual),
    session: Session = Depends(get_session)
):
    """Retorna o status atual de uma aposta específica."""
    return aposta_service.ver_status_aposta(id_aposta, usuario, session)


@router.patch(
    "/{id_aposta}/multiplicar",
    response_model=ApostaResposta,
    summary="HU4 - Multiplicar aposta"
)
def multiplicar_aposta(
    id_aposta: int,
    dados: ApostaMultiplicar,
    usuario: Usuario = Depends(get_usuario_atual),
    session: Session = Depends(get_session)
):
    """
    Multiplica uma aposta pendente (x2, x3, x4, x5...).
    Cobra a diferença de pontos do saldo do usuário.
    """
    return aposta_service.multiplicar_aposta(id_aposta, dados, usuario, session)