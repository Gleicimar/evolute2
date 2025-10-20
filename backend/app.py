from  flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
from config import Config
from  db.mongo import collect_leads
# Fuso horário de Brasília (UTC-3)
brt = timezone(timedelta(hours=-3))

app = Flask(__name__)

app.config.from_object(Config)
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/evolute2'  # <- ajuste o nome do seu banco

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

#Dados de configuração
leads =[]

#Rotas da API

@app.route('/', methods=['GET'])
def home():
    return jsonify({
    'message': 'API EvoluteCode funcionando!',
    'version': '1.0.0',
    'endpoints': {
        'leads': '/api/leads'
    }
})

@app.route('/api/leads', methods=['GET', 'POST'])
def manage_leads():
    if request.method == 'POST':
        data = request.get_json()
        nome = data.get('nome')
        email = data.get('email')
        mensagem = data.get('mensagem')

        if not nome or not email or not mensagem:
            return jsonify({'error': 'Nome, email e mensagem são obrigatórios.'}), 400

        lead = {
            'nome': nome,
            'email': email,
            'mensagem': mensagem,
            'data':datetime.now(brt).strftime('%d/%m/%Y %H:%M:%S')
        }
        # collect_leads.append(lead)
        result = collect_leads.insert_one(lead) # <- insere o lead no MongoDB
        lead['_id'] = str(result.inserted_id)  # <- adiciona o ID do MongoDB ao lead
        return jsonify({'message': 'Lead adicionado com sucesso!', 'lead': lead}), 201

    elif request.method == 'GET':
        all_leads = list(collect_leads.find())
        for lead in all_leads:
            lead['_id'] = str(lead['_id'])  # <- converte ObjectId para string
        return jsonify({'leads': all_leads}), 200

@app.route('/api/listar', methods=['GET', 'POST'])
def listar():
    if request.method == 'POST':
        data = request.get_json()

    return jsonify({'message': 'Rota de listagem ativa!'}), 200


if __name__ == '__main__':
    print('=' * 50)
    print('🚀 API EvoluteCode iniciando...')
    print('📍 URL: http://127.0.0.1:5000')
    print('📧 Leads: http://127.0.0.1:5000/api/leads')
    print('=' * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
