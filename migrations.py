from db import db, Processo
from app import app
from sqlalchemy import text, inspect


def atualizar_banco():
    with app.app_context():
        # Obtém o inspetor do banco de dados
        inspector = inspect(db.engine)

        # Verifica as colunas existentes nas tabelas
        colunas_processo = [col["name"] for col in inspector.get_columns("processo")]
        colunas_honorario = [col["name"] for col in inspector.get_columns("honorario")]
        colunas_user = [col["name"] for col in inspector.get_columns("user")]

        with db.engine.connect() as connection:
            # Adiciona colunas na tabela processo se não existirem
            if "classe" not in colunas_processo:
                connection.execute(
                    text("ALTER TABLE processo ADD COLUMN classe VARCHAR(100)")
                )
            if "assunto" not in colunas_processo:
                connection.execute(
                    text("ALTER TABLE processo ADD COLUMN assunto VARCHAR(200)")
                )
            if "valor_causa" not in colunas_processo:
                connection.execute(
                    text("ALTER TABLE processo ADD COLUMN valor_causa FLOAT")
                )
            if "ultima_atualizacao" not in colunas_processo:
                connection.execute(
                    text("ALTER TABLE processo ADD COLUMN ultima_atualizacao DATETIME")
                )

            # Adiciona coluna na tabela honorario se não existir
            if "parcela" not in colunas_honorario:
                connection.execute(
                    text("ALTER TABLE honorario ADD COLUMN parcela VARCHAR(20)")
                )

            # Adiciona coluna na tabela user se não existir
            if "role" not in colunas_user:
                connection.execute(
                    text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'advogado'")
                )

            connection.commit()

        print("Banco de dados atualizado com sucesso!")


if __name__ == "__main__":
    atualizar_banco()
