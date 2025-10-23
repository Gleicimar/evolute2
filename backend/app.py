from flask import Flask, request, jsonify, render_template, url_for, redirect, session, send_from_directory
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
from config import Config
from db.mongo import collect_leads
import secrets

# Fuso horário de Brasília (UTC-3)
brt = timezone(timedelta(hours=-3))

app = Flask(__name__, static_folder='frontend', static_url_path='')

# ✅ Configurações
app.config.from_object(Config)
app.secret_key = secrets.token_hex(16)  # ✅ Necessário para sessions

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# --- ROTA PARA FRONTEND ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# ========================================
# ROTAS API
# ========================================

@app.route('/api', methods=['GET'])
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

@app.route('/painel', methods=['GET', 'POST'])
def painel():
    if request.method == 'GET':
        # Renderiza página de login
        return render_template('painel/login.html')

    elif request.method == 'POST':
        # ✅ Pega dados do formulário
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        # ✅ Validação
        if not usuario or not senha:
            return render_template('painel/login.html',
                                   error='Usuário e senha são obrigatórios')

        # ✅ Verificar credenciais (TROCAR por validação real depois!)
        if usuario == 'admin' and senha == 'admin':
            # Login bem-sucedido
            session['usuario'] = usuario
            session['logado'] = True
            return redirect(url_for('dashboard'))
        else:
            # Credenciais inválidas
            return render_template('painel/login.html',
                                   error='Usuário ou senha inválidos')

@app.route('/dashboard')
def dashboard():
    # ✅ Verificar se está logado
    if not session.get('logado'):
        return redirect(url_for('painel'))

    try:
        # Buscar todos os leads
        all_leads = list(collect_leads.find().sort('data', -1))
        for lead in all_leads:
            lead['_id'] = str(lead['_id'])

        return render_template('painel/dashboard.html',
                               leads=all_leads,
                               usuario=session.get('usuario'))
    except Exception as e:
        return f"Erro ao carregar dashboard: {str(e)}", 500
@app.route('/dashboard/editar_lead/<lead_id>', methods=['GET', 'POST'])
def editar_lead(lead_id):
    # ✅ Verificar se está logado
    if not session.get('logado'):
        return redirect(url_for('painel'))

    from bson.objectid import ObjectId

    if request.method == 'GET':
        # Buscar lead pelo ID
        lead = collect_leads.find_one({'_id': ObjectId(lead_id)})
        if not lead:
            return "Lead não encontrado", 404
        lead['_id'] = str(lead['_id'])
        return render_template('painel/editar_lead.html', lead=lead)

    elif request.method == 'POST':
        # Atualizar lead
        status = request.form.get('status')
        mensagem = request.form.get('mensagem')

        update_data = {
            'status': status,
            'mensagem': mensagem
        }

        collect_leads.update_one({'_id': ObjectId(lead_id)}, {'$set': update_data})
        return redirect(url_for('dashboard'))
@app.route('/dashboard/deletar_lead/<lead_id>', methods=['GET','POST'])
def deletar_lead(lead_id):
    # ✅ Verificar se está logado
    if not session.get('logado'):
        return redirect(url_for('painel'))

    from bson.objectid import ObjectId

    # Deletar lead pelo ID
    collect_leads.delete_one({'_id': ObjectId(lead_id)})
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    # ✅ Limpar sessão
    session.clear()
    return redirect(url_for('painel'))

# ========================================
# INICIALIZAÇÃO
# ========================================

if __name__ == '__main__':
    print('=' * 70)
    print('🚀 API EvoluteCode iniciando...')
    print('📍 API: http://127.0.0.1:5000')
    print('📧 Leads: http://127.0.0.1:5000/api/leads')
    print('🔐 Painel: http://127.0.0.1:5000/painel')
    print('=' * 70)
    print('👤 Credenciais de teste:')
    print('   Usuário: admin')
    print('   Senha: admin')
    print('=' * 70)

    # app.run(debug=True, host='0.0.0.0', port=5000)
