import os
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.database import get_session
from app.models import Usuario, StatusUsuario

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY deve ser configurada no ambiente.")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# bcrypt 5.x é incompatível com a checagem interna do passlib 1.7.4 e faz o
# cadastro retornar 500. Novas senhas usam PBKDF2-SHA256; bcrypt continua
# aceito para permitir login de contas criadas antes desta alteração.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    default="pbkdf2_sha256",
    deprecated="auto",
)

# HTTPBearer — campo Swagger 
bearer_scheme = HTTPBearer()


# Funções de senha
def validar_senha(senha: str) -> None:
    erros = []

    if len(senha) < 8:
        erros.append("A senha deve ter no mínimo 8 caracteres.")
    if not re.search(r"[A-Z]", senha):
        erros.append("A senha deve conter pelo menos uma letra maiúscula.")
    if not re.search(r"[a-z]", senha):
        erros.append("A senha deve conter pelo menos uma letra minúscula.")
    if not re.search(r"\d", senha):
        erros.append("A senha deve conter pelo menos um número.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        erros.append("A senha deve conter pelo menos um caractere especial.")

    if erros:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=erros
        )


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plain, senha_hash)

# Funções JWT
def criar_token(data: dict) -> str:
    payload = data.copy()
    expira = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expira})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        return login
    except JWTError:
        return None


# Dependências FastAPI
def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session)
) -> Usuario:
    """
    Dependência para rotas protegidas.
    Lê o token do header Authorization: Bearer <token>
    """
    credencial_erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    login = decodificar_token(token)
    if not login:
        raise credencial_erro

    usuario = session.exec(
        select(Usuario).where(Usuario.login == login)
    ).first()

    if not usuario:
        raise credencial_erro

    if usuario.status == StatusUsuario.inativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Acesso negado."
        )

    return usuario


def get_admin_atual(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
    if not usuario.is_adm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores."
        )
    return usuario
