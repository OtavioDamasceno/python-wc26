from datetime import date, datetime
from typing import List

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import (
    Usuario, StatusUsuario, Aposta, StatusAposta,
    UsuarioCriar, UsuarioResposta, UsuarioAtualizarSenha,
    RankingItem, TokenResposta, LoginSchema
)
from app.services.auth import (
    validar_senha, hash_senha, verificar_senha, criar_token
)


def _calcular_idade(data_nascimento: date) -> int:
    """Retorna a idade em anos completos."""
    hoje = date.today()
    anos = hoje.year - data_nascimento.year
    # Ajuste se ainda não fez aniversário este ano
    if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
        anos -= 1
    return anos


def cadastrar_usuario(dados: UsuarioCriar, session: Session) -> UsuarioResposta:
    """
    Cadastra um novo usuário.

    Validações:
    1. Usuário deve ter 18 anos ou mais
    2. Email único
    3. CPF único
    4. Login único
    5. Senha válida (regras de negócio)
    """
    # Regra: maior de 18 anos
    if _calcular_idade(dados.data_nascimento) < 18:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Somente maiores de 18 anos podem se cadastrar."
        )

    # Unicidade de email
    if session.exec(select(Usuario).where(Usuario.email == dados.email)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado."
        )

    # Unicidade de CPF
    if session.exec(select(Usuario).where(Usuario.cpf == dados.cpf)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF já cadastrado."
        )

    # Unicidade de login
    if session.exec(select(Usuario).where(Usuario.login == dados.login)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Login já em uso."
        )

    # Valida a senha — lança exceção se inválida
    validar_senha(dados.senha)

    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        cpf=dados.cpf,
        data_nascimento=dados.data_nascimento,
        login=dados.login,
        senha=hash_senha(dados.senha),  
        pontos=100.0,                 
        status=StatusUsuario.ativo,
        is_adm=False,
    )

    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)

    return UsuarioResposta.model_validate(novo_usuario)


def login_usuario(dados: LoginSchema, session: Session) -> TokenResposta:
    """
    Autentica o usuário e retorna um token JWT.
    """
    usuario = session.exec(
        select(Usuario).where(Usuario.login == dados.login)
    ).first()

    if not usuario or not verificar_senha(dados.senha, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login ou senha incorretos."
        )

    if usuario.status == StatusUsuario.inativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo."
        )

    token = criar_token({"sub": usuario.login})

    return TokenResposta(
        access_token=token,
        token_type="bearer",
        usuario=UsuarioResposta.model_validate(usuario)
    )


def consultar_saldo(usuario: Usuario) -> dict:
    """
    Retorna o saldo de pontos do usuário.
    Regra: usuário começa com 100 e é excluído se chegar a 0.
    """
    return {
        "usuario": usuario.nome,
        "pontos": usuario.pontos,
        "status": usuario.status
    }


def trocar_senha(
    usuario: Usuario,
    dados: UsuarioAtualizarSenha,
    session: Session
) -> dict:
    """
    Troca a senha do usuário após verificar a senha atual.
    """
    if not verificar_senha(dados.senha_atual, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha atual incorreta."
        )

    validar_senha(dados.nova_senha)

    usuario.senha = hash_senha(dados.nova_senha)
    session.add(usuario)
    session.commit()

    return {"mensagem": "Senha alterada com sucesso."}


def cancelar_participacao(usuario: Usuario, session: Session) -> dict:
    """
    Inativa o usuário (HU5).
    Regra: permanece no ranking mas perde acesso ao sistema.
    """
    usuario.status = StatusUsuario.inativo
    session.add(usuario)
    session.commit()

    return {"mensagem": "Sua participação foi cancelada. Você permanece no ranking."}


def listar_usuarios(session: Session) -> List[UsuarioResposta]:
    """Lista todos os usuários (admin — HA1)."""
    usuarios = session.exec(select(Usuario)).all()
    return [UsuarioResposta.model_validate(u) for u in usuarios]


def buscar_usuario_por_cpf(cpf: str, session: Session) -> UsuarioResposta:
    """Busca usuário pelo CPF (admin — HA2)."""
    usuario = session.exec(
        select(Usuario).where(Usuario.cpf == cpf)
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    return UsuarioResposta.model_validate(usuario)


def ver_ranking(session: Session) -> List[RankingItem]:
    """
    Retorna o ranking de apostadores ordenado por:
    1. Número de acertos (apostas ganhas)
    2. Pontos (desempate)

    Inclui usuários inativos (regra de negócio HU5).
    """
    usuarios = session.exec(select(Usuario)).all()

    ranking = []
    for usuario in usuarios:
        acertos = session.exec(
            select(Aposta).where(
                Aposta.id_usuario == usuario.id,
                Aposta.status == StatusAposta.ganha
            )
        ).all()

        ranking.append({
            "nome": usuario.nome,
            "pontos": usuario.pontos,
            "acertos": len(acertos)
        })

    # Ordena por acertos desc, pontos desc
    ranking.sort(key=lambda x: (-x["acertos"], -x["pontos"]))

    return [
        RankingItem(posicao=i + 1, **item)
        for i, item in enumerate(ranking)
    ]


def verificar_e_excluir_se_zerou(usuario: Usuario, session: Session) -> None:
    """
    Regra de negócio: se o usuário ficou com 0 pontos ou menos, é excluído.
    Chamado após resolver apostas perdidas.
    """
    if usuario.pontos <= 0:
        usuario.pontos = 0
        session.delete(usuario)
        session.commit()