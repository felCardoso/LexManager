from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    oab = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='advogado')  # admin ou advogado
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    clientes = db.relationship("Cliente", backref="advogado", lazy=True)
    processos = db.relationship("Processo", backref="advogado", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    advogado_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    processos = db.relationship("Processo", backref="cliente", lazy=True)

    def __repr__(self):
        return f"<Cliente {self.nome}>"


class Processo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_processo = db.Column(db.String(50), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    advogado_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50))
    descricao = db.Column(db.Text)
    tribunal = db.Column(db.String(100))
    vara = db.Column(db.String(100))
    classe = db.Column(db.String(100))
    assunto = db.Column(db.String(200))
    valor_causa = db.Column(db.Float)
    ultima_atualizacao = db.Column(db.DateTime)
    audiencias = db.relationship("Audiencia", backref="processo", lazy=True)
    documentos = db.relationship("Documento", backref="processo", lazy=True)
    honorarios = db.relationship("Honorario", backref="processo", lazy=True)

    def __repr__(self):
        return f"<Processo {self.numero_processo}>"


class Audiencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    processo_id = db.Column(db.Integer, db.ForeignKey("processo.id"), nullable=False)
    data = db.Column(db.DateTime, nullable=False)
    local = db.Column(db.String(200))
    tipo = db.Column(db.String(50))
    status = db.Column(db.String(50))
    observacoes = db.Column(db.Text)

    def __repr__(self):
        return f"<Audiencia {self.id}>"


class Documento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    caminho_arquivo = db.Column(db.String(200), nullable=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    processo_id = db.Column(db.Integer, db.ForeignKey("processo.id"), nullable=False)
    observacoes = db.Column(db.Text)

    def __repr__(self):
        return f"<Documento {self.nome}>"


class Honorario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # Pago, Pendente, Atrasado
    descricao = db.Column(db.Text)
    processo_id = db.Column(db.Integer, db.ForeignKey("processo.id"), nullable=False)
    data_pagamento = db.Column(db.DateTime)
    forma_pagamento = db.Column(db.String(50))
    parcela = db.Column(db.String(20))  # Formato: "1/12", "2/12", etc.

    def __repr__(self):
        return f"<Honorario {self.id}>"


def init_db(app):
    """Inicializa o banco de dados"""
    db.init_app(app)

    with app.app_context():
        # Cria todas as tabelas
        db.create_all()

        # Verifica se já existe um usuário admin
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            # Cria usuário admin padrão
            admin = User(
                username="admin",
                password="admin123",  # Em produção, use hash de senha
                nome="Administrador",
                oab="000000",
                email="admin@cardosoemoreira.adv.br",
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
