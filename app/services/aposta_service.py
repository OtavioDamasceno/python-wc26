from datetime import datetime
from typing import List
from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import (
    Aposta, Partida, Usuario,
    StatusAposta, StatusPartida,
    ApostaCriar, ApostaMultiplicar, ApostaResposta
)
from app.services.odds import calcular_odd_para_palpite


def _partida_ja_iniciou(data_partida: datetime) -> bool:
    """Compara datas ingênuas e datas com fuso sem misturá-las."""
    agora = datetime.now(data_partida.tzinfo) if data_partida.tzinfo else datetime.utcnow()
    return data_partida <= agora


def criar_aposta(
    dados: ApostaCriar,
    usuario: Usuario,
    session: Session
) -> ApostaResposta:
    """
    Registra uma nova aposta (HU2).

    Regras:
    - Usuário precisa ter pontos suficientes
    - Partida deve estar agendada
    - Pontos são descontados imediatamente
    """
    partida = session.get(Partida, dados.id_partida)
    if not partida:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida não encontrada."
        )

    if partida.status != StatusPartida.agendada or _partida_ja_iniciou(partida.data_partida):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta partida não está disponível para apostas."
        )

    if dados.pontos_apostados <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O valor apostado deve ser maior que zero."
        )

    # Evita que duas requisições simultâneas gastem o mesmo saldo.
    usuario = session.exec(
        select(Usuario).where(Usuario.id == usuario.id).with_for_update()
    ).one()

    if usuario.pontos < dados.pontos_apostados:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Pontos insuficientes. Você tem {usuario.pontos} ponto(s)."
        )

    # Desconta os pontos imediatamente
    usuario.pontos -= dados.pontos_apostados
    session.add(usuario)

    odd_registrada = calcular_odd_para_palpite(dados.palpite, dados.id_partida, session)
    aposta = Aposta(
        id_usuario=usuario.id,
        id_partida=dados.id_partida,
        palpite=dados.palpite,
        multiplicador=1.0,
        pontos_apostados=dados.pontos_apostados,
        odd_registrada=odd_registrada,
        status=StatusAposta.pendente,
    )

    session.add(aposta)
    session.commit()
    session.refresh(aposta)

    return ApostaResposta.model_validate(aposta)


def multiplicar_aposta(
    id_aposta: int,
    dados: ApostaMultiplicar,
    usuario: Usuario,
    session: Session
) -> ApostaResposta:
    """
    Multiplica uma aposta existente (HU4).

    Regras:
    - Usuário deve ser dono da aposta
    - Aposta deve estar pendente
    - Multiplicador mínimo: 2, sem limite máximo
    - Custo adicional = pontos_apostados * (novo_mult - mult_atual)
    """
    aposta = session.get(Aposta, id_aposta)

    if not aposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aposta não encontrada."
        )

    if aposta.id_usuario != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para modificar esta aposta."
        )

    if aposta.status != StatusAposta.pendente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Só é possível multiplicar apostas pendentes."
        )

    partida = session.get(Partida, aposta.id_partida)
    if not partida or partida.status != StatusPartida.agendada or _partida_ja_iniciou(partida.data_partida):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta partida não está mais disponível para apostas."
        )

    if dados.multiplicador < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O multiplicador mínimo é 2."
        )

    if dados.multiplicador <= aposta.multiplicador:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"O novo multiplicador deve ser maior que o atual ({int(aposta.multiplicador)}x)."
        )

    # Custo = pontos apostados * diferença entre multiplicadores
    diferenca = dados.multiplicador - aposta.multiplicador
    custo_adicional = aposta.pontos_apostados * diferenca

    usuario = session.exec(
        select(Usuario).where(Usuario.id == usuario.id).with_for_update()
    ).one()

    if usuario.pontos < custo_adicional:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Pontos insuficientes. Você precisa de {custo_adicional} ponto(s) adicionais."
        )

    usuario.pontos -= custo_adicional
    aposta.multiplicador = dados.multiplicador

    session.add(usuario)
    session.add(aposta)
    session.commit()
    session.refresh(aposta)

    return ApostaResposta.model_validate(aposta)


def listar_apostas_usuario(usuario: Usuario, session: Session) -> List[ApostaResposta]:
    """Lista todas as apostas do usuário autenticado (HU8)."""
    apostas = session.exec(
        select(Aposta).where(Aposta.id_usuario == usuario.id)
    ).all()

    return [ApostaResposta.model_validate(a) for a in apostas]


def ver_status_aposta(
    id_aposta: int,
    usuario: Usuario,
    session: Session
) -> ApostaResposta:
    """Retorna o status de uma aposta específica (HU3)."""
    aposta = session.get(Aposta, id_aposta)

    if not aposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aposta não encontrada."
        )

    if aposta.id_usuario != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a esta aposta."
        )

    return ApostaResposta.model_validate(aposta)
