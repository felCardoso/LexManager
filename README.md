# LexManager

Sistema de CRM para escritórios de advocacia desenvolvido com Flask, SQLite e integração com a API do Datajud.

## Funcionalidades

- Gerenciamento de clientes
- Controle de processos
- Integração com API do Datajud
- Dashboard com estatísticas
- Sistema de autenticação
- Controle de audiências

## Requisitos

- Python 3.8+
- pip

## Instalação

1. Clone o repositório:
```bash
git clone [url-do-repositorio]
cd crm-advocacia
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
- Copie o arquivo `.env.example` para `.env`
- Edite o arquivo `.env` com suas configurações

5. Inicialize o banco de dados:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Executando o Sistema

1. Ative o ambiente virtual (se ainda não estiver ativo):
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Execute o servidor:
```bash
python app.py
```

3. Acesse o sistema em: `http://localhost:5000`

## Estrutura do Projeto

```
crm-advocacia/
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências
├── .env                # Variáveis de ambiente
├── templates/          # Templates HTML
│   ├── base.html
│   ├── index.html
│   └── login.html
└── README.md           # Documentação
```

## Segurança

- Use uma chave secreta forte no arquivo `.env`
- Mantenha o sistema atualizado

## Contribuição

Contribuições são bem-vindas! Por favor, siga as diretrizes de contribuição.

## Licença

Este projeto está licenciado sob a licença MIT. 
