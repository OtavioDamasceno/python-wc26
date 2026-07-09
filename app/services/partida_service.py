import os
from typing import List, Optional
from datetime import datetime

import httpx
from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import (
    Partida, Aposta, Usuario, StatusPartida, StatusAposta,
    ResultadoPartida, Palpite, PartidaCriar, PartidaResposta,
    PartidaFinalizarSchema
)
from app.services.odds import calcular_odds
from app.services.usuario_service import verificar_e_excluir_se_zerou


# Configuração da API Externa (.env)
FOOTBALL_API_URL = os.getenv("FOOTBALL_API_URL", "https://worldcup26.ir/get/games")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")


# Criar / Importar partidas
def criar_partida(dados: PartidaCriar, session: Session) -> PartidaResposta:
    """Cria uma partida manualmente (admin — HA4)."""
    partida = Partida(
        time_a=dados.time_a,
        time_b=dados.time_b,
        data_partida=dados.data_partida,
        status=StatusPartida.agendada
    )
    session.add(partida)
    session.commit()
    session.refresh(partida)

    return _partida_para_resposta(partida, session)


def importar_partidas_da_api(session: Session) -> dict:
    """
    Importa partidas da API externa worldcup2026.ir (admin — HA4).
    Ignora partidas já existentes (verifica time_a + time_b + data).
    """
    try:
        # Prepara os headers com o Token JWT se ele existir no .env
        headers = {}
        if FOOTBALL_API_KEY and FOOTBALL_API_KEY != "sua_chave_api_aqui":
            headers["Authorization"] = f"Bearer {FOOTBALL_API_KEY}"

        response = httpx.get(FOOTBALL_API_URL, headers=headers, timeout=10.0)
        response.raise_for_status()
        jogos = response.json()
        
        # O retorno da API para partidas fica dentro da chave "games"
        lista_jogos = jogos.get("games", [])
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao acessar API externa: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado: {str(e)}"
        )

    importadas = 0
    ignoradas = 0

    for jogo in lista_jogos:
        try:
            # Pega os nomes em inglês e a data da API
            time_a = jogo.get("home_team_name_en")
            time_b = jogo.get("away_team_name_en")
            data_str = jogo.get("local_date")

            if not time_a or not time_b or not data_str:
                ignoradas += 1
                continue

            # Data formato "MM/DD/YYYY HH:MM"
            try:
                data_partida = datetime.strptime(data_str, "%m/%d/%Y %H:%M")
            except ValueError:
                # Caso venha em outro formato inesperado
                ignoradas += 1
                continue

            # Verifica se já existe
            existe = session.exec(
                select(Partida).where(
                    Partida.time_a == time_a,
                    Partida.time_b == time_b,
                    Partida.data_partida == data_partida
                )
            ).first()

            if existe:
                ignoradas += 1
                continue

            partida = Partida(
                time_a=time_a,
                time_b=time_b,
                data_partida=data_partida,
                status=StatusPartida.agendada
            )
            session.add(partida)
            importadas += 1

        except Exception:
            ignoradas += 1
            continue

    session.commit()

    return {
        "mensagem": f"{importadas} partida(s) importada(s), {ignoradas} ignorada(s).",
        "importadas": importadas,
        "ignoradas": ignoradas
    }


# Consultas
def listar_partidas(session: Session) -> List[PartidaResposta]:
    """Lista todas as partidas com odds calculadas."""
    partidas = session.exec(select(Partida)).all()
    return [_partida_para_resposta(p, session) for p in partidas]


def listar_partidas_ativas(session: Session) -> List[PartidaResposta]:
    """
    Lista partidas disponíveis para apostas (agendadas).
    Usado em HU8 — ver apostas ativas.
    """
    partidas = session.exec(
        select(Partida).where(Partida.status == StatusPartida.agendada)
    ).all()
    return [_partida_para_resposta(p, session) for p in partidas]


def buscar_partida_por_id(id_partida: int, session: Session) -> PartidaResposta:
    """Busca partida pelo ID."""
    partida = _get_partida_ou_404(id_partida, session)
    return _partida_para_resposta(partida, session)


def buscar_historico_selecao(nome_selecao: str, session: Session) -> List[PartidaResposta]:
    """
    Retorna jogos anteriores de uma determinada seleção (HU7).
    Busca tanto como time_a quanto como time_b.
    """
    partidas = session.exec(
        select(Partida).where(
            Partida.status == StatusPartida.finalizada
        ).where(
            (Partida.time_a.ilike(f"%{nome_selecao}%")) |
            (Partida.time_b.ilike(f"%{nome_selecao}%"))
        )
    ).all()

    return [_partida_para_resposta(p, session) for p in partidas]


def buscar_apostas_da_partida(id_partida: int, session: Session) -> dict:
    """
    Retorna dados detalhados das apostas de uma partida (admin — HA3/HA5).
    """
    partida = _get_partida_ou_404(id_partida, session)
    odds_info = calcular_odds(id_partida, session)

    apostas = session.exec(
        select(Aposta).where(Aposta.id_partida == id_partida)
    ).all()

    return {
        "partida": {
            "id": partida.id,
            "time_a": partida.time_a,
            "time_b": partida.time_b,
            "data_partida": partida.data_partida,
            "status": partida.status,
            "resultado": partida.resultado
        },
        "odds": odds_info,
        "total_apostas": len(apostas),
        "apostas": [
            {
                "id": a.id,
                "id_usuario": a.id_usuario,
                "palpite": a.palpite,
                "pontos_apostados": a.pontos_apostados,
                "multiplicador": a.multiplicador,
                "status": a.status
            }
            for a in apostas
        ]
    }


# Finalizar partida e resolver apostas
def finalizar_partida(
    id_partida: int,
    dados: PartidaFinalizarSchema,
    session: Session
) -> dict:
    """
    Finaliza uma partida e resolve todas as apostas pendentes.

    Regras:
    - Vitória: ganhador recebe pontos_apostados * odd
    - Derrota: perde os pontos apostados
    - Empate: pontos devolvidos, ranking inalterado
    - Se usuário ficar com 0 pontos: é excluído
    """
    partida = _get_partida_ou_404(id_partida, session)

    if partida.status == StatusPartida.finalizada:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta partida já foi finalizada."
        )

    # Captura as odds ANTES de finalizar
    odds_snapshot = calcular_odds(id_partida, session)

    # Atualiza a partida
    partida.resultado = dados.resultado
    partida.status = StatusPartida.finalizada
    session.add(partida)

    # Busca todas as apostas pendentes desta partida
    apostas = session.exec(
        select(Aposta).where(
            Aposta.id_partida == id_partida,
            Aposta.status == StatusAposta.pendente
        )
    ).all()

    resolvidas = {"ganhas": 0, "perdidas": 0, "devolvidas": 0}

    for aposta in apostas:
        usuario = session.get(Usuario, aposta.id_usuario)
        if not usuario:
            continue

        if dados.resultado == ResultadoPartida.empate:
            # Devolve os pontos apostados
            usuario.pontos += aposta.pontos_apostados
            aposta.status = StatusAposta.devolvida
            resolvidas["devolvidas"] += 1

        elif aposta.palpite.value == dados.resultado.value:
            # Acertou! Calcula o ganho com base na odd do palpite
            mapa_odd = {
                Palpite.time_a: odds_snapshot["time_a"],
                Palpite.time_b: odds_snapshot["time_b"],
                Palpite.empate: odds_snapshot["empate"],
            }
            odd = mapa_odd.get(aposta.palpite, 1.0)
            ganho = round(aposta.pontos_apostados * aposta.multiplicador * odd, 2)
            usuario.pontos += ganho
            aposta.status = StatusAposta.ganha
            resolvidas["ganhas"] += 1

        else:
            # Errou — pontos já foram descontados no momento da aposta
            aposta.status = StatusAposta.perdida
            resolvidas["perdidas"] += 1

            # Verifica se deve ser excluído (pontos zerados)
            verificar_e_excluir_se_zerou(usuario, session)

        session.add(aposta)
        if session.get(Usuario, aposta.id_usuario):  # Usuário ainda existe?
            session.add(usuario)

    session.commit()

    return {
        "mensagem": f"Partida finalizada. Resultado: {dados.resultado.value}",
        "apostas_resolvidas": resolvidas
    }


# Helpers internos
def _get_partida_ou_404(id_partida: int, session: Session) -> Partida:
    """Busca partida ou lança 404."""
    partida = session.get(Partida, id_partida)
    if not partida:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida não encontrada."
        )
    return partida


def _partida_para_resposta(partida: Partida, session: Session) -> PartidaResposta:
    """Converte Partida para PartidaResposta com odds calculadas."""
    odds_info = calcular_odds(partida.id, session)

    return PartidaResposta(
        id=partida.id,
        time_a=partida.time_a,
        time_b=partida.time_b,
        data_partida=partida.data_partida,
        resultado=partida.resultado,
        status=partida.status,
        odd_time_a=odds_info["time_a"],
        odd_time_b=odds_info["time_b"],
        odd_empate=odds_info["empate"],
        total_apostadores=odds_info["total_apostadores"],
    )