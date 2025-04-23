import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Datajud
DATAJUD_API_URL = os.getenv("DATAJUD_API_URL", "https://api.datajud.cnj.jus.br/api/v1")
DATAJUD_API_KEY = os.getenv(
    "DATAJUD_API_KEY", "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
)
DATAJUD_API_SECRET = os.getenv("DATAJUD_API_SECRET", "")

# Configurações do aplicativo
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt"}


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///crm_advocacia.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações do Datajud
    DATAJUD_API_KEY = os.getenv("DATAJUD_API_KEY", "sua_chave_api_datajud_aqui")
