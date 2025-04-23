from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
)
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from db import db, init_db, User, Processo, Audiencia, Cliente, Documento, Honorario
from datetime import datetime
from werkzeug.utils import secure_filename
from datajud_api import DatajudAPI

# Carrega as variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "chavesecreta124912478124")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lexManager.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")

# Configuração do logger
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/lexManager.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Iniciando CRM Advocacia')

# Inicializa o banco de dados
init_db(app)

# Cria a pasta de uploads se não existir
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Rotas
@app.route("/")
@login_required
def index():
    # Obtém estatísticas para o dashboard
    clientes_total = len(current_user.clientes)
    processos_ativos = len([p for p in current_user.processos if p.status == "Ativo"])
    audiencias_hoje = len(
        [
            a
            for a in current_user.processos
            for a in a.audiencias
            if a.data.date() == datetime.now().date()
        ]
    )
    novos_clientes = len(
        [
            c
            for c in current_user.clientes
            if (datetime.now() - c.data_cadastro).days <= 30
        ]
    )

    # Obtém últimos processos e próximas audiências
    ultimos_processos = (
        Processo.query.filter_by(advogado_id=current_user.id)
        .order_by(Processo.data_abertura.desc())
        .limit(5)
        .all()
    )

    proximas_audiencias = (
        Audiencia.query.join(Processo)
        .filter(Processo.advogado_id == current_user.id)
        .filter(Audiencia.data >= datetime.now())
        .order_by(Audiencia.data.asc())
        .limit(5)
        .all()
    )

    return render_template(
        "index.html",
        clientes_total=clientes_total,
        processos_ativos=processos_ativos,
        audiencias_hoje=audiencias_hoje,
        novos_clientes=novos_clientes,
        ultimos_processos=ultimos_processos,
        proximas_audiencias=proximas_audiencias,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:  # Em produção, use hash de senha
            login_user(user)
            return redirect(url_for("index"))
        flash("Usuário ou senha inválidos")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if request.method == "POST":
        current_user.nome = request.form.get("nome")
        current_user.oab = request.form.get("oab")
        current_user.username = request.form.get("username")
        current_user.email = request.form.get("email")

        # Atualiza a senha se fornecida
        password = request.form.get("password")
        if password:
            current_user.password = password

        db.session.commit()
        flash("Perfil atualizado com sucesso!")
        return redirect(url_for("perfil"))

    return render_template("perfil.html")


@app.route("/clientes")
@login_required
def clientes():
    clientes = Cliente.query.filter_by(advogado_id=current_user.id).all()
    return render_template("clientes.html", clientes=clientes)


@app.route("/adicionar_cliente", methods=["GET", "POST"])
@login_required
def adicionar_cliente():
    if request.method == "POST":
        cliente = Cliente(
            nome=request.form.get("nome"),
            cpf=request.form.get("cpf"),
            email=request.form.get("email"),
            telefone=request.form.get("telefone"),
            endereco=request.form.get("endereco"),
            advogado_id=current_user.id,
        )
        db.session.add(cliente)
        db.session.commit()
        flash("Cliente adicionado com sucesso!")
        return redirect(url_for("clientes"))

    return render_template("adicionar_cliente.html")


@app.route("/processos")
@login_required
def processos():
    processos = Processo.query.filter_by(advogado_id=current_user.id).all()
    return render_template("processos.html", processos=processos)


@app.route("/adicionar_processo", methods=["GET", "POST"])
@login_required
def adicionar_processo():
    if request.method == "POST":
        numero_processo = request.form.get("numero_processo")

        # Tenta sincronizar com o Datajud
        datajud = DatajudAPI()
        processo_datajud = datajud.sincronizar_processo(numero_processo)

        if processo_datajud:
            flash("Processo sincronizado com sucesso do Datajud!")
            return redirect(url_for("processos"))

        # Se não conseguir sincronizar, cria manualmente
        processo = Processo(
            numero_processo=numero_processo,
            cliente_id=request.form.get("cliente_id"),
            advogado_id=current_user.id,
            tribunal=request.form.get("tribunal"),
            vara=request.form.get("vara"),
            descricao=request.form.get("descricao"),
            status=request.form.get("status"),
        )
        db.session.add(processo)
        db.session.commit()
        flash("Processo adicionado com sucesso!")
        return redirect(url_for("processos"))

    clientes = Cliente.query.filter_by(advogado_id=current_user.id).all()
    return render_template("adicionar_processo.html", clientes=clientes)


@app.route("/audiencias")
@login_required
def audiencias():
    audiencias = (
        Audiencia.query.join(Processo)
        .filter(Processo.advogado_id == current_user.id)
        .all()
    )
    return render_template("audiencias.html", audiencias=audiencias)


@app.route("/adicionar_audiencia", methods=["GET", "POST"])
@login_required
def adicionar_audiencia():
    if request.method == "POST":
        audiencia = Audiencia(
            processo_id=request.form.get("processo_id"),
            data=datetime.strptime(request.form.get("data"), "%Y-%m-%dT%H:%M"),
            local=request.form.get("local"),
            tipo=request.form.get("tipo"),
            status=request.form.get("status"),
            observacoes=request.form.get("observacoes"),
        )
        db.session.add(audiencia)
        db.session.commit()
        flash("Audiência adicionada com sucesso!")
        return redirect(url_for("audiencias"))

    processos = Processo.query.filter_by(advogado_id=current_user.id).all()
    return render_template("adicionar_audiencia.html", processos=processos)


@app.route("/documentos")
@login_required
def documentos():
    documentos = (
        Documento.query.join(Processo)
        .filter(Processo.advogado_id == current_user.id)
        .all()
    )
    return render_template("documentos.html", documentos=documentos)


@app.route("/adicionar_documento", methods=["GET", "POST"])
@login_required
def adicionar_documento():
    if request.method == "POST":
        if "arquivo" not in request.files:
            flash("Nenhum arquivo selecionado")
            return redirect(request.url)

        arquivo = request.files["arquivo"]
        if arquivo.filename == "":
            flash("Nenhum arquivo selecionado")
            return redirect(request.url)

        if arquivo:
            filename = secure_filename(arquivo.filename)
            arquivo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            documento = Documento(
                nome=request.form["nome"],
                tipo=request.form["tipo"],
                caminho_arquivo=filename,
                processo_id=request.form["processo_id"],
                observacoes=request.form["observacoes"],
            )
            db.session.add(documento)
            db.session.commit()
            flash("Documento adicionado com sucesso!")
            return redirect(url_for("documentos"))

    processos = Processo.query.filter_by(advogado_id=current_user.id).all()
    return render_template("adicionar_documento.html", processos=processos)


@app.route("/download_documento/<int:id>")
@login_required
def download_documento(id):
    documento = Documento.query.get_or_404(id)
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], documento.caminho_arquivo, as_attachment=True
    )


@app.route("/relatorios")
@login_required
def relatorios():
    clientes = Cliente.query.filter_by(advogado_id=current_user.id).all()
    processos = Processo.query.filter_by(advogado_id=current_user.id).all()
    return render_template("relatorios.html", clientes=clientes, processos=processos)


@app.route("/relatorios/processos", methods=["GET", "POST"])
@login_required
def gerar_relatorio_processos():
    if request.method == "POST":
        data_inicio = datetime.strptime(request.form["data_inicio"], "%Y-%m-%d")
        data_fim = datetime.strptime(request.form["data_fim"], "%Y-%m-%d")
        status = request.form.get("status")
        advogado_id = request.form.get("advogado_id")
        
        # Construir a query base
        query = Processo.query
        
        # Aplicar filtros
        if data_inicio:
            query = query.filter(Processo.data_abertura >= data_inicio)
        if data_fim:
            query = query.filter(Processo.data_abertura <= data_fim)
        if status and status != "todos":
            query = query.filter(Processo.status == status)
        if advogado_id and advogado_id != "todos":
            query = query.filter(Processo.advogado_id == advogado_id)
        
        # Filtrar por permissões
        if current_user.role != "admin":
            query = query.filter(Processo.advogado_id == current_user.id)
        
        processos = query.all()
        
        return render_template("relatorio_processos.html", 
                             processos=processos,
                             data_inicio=data_inicio,
                             data_fim=data_fim,
                             status=status,
                             advogado_id=advogado_id)
    
    # Se for GET, mostrar o formulário
    advogados = User.query.filter_by(role="advogado").all()
    return render_template("relatorio_processos.html", advogados=advogados)


@app.route("/gerar_relatorio_honorarios", methods=["POST"])
@login_required
def gerar_relatorio_honorarios():
    mes = request.form.get("mes")
    cliente_id = request.form.get("cliente")

    query = Honorario.query
    if mes:
        query = query.filter(db.func.strftime("%Y-%m", Honorario.data) == mes)
    if cliente_id:
        query = query.filter(Honorario.cliente_id == cliente_id)

    honorarios = query.all()
    return render_template("relatorio_honorarios.html", honorarios=honorarios)


@app.route("/gerar_relatorio_audiencias", methods=["POST"])
@login_required
def gerar_relatorio_audiencias():
    data_inicio = request.form.get("data_inicio")
    data_fim = request.form.get("data_fim")
    status = request.form.get("status")

    query = Audiencia.query
    if data_inicio:
        query = query.filter(Audiencia.data >= data_inicio)
    if data_fim:
        query = query.filter(Audiencia.data <= data_fim)
    if status:
        query = query.filter(Audiencia.status == status)

    audiencias = query.all()
    return render_template("relatorio_audiencias.html", audiencias=audiencias)


@app.route("/gerar_relatorio_documentos", methods=["POST"])
@login_required
def gerar_relatorio_documentos():
    tipo = request.form.get("tipo")
    processo_id = request.form.get("processo")

    query = Documento.query
    if tipo:
        query = query.filter(Documento.tipo == tipo)
    if processo_id:
        query = query.filter(Documento.processo_id == processo_id)

    documentos = query.all()
    return render_template("relatorio_documentos.html", documentos=documentos)


@app.route("/pesquisar_processos", methods=["GET", "POST"])
@login_required
def pesquisar_processos():
    if request.method == "POST":
        numero_processo = request.form.get("numero_processo")
        datajud = DatajudAPI()
        processo_data = datajud.buscar_processo(numero_processo)

        if processo_data:
            # Obtém o primeiro cliente do advogado atual
            cliente = Cliente.query.filter_by(advogado_id=current_user.id).first()
            if not cliente:
                flash("Você precisa ter pelo menos um cliente cadastrado para adicionar processos.", "warning")
                return redirect(url_for("adicionar_cliente"))

            # Cria um objeto Processo temporário para exibição
            processo = Processo(
                numero_processo=numero_processo,
                cliente_id=cliente.id,  # Usa o ID do primeiro cliente
                advogado_id=current_user.id,
                classe=processo_data.get("classe", ""),
                assunto=processo_data.get("assunto", ""),
                status=processo_data.get("status", "Ativo"),
                tribunal=processo_data.get("tribunal", ""),
                vara=processo_data.get("vara", ""),
                valor_causa=processo_data.get("valor_causa", 0.0),
                descricao=processo_data.get("descricao", ""),
                data_abertura=datetime.utcnow(),
                ultima_atualizacao=datetime.utcnow(),
            )
            return render_template("pesquisar_processos.html", resultados=[processo])

        flash("Processo não encontrado no Datajud.", "warning")

    return render_template("pesquisar_processos.html")


@app.route("/adicionar_processo_datajud/<numero_processo>")
@login_required
def adicionar_processo_datajud(numero_processo):
    datajud = DatajudAPI()
    processo = datajud.sincronizar_processo(numero_processo)

    if processo:
        flash("Processo adicionado com sucesso!", "success")
    else:
        flash("Erro ao adicionar processo.", "danger")

    return redirect(url_for("processos"))


@app.route("/excluir_cliente/<int:id>", methods=["POST"])
@login_required
def excluir_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if cliente.advogado_id != current_user.id:
        flash("Você não tem permissão para excluir este cliente.", "danger")
        return redirect(url_for("clientes"))
    
    try:
        # Primeiro, verifica se existem processos ativos
        processos_ativos = Processo.query.filter_by(cliente_id=id).all()
        if processos_ativos:
            flash("Não é possível excluir o cliente pois existem processos ativos vinculados a ele.", "danger")
            return redirect(url_for("clientes"))
        
        # Se não houver processos ativos, pode excluir o cliente
        db.session.delete(cliente)
        db.session.commit()
        flash("Cliente excluído com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao excluir o cliente. Por favor, tente novamente.", "danger")
        app.logger.error(f"Erro ao excluir cliente: {str(e)}")
    
    return redirect(url_for("clientes"))


@app.route("/excluir_audiencia/<int:id>", methods=["POST"])
@login_required
def excluir_audiencia(id):
    audiencia = Audiencia.query.get_or_404(id)
    processo = Processo.query.get_or_404(audiencia.processo_id)
    
    if processo.advogado_id != current_user.id:
        flash("Você não tem permissão para excluir esta audiência.", "danger")
        return redirect(url_for("audiencias"))
    
    db.session.delete(audiencia)
    db.session.commit()
    flash("Audiência excluída com sucesso!", "success")
    return redirect(url_for("audiencias"))


@app.route("/excluir_processo/<int:id>", methods=["POST"])
@login_required
def excluir_processo(id):
    processo = Processo.query.get_or_404(id)
    if processo.advogado_id != current_user.id:
        flash("Você não tem permissão para excluir este processo.", "danger")
        return redirect(url_for("processos"))
    
    try:
        # Exclui todas as audiências relacionadas
        for audiencia in processo.audiencias:
            db.session.delete(audiencia)
        
        # Exclui todos os documentos relacionados
        for documento in processo.documentos:
            # Remove o arquivo físico se existir
            if documento.caminho_arquivo:
                try:
                    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], documento.caminho_arquivo))
                except OSError:
                    pass  # Ignora se o arquivo não existir
            db.session.delete(documento)
        
        # Exclui todos os honorários relacionados
        for honorario in processo.honorarios:
            db.session.delete(honorario)
        
        # Agora pode excluir o processo
        db.session.delete(processo)
        db.session.commit()
        flash("Processo e todos os dados relacionados foram excluídos com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao excluir o processo. Por favor, tente novamente.", "danger")
        app.logger.error(f"Erro ao excluir processo: {str(e)}")
    
    return redirect(url_for("processos"))


@app.route("/editar_cliente/<int:id>", methods=["GET", "POST"])
@login_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if cliente.advogado_id != current_user.id:
        flash("Você não tem permissão para editar este cliente.", "danger")
        return redirect(url_for("clientes"))

    if request.method == "POST":
        cliente.nome = request.form.get("nome")
        cliente.cpf = request.form.get("cpf")
        cliente.email = request.form.get("email")
        cliente.telefone = request.form.get("telefone")
        cliente.endereco = request.form.get("endereco")
        
        db.session.commit()
        flash("Cliente atualizado com sucesso!", "success")
        return redirect(url_for("clientes"))

    return render_template("editar_cliente.html", cliente=cliente)


@app.route("/editar_processo/<int:id>", methods=["GET", "POST"])
@login_required
def editar_processo(id):
    processo = Processo.query.get_or_404(id)
    if processo.advogado_id != current_user.id:
        flash("Você não tem permissão para editar este processo.", "danger")
        return redirect(url_for("processos"))

    if request.method == "POST":
        processo.numero_processo = request.form.get("numero_processo")
        processo.cliente_id = request.form.get("cliente_id")
        processo.tribunal = request.form.get("tribunal")
        processo.vara = request.form.get("vara")
        processo.classe = request.form.get("classe")
        processo.assunto = request.form.get("assunto")
        processo.valor_causa = float(request.form.get("valor_causa", 0))
        processo.status = request.form.get("status")
        processo.descricao = request.form.get("descricao")
        
        db.session.commit()
        flash("Processo atualizado com sucesso!", "success")
        return redirect(url_for("processos"))

    clientes = Cliente.query.filter_by(advogado_id=current_user.id).all()
    return render_template("editar_processo.html", processo=processo, clientes=clientes)


@app.route("/editar_audiencia/<int:id>", methods=["GET", "POST"])
@login_required
def editar_audiencia(id):
    audiencia = Audiencia.query.get_or_404(id)
    processo = Processo.query.get_or_404(audiencia.processo_id)
    
    if processo.advogado_id != current_user.id:
        flash("Você não tem permissão para editar esta audiência.", "danger")
        return redirect(url_for("audiencias"))

    if request.method == "POST":
        audiencia.processo_id = request.form.get("processo_id")
        audiencia.data = datetime.strptime(request.form.get("data"), "%Y-%m-%dT%H:%M")
        audiencia.local = request.form.get("local")
        audiencia.tipo = request.form.get("tipo")
        audiencia.status = request.form.get("status")
        audiencia.observacoes = request.form.get("observacoes")
        
        db.session.commit()
        flash("Audiência atualizada com sucesso!", "success")
        return redirect(url_for("audiencias"))

    processos = Processo.query.filter_by(advogado_id=current_user.id).all()
    return render_template("editar_audiencia.html", audiencia=audiencia, processos=processos)


@app.route("/honorarios/<int:processo_id>", methods=["GET", "POST"])
@login_required
def honorarios(processo_id):
    processo = Processo.query.get_or_404(processo_id)
    if processo.advogado_id != current_user.id:
        flash("Você não tem permissão para acessar este processo.", "danger")
        return redirect(url_for("processos"))

    if request.method == "POST":
        try:
            # Log dos dados recebidos
            app.logger.info(f"Dados do formulário: {request.form}")
            
            tipo_calculo = request.form.get("tipo_calculo")
            app.logger.info(f"Tipo de cálculo: {tipo_calculo}")
            
            valor_base_str = request.form.get("valor_base", "0")
            percentual_str = request.form.get("percentual", "0")
            valor_fixo_str = request.form.get("valor_fixo", "0")
            
            app.logger.info(f"Valores recebidos - Base: {valor_base_str}, Percentual: {percentual_str}, Fixo: {valor_fixo_str}")
            
            # Conversão segura dos valores
            valor_base = float(valor_base_str.replace(',', '.')) if valor_base_str else 0
            percentual = float(percentual_str.replace(',', '.')) if percentual_str else 0
            valor_fixo = float(valor_fixo_str.replace(',', '.')) if valor_fixo_str else 0
            
            app.logger.info(f"Valores convertidos - Base: {valor_base}, Percentual: {percentual}, Fixo: {valor_fixo}")
            
            parcelas = int(request.form.get("parcelas", 1))
            data_vencimento_str = request.form.get("data_vencimento")
            
            app.logger.info(f"Parcelas: {parcelas}, Data vencimento: {data_vencimento_str}")
            
            if not data_vencimento_str:
                raise ValueError("Data de vencimento não fornecida")
                
            data_vencimento = datetime.strptime(data_vencimento_str, "%Y-%m-%d")

            # Validação dos campos
            if tipo_calculo == "percentual":
                if valor_base <= 0:
                    raise ValueError("Valor da causa deve ser maior que zero")
                if percentual <= 0:
                    raise ValueError("Percentual deve ser maior que zero")
                valor_total = valor_base * (percentual / 100)
            else:  # valor_fixo
                if valor_fixo <= 0:
                    raise ValueError("Valor fixo deve ser maior que zero")
                valor_total = valor_fixo

            app.logger.info(f"Valor total calculado: {valor_total}")

            # Cria as parcelas
            valor_parcela = valor_total / parcelas
            app.logger.info(f"Valor da parcela: {valor_parcela}")
            
            for i in range(parcelas):
                data_parcela = data_vencimento.replace(day=1)  # Primeiro dia do mês
                if i > 0:
                    # Adiciona meses para as parcelas seguintes, lidando com a mudança de ano
                    mes = data_parcela.month + i
                    ano = data_parcela.year
                    while mes > 12:
                        mes -= 12
                        ano += 1
                    data_parcela = data_parcela.replace(year=ano, month=mes)
                
                honorario = Honorario(
                    processo_id=processo_id,
                    valor=valor_parcela,
                    data=data_parcela,
                    status="Pendente",
                    parcela=f"{i+1}/{parcelas}"
                )
                db.session.add(honorario)
                app.logger.info(f"Criada parcela {i+1}/{parcelas} para {data_parcela.strftime('%d/%m/%Y')}")
            
            db.session.commit()
            flash("Honorários calculados e parcelas criadas com sucesso!", "success")
            return redirect(url_for("honorarios", processo_id=processo_id))

        except ValueError as e:
            app.logger.error(f"Erro de validação: {str(e)}")
            flash(f"Erro: {str(e)}", "danger")
            return redirect(url_for("honorarios", processo_id=processo_id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao calcular honorários: {str(e)}", exc_info=True)
            flash("Erro ao calcular honorários. Por favor, tente novamente.", "danger")
            return redirect(url_for("honorarios", processo_id=processo_id))

    # Calcula totais
    honorarios = Honorario.query.filter_by(processo_id=processo_id).all()
    total_pendente = sum(h.valor for h in honorarios if h.status == "Pendente")
    total_pago = sum(h.valor for h in honorarios if h.status == "Pago")
    total_geral = total_pendente + total_pago

    return render_template(
        "honorarios.html",
        processo=processo,
        honorarios=honorarios,
        total_pendente=total_pendente,
        total_pago=total_pago,
        total_geral=total_geral
    )


@app.route("/atualizar_honorario/<int:id>", methods=["POST"])
@login_required
def atualizar_honorario(id):
    honorario = Honorario.query.get_or_404(id)
    processo = Processo.query.get_or_404(honorario.processo_id)
    
    if processo.advogado_id != current_user.id:
        flash("Você não tem permissão para atualizar este honorário.", "danger")
        return redirect(url_for("processos"))

    honorario.status = request.form.get("status")
    db.session.commit()
    flash("Status do honorário atualizado com sucesso!", "success")
    return redirect(url_for("honorarios", processo_id=honorario.processo_id))


@app.route("/excluir_honorario/<int:id>", methods=["POST"])
@login_required
def excluir_honorario(id):
    honorario = Honorario.query.get_or_404(id)
    processo = Processo.query.get_or_404(honorario.processo_id)
    
    if processo.advogado_id != current_user.id:
        flash("Você não tem permissão para excluir este honorário.", "danger")
        return redirect(url_for("honorarios", processo_id=processo.id))
    
    try:
        db.session.delete(honorario)
        db.session.commit()
        flash("Honorário excluído com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao excluir o honorário. Por favor, tente novamente.", "danger")
        app.logger.error(f"Erro ao excluir honorário: {str(e)}")
    
    return redirect(url_for("honorarios", processo_id=processo.id))


if __name__ == "__main__":
    app.run(debug=True)
