from flask import Flask, request, jsonify, render_template, url_for, redirect, session
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
from config import Config
from db.mongo import collect_leads
from bson.objectid import ObjectId
import secrets

# Fuso horário de Brasília (UTC-3)
brt = timezone(timedelta(hours=-3))

app = Flask(__name__)

# Configurações
app.config.from_object(Config)
app.secret_key = secrets.token_hex(16)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ========================================
# ROTAS API
# ========================================

@app.route('/', methods=['GET'])
def home():
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

            lead = {
                'nome': nome,
                'email': email,
                'mensagem': mensagem or '',
                'data': datetime.now(brt).strftime('%d/%m/%Y %H:%M:%S'),
                'status': 'novo'
            }

            result = collect_leads.insert_one(lead)
            lead['_id'] = str(result.inserted_id)

            print(f'✅ Lead salvo: {nome} - {email}')

            return jsonify({
                'success': True,
                'message': 'Lead adicionado com sucesso!',
                'lead': lead
            }), 201

        except Exception as e:
            print(f'❌ Erro: {str(e)}')
            return jsonify({
                'success': False,
                'error': 'Erro ao processar requisição'
            }), 500

    elif request.method == 'GET':
        try:
            all_leads = list(collect_leads.find().sort('data', -1))
            for lead in all_leads:
                lead['_id'] = str(lead['_id'])

            return jsonify({
                'success': True,
                'count': len(all_leads),
                'leads': all_leads
            }), 200

        except Exception as e:
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
    """Rota do DASHBOARD (painel principal)"""
    # Verificar se está logado
    if not session.get('logado'):
        return redirect(url_for('login'))  # ← Redireciona para login

    try:
        # Buscar todos os leads
        all_leads = list(collect_leads.find().sort('data', -1))
        for lead in all_leads:
            lead['_id'] = str(lead['_id'])

        print(f'📊 Dashboard carregado com {len(all_leads)} leads')

        return render_template('painel/painel.html',
                               leads=all_leads,
                               usuario=session.get('usuario'))
    except Exception as e:
        print(f'❌ Erro ao carregar painel: {str(e)}')
        return f"Erro ao carregar painel: {str(e)}", 500

@app.route('/painel/editar_lead/<lead_id>', methods=['GET', 'POST'])
def editar_lead(lead_id):
    """Editar um lead"""
    if not session.get('logado'):
        return redirect(url_for('login'))

    if request.method == 'GET':
        # Buscar lead pelo ID
        lead = collect_leads.find_one({'_id': ObjectId(lead_id)})
        if not lead:
            return "Lead não encontrado", 404

        lead['_id'] = str(lead['_id'])
        return render_template('painel/editar_lead.html', lead=lead)

    elif request.method == 'POST':
        # Atualizar lead
        nome = request.form.get('nome')
        email = request.form.get('email')
        mensagem = request.form.get('mensagem')
        status = request.form.get('status')

        update_data = {
            'nome': nome,
            'email': email,
            'mensagem': mensagem,
            'status': status
        }

        collect_leads.update_one(
            {'_id': ObjectId(lead_id)},
            {'$set': update_data}
        )

        print(f'✅ Lead {lead_id} atualizado')
        return redirect(url_for('painel'))

@app.route('/painel/deletar_lead/<lead_id>', methods=['POST'])  # ← POST!
def deletar_lead(lead_id):
    """Deletar um lead"""
    if not session.get('logado'):
        return redirect(url_for('login'))

    try:
        result = collect_leads.delete_one({'_id': ObjectId(lead_id)})

        if result.deleted_count > 0:
            print(f'✅ Lead {lead_id} deletado')
        else:
            print(f'⚠️ Lead {lead_id} não encontrado')

        return redirect(url_for('painel'))

    except Exception as e:
        print(f'❌ Erro ao deletar: {str(e)}')
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
    print('=' * 70)
    print('👤 Credenciais de teste:')
    print('   Usuário: admin')
    print('   Senha: admin')
    print('=' * 70)

    app.run(debug=True, host='0.0.0.0', port=5000)
