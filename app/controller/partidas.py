from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.database import get_session
from app.models import (
    PartidaCriar, PartidaResposta, PartidaFinalizarSchema, Usuario
)
from app.services.auth import get_usuario_atual, get_admin_atual
from app.services import partida_service

router = APIRouter(prefix="/partidas", tags=["Partidas"])

#USUÁRIO AUTENTICADO
@router.get(
    "/",
    response_model=List[PartidaResposta],
    summary="Listar todas as partidas com odds"
)
def listar(session: Session = Depends(get_session)):
    """Lista todas as partidas com odds calculadas dinamicamente."""
    return partida_service.listar_partidas(session)


@router.get(
    "/ativas",
    response_model=List[PartidaResposta],
    summary="HU8 - Ver partidas disponíveis para apostas"
)
def ativas(session: Session = Depends(get_session)):
    """Lista partidas agendadas onde ainda é possível apostar."""
    return partida_service.listar_partidas_ativas(session)


@router.get(
    "/{id_partida}",
    response_model=PartidaResposta,
    summary="Buscar partida por ID"
)
def buscar(id_partida: int, session: Session = Depends(get_session)):
    """Retorna os dados de uma partida específica com odds."""
    return partida_service.buscar_partida_por_id(id_partida, session)


@router.get(
    "/selecao/{nome}",
    response_model=List[PartidaResposta],
    summary="HU7 - Ver histórico de jogos de uma seleção"
)
def historico_selecao(nome: str, session: Session = Depends(get_session)):
    """
    Retorna os jogos finalizados de uma seleção.
    Busca parcial pelo nome (ex: 'Brasil', 'Argentina').
    """
    return partida_service.buscar_historico_selecao(nome, session)



# ADMIN
@router.post(
    "/",
    response_model=PartidaResposta,
    status_code=status.HTTP_201_CREATED,
    summary="HA4 - Criar partida (admin)"
)
def criar(
    dados: PartidaCriar,
    admin: Usuario = Depends(get_admin_atual),
    session: Session = Depends(get_session)
):
    """Cria uma nova partida manualmente. Requer perfil admin."""
    return partida_service.criar_partida(dados, session)


@router.post(
    "/importar",
    summary="HA4 - Importar partidas da API externa (admin)"
)
def importar(
    admin: Usuario = Depends(get_admin_atual),
    session: Session = Depends(get_session)
):
    """Importa partidas da API worldcup2026.ir. Requer perfil admin."""
    return partida_service.importar_partidas_da_api(session)


@router.patch(
    "/{id_partida}/finalizar",
    summary="Finalizar partida e resolver apostas (admin)"
)
def finalizar(
    id_partida: int,
    dados: PartidaFinalizarSchema,
    admin: Usuario = Depends(get_admin_atual),
    session: Session = Depends(get_session)
):
    """
    Finaliza uma partida, registra o resultado e resolve
    todas as apostas pendentes automaticamente.
    """
    return partida_service.finalizar_partida(id_partida, dados, session)


@router.get(
    "/{id_partida}/apostas",
    summary="HA3/HA5 - Ver apostas de uma partida (admin)"
)
def apostas_da_partida(
    id_partida: int,
    admin: Usuario = Depends(get_admin_atual),
    session: Session = Depends(get_session)
):
    """Retorna todas as apostas de uma partida com odds e totais. Admin only."""
    return partida_service.buscar_apostas_da_partida(id_partida, session)