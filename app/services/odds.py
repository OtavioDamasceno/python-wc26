from typing import Dict
from sqlmodel import Session, select, func

from app.models import Aposta, Palpite, StatusAposta


def calcular_odds(id_partida: int, session: Session) -> Dict[str, float]:
    """
    Calcula as ODDs dinâmicas de uma partida com base nas apostas pendentes.

    Retorna um dicionário com as odds para cada resultado:
    {
        "time_a": float,
        "time_b": float,
        "empate": float,
        "total_apostadores": int
    }
    """
    # Conta apostadores por palpite (apenas apostas pendentes)
    apostas = session.exec(
        select(Aposta).where(
            Aposta.id_partida == id_partida,
            Aposta.status == StatusAposta.pendente
        )
    ).all()

    contagem = {
        Palpite.time_a: 0,
        Palpite.time_b: 0,
        Palpite.empate: 0,
    }

    for aposta in apostas:
        contagem[aposta.palpite] += 1

    total = sum(contagem.values())

    def calcular_odd(apostadores_lado: int, apostadores_outros: int) -> float:
        """
        ODD = 1 + (outros / lado)
        Se não há apostadores no lado, retorna ODD padrão de 2.0.
        """
        if apostadores_lado == 0:
            return 2.0
        return round(1 + (apostadores_outros / apostadores_lado), 2)

    qt_a = contagem[Palpite.time_a]
    qt_b = contagem[Palpite.time_b]
    qt_e = contagem[Palpite.empate]

    return {
        "time_a": calcular_odd(qt_a, qt_b + qt_e),
        "time_b": calcular_odd(qt_b, qt_a + qt_e),
        "empate": calcular_odd(qt_e, qt_a + qt_b),
        "total_apostadores": total,
        "apostadores_time_a": qt_a,
        "apostadores_time_b": qt_b,
        "apostadores_empate": qt_e,
    }


def calcular_odd_para_palpite(
    palpite: Palpite,
    id_partida: int,
    session: Session
) -> float:
    """
    Retorna a ODD atual para um palpite específico.
    Usado no momento de registrar uma aposta.
    """
    odds = calcular_odds(id_partida, session)

    mapa = {
        Palpite.time_a: odds["time_a"],
        Palpite.time_b: odds["time_b"],
        Palpite.empate: odds["empate"],
    }
    return mapa[palpite]