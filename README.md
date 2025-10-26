# 🚀 Evolute2 - Sistema CRM Seguro

Sistema completo de gerenciamento de leads com autenticação segura, desenvolvido com Flask e MongoDB.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Security](https://img.shields.io/badge/security-bcrypt-green)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Funcionalidades

### 🔒 **Segurança**
- ✅ Autenticação com bcrypt (hash de senhas)
- ✅ Proteção contra brute force (bloqueio após 5 tentativas)
- ✅ Sessões seguras com HTTPS
- ✅ Validação de entrada
- ✅ Logs de auditoria

### 📊 **Gerenciamento de Leads**
- ✅ CRUD completo de leads
- ✅ Sistema de status (novo, contatado, proposta, fechado, perdido)
- ✅ Priorização (baixa, média, alta)
- ✅ Valor estimado por lead
- ✅ Histórico de anotações
- ✅ Dashboard com estatísticas

### 👥 **Gestão de Usuários**
- ✅ Criação de usuários
- ✅ Alteração de senha
- ✅ Níveis de permissão (admin/user)
- ✅ Desativação de contas

### 📱 **Interface**
- ✅ Design moderno e responsivo
- ✅ Animações suaves
- ✅ Feedback visual
- ✅ Mobile-friendly

## 🛠️ Tecnologias

- **Backend:** Flask 3.0
- **Banco de Dados:** MongoDB
- **Segurança:** bcrypt, python-dotenv
- **Frontend:** HTML5, CSS3, JavaScript
- **Deploy:** Render + MongoDB Atlas

## 📦 Instalação

### **Pré-requisitos**
- Python 3.8+
- MongoDB (local ou Atlas)
- pip

### **1. Clone o repositório**
```bash
git clone https://github.com/Gleicimar/evolute2.git
cd evolute2
```

### **2. Crie ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### **3. Instale dependências**
```bash
pip install -r requirements.txt
```

### **4. Configure variáveis de ambiente**
```bash
# Copie o exemplo
cp .env.example .env

# Gere uma SECRET_KEY forte
python -c "import secrets; print(secrets.token_hex(32))"

# Edite o .env e cole a chave gerada
```

**Arquivo `.env`:**
```bash
SECRET_KEY=sua-chave-gerada-aqui
MONGODB_URI=mongodb://localhost:27017/evolutecode
FLASK_ENV=development
PORT=5000
```

### **5. Execute o sistema**
```bash
python app.py
```

O sistema criará automaticamente um usuário admin na primeira execução:
- **Usuário:** admin
- **Senha:** Admin@123

⚠️ **ALTERE ESSA SENHA IMEDIATAMENTE!**

### **6. Acesse o sistema**
```
http://localhost:5000/login
```

## 🧪 Testes

### **Executar suite de testes:**
```bash
python test_auth.py
```

### **Testes manuais interativos:**
```bash
python test_auth.py --manual
```

### **Limpar dados de teste:**
```bash
python test_auth.py --limpar
```

## 👤 Gerenciar Usuários

### **Criar novo usuário:**
```bash
python criar_usuario.py
```

### **Listar usuários:**
```bash
python criar_usuario.py --listar
```

### **Via Python (programático):**
```python
from auth import criar_usuario

resultado = criar_usuario(
    usuario='joao',
    senha='senha_segura',
    nome_completo='João Silva',
    email='joao@email.com',
    role='user'
)
print(resultado)
```

## 🚀 Deploy (Render + MongoDB Atlas)

### **1. Configure MongoDB Atlas**
1. Crie cluster gratuito em [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Crie banco de dados `evolutecode`
3. Copie a connection string

### **2. Configure o Render**
1. Faça fork do repositório
2. Crie novo Web Service no [render.com](https://render.com)
3. Conecte seu repositório
4. Configure:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

**Environment Variables:**
```
SECRET_KEY = [Generate no Render]
MONGODB_URI = sua-connection-string-do-atlas
FLASK_ENV = production
```

### **3. Deploy**
- Render fará deploy automaticamente
- Acesse a URL fornecida
- Faça login com admin/Admin@123
- **Altere a senha imediatamente!**

## 📚 Estrutura do Projeto

```
evolute2/
├── app.py                    # Aplicação principal
├── auth.py                   # Sistema de autenticação
├── config.py                 # Configurações
├── criar_usuario.py          # Script criação de usuários
├── test_auth.py              # Testes automatizados
├── requirements.txt          # Dependências
├── .env.example              # Exemplo de variáveis
├── .gitignore               # Arquivos ignorados
├── GUIA_INSTALACAO.md       # Guia detalhado
├── db/
│   ├── __init__.py
│   └── mongo.py             # Conexão MongoDB
├── static/
│   ├── css/
│   │   └── painel.css       # Estilos
│   └── js/
│       └── function.js      # JavaScript
└── templates/
    └── painel/
        ├── login.html       # Tela de login
        ├── painel.html      # Dashboard
        ├── alterar_senha.html
        └── editar_lead.html
```

## 🔐 Segurança

### **Boas práticas implementadas:**

✅ **Senhas:**
- Hash com bcrypt (12 rounds)
- Nunca armazenadas em texto plano
- Validação de força (mínimo 6 caracteres)

✅ **Sessões:**
- HttpOnly cookies (protege XSS)
- Secure flag em HTTPS
- SameSite=Lax (protege CSRF)
- Expiração de 24 horas

✅ **Proteção:**
- Bloqueio após 5 tentativas falhas
- Mensagens genéricas (não revela se user existe)
- Logs de todas as tentativas
- Validação de entrada

✅ **Variáveis de Ambiente:**
- Secrets fora do código
- .env no .gitignore
- Configuração por ambiente

## 📖 API Endpoints

### **Público:**
- `GET /` - Info da API
- `POST /api/leads` - Criar lead
- `GET /api/leads` - Listar leads

### **Autenticado:**
- `POST /login` - Login
- `GET /logout` - Logout
- `GET /painel` - Dashboard
- `GET /alterar-senha` - Alterar senha
- `POST /painel/deletar_lead/<id>` - Deletar lead
- `GET /painel/editar_lead/<id>` - Editar lead

### **Admin apenas:**
- `GET /admin/usuarios` - Listar usuários
- `POST /admin/criar-usuario` - Criar usuário

## 🐛 Troubleshooting

### **Erro: ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

### **Erro: MongoDB connection refused**
- Verifique se MongoDB está rodando
- Confirme MONGODB_URI no .env
- Para Atlas, verifique whitelist de IPs

### **Erro: Esqueci a senha**
```python
from auth import resetar_senha_admin
resetar_senha_admin('admin', 'NovaSenha@123')
```

### **Erro 502 no Render**
- Verifique logs no dashboard
- Confirme environment variables
- Teste build command localmente

## 📄 Licença

MIT License - veja [LICENSE](LICENSE)

## 👨‍💻 Autor

**Gleicimar**
- GitHub: [@Gleicimar](https://github.com/Gleicimar)
- Projeto: [evolute2](https://github.com/Gleicimar/evolute2)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Changelog

### v2.0.0 (Atual)
- ✅ Sistema de autenticação seguro com bcrypt
- ✅ Proteção contra brute force
- ✅ Gestão de usuários
- ✅ Testes automatizados
- ✅ Deploy otimizado para produção

### v1.0.0
- ✅ CRUD de leads
- ✅ Dashboard básico
- ⚠️ Autenticação insegura (corrigida na v2.0.0)

## 📞 Suporte

- **Issues:** [GitHub Issues](https://github.com/Gleicimar/evolute2/issues)
- **Documentação:** [GUIA_INSTALACAO.md](GUIA_INSTALACAO.md)

---

**⭐ Se este projeto te ajudou, considere dar uma estrela no GitHub!**
