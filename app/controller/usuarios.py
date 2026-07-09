from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.database import get_session
from app.models import (
    UsuarioCriar, UsuarioResposta, UsuarioAtualizarSenha,
    RankingItem, TokenResposta, LoginSchema, Usuario
)
from app.services.auth import get_usuario_atual, get_admin_atual
from app.services import usuario_service

#Roteadores 
router_auth = APIRouter(prefix="/auth", tags=["Autenticação"])
router_usuarios = APIRouter(prefix="/usuarios", tags=["Usuários"])


# AUTH
@router_auth.post(
    "/cadastro",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="HU1 - Criar conta"
)
def cadastrar(dados: UsuarioCriar, session: Session = Depends(get_session)):
    """
    Cria uma nova conta de usuário.
    - Deve ter 18 anos ou mais
    - Começa com 100 pontos
    - Senha: 8+ chars, maiúscula, minúscula, número, especial
    """
    return usuario_service.cadastrar_usuario(dados, session)


@router_auth.post(
    "/login",
    response_model=TokenResposta,
    summary="Login — obtém token JWT"
)
def login(dados: LoginSchema, session: Session = Depends(get_session)):
    """Autentica e retorna o token JWT para usar nas rotas protegidas."""
    return usuario_service.login_usuario(dados, session)


# USUÁRIO AUTENTICADO
@router_usuarios.get(
    "/saldo",
    summary="HU9 - Consultar saldo de pontos"
)
def saldo(usuario: Usuario = Depends(get_usuario_atual)):
    """Retorna os pontos atuais do usuário autenticado."""
    return usuario_service.consultar_saldo(usuario)


@router_usuarios.put(
    "/senha",
    summary="HU6 - Trocar senha"
)
def trocar_senha(
    dados: UsuarioAtualizarSenha,
    usuario: Usuario = Depends(get_usuario_atual),
    session: Session = Depends(get_session)
):
    """Troca a senha do usuário após verificar a senha atual."""
    return usuario_service.trocar_senha(usuario, dados, session)


@router_usuarios.delete(
    "/cancelar",
    summary="HU5 - Cancelar participação"
)
def cancelar(
    usuario: Usuario = Depends(get_usuario_atual),
    session: Session = Depends(get_session)
):
    """
    Inativa o usuário no sistema.
    O usuário permanece no ranking mas perde acesso.
    """
    return usuario_service.cancelar_participacao(usuario, session)


@router_usuarios.get(
    "/ranking",
    response_model=List[RankingItem],
    summary="HU10 - Ver ranking de apostadores"
)
def ranking(session: Session = Depends(get_session)):
    """Ranking público ordenado por acertos e pontos."""
    return usuario_service.ver_ranking(session)


# ADMIN
@router_usuarios.get(
    "/",
    response_model=List[UsuarioResposta],
    summary="HA1 - Listar todos os usuários (admin)"
)
def listar(admin: Usuario = Depends(get_admin_atual), session: Session = Depends(get_session)):
    """Lista todos os usuários cadastrados. Requer perfil admin."""
    return usuario_service.listar_usuarios(session)


@router_usuarios.get(
    "/cpf/{cpf}",
    response_model=UsuarioResposta,
    summary="HA2 - Buscar usuário por CPF (admin)"
)
def buscar_cpf(
    cpf: str,
    admin: Usuario = Depends(get_admin_atual),
    session: Session = Depends(get_session)
):
    """Busca um usuário pelo CPF. Requer perfil admin."""
    return usuario_service.buscar_usuario_por_cpf(cpf, session)