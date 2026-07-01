from flask import Flask, request, jsonify, render_template, url_for, redirect, session
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
from config import Config
from db.mongo import collect_leads
from bson.objectid import ObjectId
import secrets
import os
import bcrypt

# Fuso horário de Brasília (UTC-3)
brt = timezone(timedelta(hours=-3))
# ========================================
# HELPER FUNCTIONS (ADICIONAR AQUI)
# ========================================

def formatar_data_br():
    """Retorna data/hora atual formatada"""
    return datetime.now(brt).strftime('%d/%m/%Y %H:%M:%S')

def adicionar_anotacao(lead_id, texto, usuario):
    """Adiciona uma anotação ao histórico do lead"""
    anotacao = {
        'texto': texto,
        'data': formatar_data_br(),
        'usuario': usuario
    }

    collect_leads.update_one(
        {'_id': ObjectId(lead_id)},
        {
            '$push': {'anotacoes': anotacao},
            '$set': {'data_ultima_interacao': formatar_data_br()}
        }
    )


app = Flask(__name__)

# Configurações
app.config.from_object(Config)
app.secret_key = secrets.token_hex(16)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ========================================
# ROTAS API
# ========================================
@app.route('/')
def home():
    return render_template('frontend/index.html')
 
@app.route('/response', methods=['GET'])
def responsehome():
    return jsonify({
        'message': 'API EvoluteCode funcionando!',
        'version': '1.0.0',
        'endpoints': {
            'leads': '/api/leads',
            'painel': '/painel'
        }
    })

@app.route('/api/leads', methods=['GET', 'POST'])
def manage_leads():
    if request.method == 'POST':
        try:
            data = request.get_json()
            nome = data.get('nome')
            email = data.get('email')
            mensagem = data.get('mensagem')

            if not nome or not email:
                return jsonify({
                    'success': False,
                    'error': 'Nome e email são obrigatórios'
                }), 400
            # ✅ LEAD COM FOLLOW-UP (ATUALIZADO)
            lead = {
                'nome': nome,
                'email': email,
                'telefone': data.get('telefone', ''),
                'mensagem': mensagem or '',

                # ✅ FOLLOW-UP (NOVO)
                'status': 'novo',
                'prioridade': data.get('prioridade', 'média'),
                'origem': data.get('origem', 'site'),
                'valor_estimado': data.get('valor_estimado', 0),

                # ✅ DATAS (NOVO)
                'data': datetime.now(brt).strftime('%d/%m/%Y %H:%M:%S'),
                'data_criacao': datetime.now(brt).strftime('%d/%m/%Y %H:%M:%S'),
                'data_ultima_interacao': datetime.now(brt).strftime('%d/%m/%Y %H:%M:%S'),
                'data_proximo_contato': data.get('data_proximo_contato', ''),

                # ✅ HISTÓRICO (NOVO)
                'anotacoes': [{
                   'texto': 'Lead criado',
                   'data': datetime.now(brt).strftime('%d/%m/%Y %H:%M:%S'),
                   'usuario': 'sistema'
                                   }],
                 # ✅ RESPONSÁVEL (NOVO)
                 'responsavel':None
            }
            result = collect_leads.insert_one(lead)
            lead['_id'] = str(result.inserted_id)

            print(f'📥 Novo lead adicionado: {lead["_id"]} - {nome} ({email})')
            return jsonify({
                'success': True,
                'lead': lead
            }), 201
        except Exception as e:
            print(f'❌ Erro ao adicionar lead: {str(e)}')
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    elif request.method == 'GET':
        try:
            leads = list(collect_leads.find().sort('data', -1))
            for lead in leads:
                lead['_id'] = str(lead['_id'])

            print(f'📊 {len(leads)} leads recuperados')
            return jsonify({
                'success': True,
                'leads': leads
            }), 200
        except Exception as e:
            print(f'❌ Erro ao recuperar leads: {str(e)}')
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
# ========================================
# ROTAS PAINEL
# ========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de LOGIN"""
    if request.method == 'GET':
        return render_template('painel/login.html')

    elif request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if not usuario or not senha:
            return render_template('painel/login.html',
                                   error='Usuário e senha são obrigatórios')

        # Validação (trocar por validação real!)
        if usuario == 'admin' and senha == 'admin':
            session['usuario'] = usuario
            session['logado'] = True
            print(f'✅ Login bem-sucedido: {usuario}')
            return redirect(url_for('painel'))  # ← Redireciona para dashboard
        else:
            return render_template('painel/login.html',
                                   error='Usuário ou senha inválidos')

@app.route('/painel', methods=['GET', 'POST'])
def painel():
    """Dashboard com estatísticas de follow-up"""
    if not session.get('logado'):
        return redirect(url_for('login'))

    try:
        # Buscar todos os leads
        all_leads = list(collect_leads.find().sort('data', -1))

        # ✅ CALCULAR ESTATÍSTICAS
        total_leads = len(all_leads)
        novos = len([l for l in all_leads if l.get('status') == 'novo'])
        contatados = len([l for l in all_leads if l.get('status') == 'contatado'])
        em_proposta = len([l for l in all_leads if l.get('status') == 'proposta'])
        fechados = len([l for l in all_leads if l.get('status') == 'fechado'])
        perdidos = len([l for l in all_leads if l.get('status') == 'perdido'])

        # Valor total estimado
        valor_total = sum([l.get('valor_estimado', 0) for l in all_leads if l.get('status') != 'perdidos'])

        for lead in all_leads:
            lead['_id'] = str(lead['_id'])

        # ✅ Return fora do loop
        return render_template('painel/painel.html',
                               leads=all_leads,
                               usuario=session.get('usuario'),
                               stats={
                                   'total_leads': total_leads,
                                   'novos': novos,
                                   'contatados': contatados,
                                   'em_proposta': em_proposta,
                                   'fechados': fechados,
                                   'perdidos': perdidos,
                                   'valor_total': valor_total
                               })

    except Exception as e:
        print(f'❌ Erro ao carregar painel: {str(e)}')
        return f"Erro ao carregar painel: {str(e)}", 500


@app.route('/painel/editar_lead/<lead_id>', methods=['GET', 'POST'])
def editar_lead(lead_id):
    """Editar lead (mantém compatibilidade)"""
    if not session.get('logado'):
        return redirect(url_for('login'))

    if request.method == 'GET':
        lead = collect_leads.find_one({'_id': ObjectId(lead_id)})
        if not lead:
            return "Lead não encontrado", 404

        lead['_id'] = str(lead['_id'])
        return render_template('painel/editar_lead.html', lead=lead)

    elif request.method == 'POST':
        # Atualizar dados básicos + follow-up
        nome = request.form.get('nome')
        email = request.form.get('email')
        mensagem = request.form.get('mensagem')
        status = request.form.get('status', 'novo')  # ✅ NOVO
        prioridade = request.form.get('prioridade', 'media')  # ✅ NOVO

        update_data = {
            'nome': nome,
            'email': email,
            'mensagem': mensagem,
            'status': status,  # ✅ NOVO
            'prioridade': prioridade,  # ✅ NOVO
            'data_ultima_interacao': datetime.now(brt).strftime('%d/%m/%Y %H:%M:%S')  # ✅ NOVO
        }

        collect_leads.update_one(
            {'_id': ObjectId(lead_id)},
            {'$set': update_data}
        )

        # ✅ ADICIONAR ANOTAÇÃO (NOVO)
        adicionar_anotacao(
            lead_id,
            f'Lead editado por {session.get("usuario")}',
            session.get('usuario')
        )

        print(f'✅ Lead {lead_id} atualizado')
        return redirect(url_for('painel'))
# ✅ NOVAS ROTAS DE FOLLOW-UP (ADICIONAR)

@app.route('/painel/lead/<lead_id>')
def visualizar_lead(lead_id):
    """Ver detalhes completos do lead"""
    if not session.get('logado'):
        return redirect(url_for('login'))

    try:
        lead = collect_leads.find_one({'_id': ObjectId(lead_id)})
        if not lead:
            return "Lead não encontrado", 404

        lead['_id'] = str(lead['_id'])

        return render_template('painel/lead_detalhes.html',
                               lead=lead,
                               usuario=session.get('usuario'))
    except Exception as e:
        return f"Erro: {str(e)}", 500

@app.route('/painel/lead/<lead_id>/atualizar', methods=['POST'])
def atualizar_lead_followup(lead_id):
    """Atualizar status e informações de follow-up"""
    if not session.get('logado'):
        return redirect(url_for('login'))

    try:
        status = request.form.get('status')
        prioridade = request.form.get('prioridade')
        valor_estimado = request.form.get('valor_estimado', 0)
        data_proximo_contato = request.form.get('data_proximo_contato')

        update_data = {
            'status': status,
            'prioridade': prioridade,
            'valor_estimado': float(valor_estimado) if valor_estimado else 0,
            'data_ultima_interacao': datetime.now(brt).strftime('%d/%m/%Y %H:%M:%S')
        }

        if data_proximo_contato:
            update_data['data_proximo_contato'] = data_proximo_contato

        collect_leads.update_one(
            {'_id': ObjectId(lead_id)},
            {'$set': update_data}
        )

        # Adicionar anotação automática
        adicionar_anotacao(
            lead_id,
            f'Status atualizado para: {status}',
            session.get('usuario')
        )

        print(f'✅ Lead {lead_id} atualizado')
        return redirect(url_for('visualizar_lead', lead_id=lead_id))

    except Exception as e:
        return f"Erro: {str(e)}", 500

@app.route('/painel/lead/<lead_id>/anotacao', methods=['POST'])
def adicionar_anotacao_lead(lead_id):
    """Adicionar nota ao histórico"""
    if not session.get('logado'):
        return redirect(url_for('login'))

    try:
        texto = request.form.get('anotacao')

        if not texto:
            return "Anotação vazia", 400

        adicionar_anotacao(lead_id, texto, session.get('usuario'))

        print(f'✅ Anotação adicionada ao lead {lead_id}')
        return redirect(url_for('visualizar_lead', lead_id=lead_id))

    except Exception as e:
        return f"Erro: {str(e)}", 500
@app.route('/painel/deletar_lead/<lead_id>', methods=['POST'])  # ← POST!
def deletar_lead(lead_id):
    """Deletar um lead - Suporta AJAX e formulário"""
    if not session.get('logado'):
        # Se for requisição AJAX, retorna JSON
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        return redirect(url_for('login'))

    try:
        result = collect_leads.delete_one({'_id': ObjectId(lead_id)})

        if result.deleted_count > 0:
            print(f'✅ Lead {lead_id} deletado')

            # ✅ Retorna JSON se for requisição AJAX
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Lead deletado com sucesso!'
                }), 200

            # Ou redireciona se for formulário
            return redirect(url_for('painel'))
        else:
            print(f'⚠️ Lead {lead_id} não encontrado')

            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Lead não encontrado'
                }), 404

            return redirect(url_for('painel'))

    except Exception as e:
        print(f'❌ Erro ao deletar: {str(e)}')

        if request.headers.get('Content-Type') == 'application/json' or request.is_json:
            return jsonify({
                'success': False,
                'message': f'Erro ao deletar: {str(e)}'
            }), 500

        return f"Erro: {str(e)}", 500

@app.route('/logout')
def logout():
    """Logout do painel"""
    usuario = session.get('usuario')
    session.clear()
    print(f'👋 Logout: {usuario}')
    return redirect(url_for('login'))

# ========================================
# INICIALIZAÇÃO
# ========================================

if __name__ == '__main__':
    print('=' * 70)
    print('🚀 API EvoluteCode iniciando...')
    print('📍 API: http://127.0.0.1:5000')
    print('📧 Leads: http://127.0.0.1:5000/api/leads')
    print('🔐 Login: http://127.0.0.1:5000/login')
    print('📊 Painel: http://127.0.0.1:5000/painel')
    # print(f'📍 Porta: {port}')
    print('=' * 70)
    print('👤 Credenciais de teste:')
    print('   Usuário: admin')
    print('   Senha: admin')
    print('=' * 70)
    # port = int(os.environ.get('PORT', 5000))

    app.run(debug=True, host='0.0.0.0', port=5000)
