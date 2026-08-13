import os
from sqlalchemy import inspect, text
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

import app.models

# Configurações de Conexão com o MySQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "wc26_apostas")

# Montagem da URL usando o driver pymysql
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)

# Criação do motor do banco de dados (echo=True exibe o SQL gerado no terminal)
engine = create_engine(DATABASE_URL, echo=True)


def reseta_tabelas():
    """
    Reseta todas as tabelas no banco de dados.
    """
    SQLModel.metadata.drop_all(engine)

def criar_tabelas():
    """
    Cria todas as tabelas no banco de dados caso elas não existam.
    Será chamada quando o FastAPI iniciar.
    """
    SQLModel.metadata.create_all(engine)
    _migrar_coluna_odd_registrada()


def _migrar_coluna_odd_registrada():
    """Adiciona a coluna de odd em bancos criados antes dessa regra."""
    inspector = inspect(engine)
    if "aposta" not in inspector.get_table_names():
        return

    colunas = {coluna["name"] for coluna in inspector.get_columns("aposta")}
    if "odd_registrada" not in colunas:
        with engine.begin() as conexao:
            conexao.execute(text("ALTER TABLE aposta ADD COLUMN odd_registrada FLOAT NULL"))


def get_session():
    """
    Gerador de Sessões (Dependência do FastAPI).
    Abre uma conexão limpa por requisição e fecha automaticamente no final.
    """
    with Session(engine) as session:
        yield session
