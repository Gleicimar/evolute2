# auth.py - Sistema de Autenticação Seguro
"""
Módulo de autenticação com bcrypt e boas práticas de segurança
"""

import bcrypt
from datetime import datetime, timezone, timedelta
from db.mongo import db

# Collection de usuários
collect_users = db['usuarios']

# Fuso horário de Brasília
brt = timezone(timedelta(hours=-3))


def hash_senha(senha):
    """
    Gera hash seguro da senha usando bcrypt

    Args:
        senha (str): Senha em texto plano

    Returns:
        bytes: Hash da senha
    """
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds é um bom balanço segurança/performance
    return bcrypt.hashpw(senha.encode('utf-8'), salt)


def verificar_senha(senha, hash_armazenado):
    """
    Verifica se a senha corresponde ao hash armazenado

    Args:
        senha (str): Senha em texto plano
        hash_armazenado (bytes ou str): Hash armazenado no banco

    Returns:
        bool: True se a senha é válida, False caso contrário
    """
    try:
        # Converte para bytes se necessário
        if isinstance(hash_armazenado, str):
            hash_armazenado = hash_armazenado.encode('utf-8')

        return bcrypt.checkpw(senha.encode('utf-8'), hash_armazenado)
    except Exception as e:
        print(f'❌ Erro ao verificar senha: {str(e)}')
        return False


def criar_usuario(usuario, senha, nome_completo, email, role='user'):
    """
    Cria um novo usuário no sistema

    Args:
        usuario (str): Nome de usuário (único)
        senha (str): Senha em texto plano
        nome_completo (str): Nome completo do usuário
        email (str): Email do usuário
        role (str): Papel do usuário (admin, user, etc)

    Returns:
        dict: Resultado da operação
    """
    # Verifica se usuário já existe
    if collect_users.find_one({'usuario': usuario}):
        return {
            'success': False,
            'message': 'Usuário já existe'
        }

    # Verifica se email já existe
    if collect_users.find_one({'email': email}):
        return {
            'success': False,
            'message': 'Email já cadastrado'
        }

    # Cria hash da senha
    senha_hash = hash_senha(senha)

    # Cria documento do usuário
    novo_usuario = {
        'usuario': usuario,
        'senha': senha_hash,
        'nome_completo': nome_completo,
        'email': email,
        'role': role,
        'ativo': True,
        'data_criacao': datetime.now(brt).strftime('%d/%m/%Y %H:%M:%S'),
        'ultimo_login': None,
        'tentativas_login': 0,
        'bloqueado_ate': None
    }

    try:
        result = collect_users.insert_one(novo_usuario)
        print(f'✅ Usuário criado: {usuario}')
        return {
            'success': True,
            'message': 'Usuário criado com sucesso',
            'user_id': str(result.inserted_id)
        }
    except Exception as e:
        print(f'❌ Erro ao criar usuário: {str(e)}')
        return {
            'success': False,
            'message': f'Erro ao criar usuário: {str(e)}'
        }


def autenticar_usuario(usuario, senha):
    """
    Autentica um usuário

    Args:
        usuario (str): Nome de usuário
        senha (str): Senha em texto plano

    Returns:
        dict: Resultado da autenticação
    """
    # Busca usuário
    user = collect_users.find_one({'usuario': usuario})

    if not user:
        print(f'⚠️ Tentativa de login com usuário inexistente: {usuario}')
        return {
            'success': False,
            'message': 'Usuário ou senha inválidos'  # Não especifica qual está errado
        }

    # Verifica se conta está ativa
    if not user.get('ativo', True):
        return {
            'success': False,
            'message': 'Conta desativada. Contate o administrador.'
        }

    # Verifica se conta está bloqueada
    bloqueado_ate = user.get('bloqueado_ate')
    if bloqueado_ate:
        if isinstance(bloqueado_ate, str):
            # Se estiver como string, considera como ainda bloqueado
            return {
                'success': False,
                'message': 'Conta temporariamente bloqueada. Tente novamente mais tarde.'
            }

    # Verifica senha
    if verificar_senha(senha, user['senha']):
        # Senha correta - Reseta tentativas e atualiza último login
        collect_users.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'ultimo_login': datetime.now(brt).strftime('%d/%m/%Y %H:%M:%S'),
                    'tentativas_login': 0,
                    'bloqueado_ate': None
                }
            }
        )

        print(f'✅ Login bem-sucedido: {usuario}')
        return {
            'success': True,
            'message': 'Login realizado com sucesso',
            'user': {
                'id': str(user['_id']),
                'usuario': user['usuario'],
                'nome_completo': user['nome_completo'],
                'email': user['email'],
                'role': user.get('role', 'user')
            }
        }
    else:
        # Senha incorreta - Incrementa tentativas
        tentativas = user.get('tentativas_login', 0) + 1

        update_data = {
            'tentativas_login': tentativas
        }

        # Bloqueia após 5 tentativas
        if tentativas >= 5:
            # Bloqueia por 15 minutos
            bloqueio = datetime.now(brt) + timedelta(minutes=15)
            update_data['bloqueado_ate'] = bloqueio.strftime('%d/%m/%Y %H:%M:%S')
            print(f'⚠️ Conta bloqueada por múltiplas tentativas: {usuario}')

        collect_users.update_one(
            {'_id': user['_id']},
            {'$set': update_data}
        )

        print(f'❌ Tentativa de login falhou: {usuario} (tentativa {tentativas})')

        mensagem = 'Usuário ou senha inválidos'
        if tentativas >= 5:
            mensagem = 'Conta bloqueada por 15 minutos devido a múltiplas tentativas falhas'

        return {
            'success': False,
            'message': mensagem,
            'tentativas': tentativas
        }


def alterar_senha(usuario, senha_antiga, senha_nova):
    """
    Altera a senha de um usuário

    Args:
        usuario (str): Nome de usuário
        senha_antiga (str): Senha atual
        senha_nova (str): Nova senha

    Returns:
        dict: Resultado da operação
    """
    # Busca usuário
    user = collect_users.find_one({'usuario': usuario})

    if not user:
        return {
            'success': False,
            'message': 'Usuário não encontrado'
        }

    # Verifica senha antiga
    if not verificar_senha(senha_antiga, user['senha']):
        return {
            'success': False,
            'message': 'Senha atual incorreta'
        }

    # Valida nova senha
    if len(senha_nova) < 6:
        return {
            'success': False,
            'message': 'A nova senha deve ter no mínimo 6 caracteres'
        }

    # Gera novo hash
    novo_hash = hash_senha(senha_nova)

    # Atualiza no banco
    collect_users.update_one(
        {'_id': user['_id']},
        {'$set': {'senha': novo_hash}}
    )

    print(f'✅ Senha alterada: {usuario}')
    return {
        'success': True,
        'message': 'Senha alterada com sucesso'
    }


def resetar_senha_admin(usuario, senha_nova):
    """
    Admin reseta senha de usuário (sem precisar da senha antiga)

    Args:
        usuario (str): Nome de usuário
        senha_nova (str): Nova senha

    Returns:
        dict: Resultado da operação
    """
    user = collect_users.find_one({'usuario': usuario})

    if not user:
        return {
            'success': False,
            'message': 'Usuário não encontrado'
        }

    # Gera novo hash
    novo_hash = hash_senha(senha_nova)

    # Atualiza no banco e reseta tentativas
    collect_users.update_one(
        {'_id': user['_id']},
        {
            '$set': {
                'senha': novo_hash,
                'tentativas_login': 0,
                'bloqueado_ate': None
            }
        }
    )

    print(f'✅ Senha resetada por admin: {usuario}')
    return {
        'success': True,
        'message': 'Senha resetada com sucesso'
    }


def listar_usuarios():
    """
    Lista todos os usuários (sem as senhas)

    Returns:
        list: Lista de usuários
    """
    usuarios = collect_users.find(
        {},
        {
            'senha': 0  # Não retorna a senha
        }
    )

    users_list = []
    for user in usuarios:
        user['_id'] = str(user['_id'])
        users_list.append(user)

    return users_list


def desativar_usuario(usuario):
    """
    Desativa um usuário (não deleta, apenas desativa)

    Args:
        usuario (str): Nome de usuário

    Returns:
        dict: Resultado da operação
    """
    result = collect_users.update_one(
        {'usuario': usuario},
        {'$set': {'ativo': False}}
    )

    if result.modified_count > 0:
        print(f'✅ Usuário desativado: {usuario}')
        return {
            'success': True,
            'message': 'Usuário desativado com sucesso'
        }
    else:
        return {
            'success': False,
            'message': 'Usuário não encontrado'
        }


# ========================================
# SCRIPT DE INICIALIZAÇÃO
# ========================================

def inicializar_usuarios():
    """
    Cria usuário admin padrão se não existir
    """
    admin_existente = collect_users.find_one({'usuario': 'admin'})

    if not admin_existente:
        print('📝 Criando usuário admin padrão...')
        resultado = criar_usuario(
            usuario='admin',
            senha='Admin@123',  # ALTERE ESSA SENHA DEPOIS!
            nome_completo='Administrador',
            email='admin@evolutecode.com',
            role='admin'
        )

        if resultado['success']:
            print('✅ Usuário admin criado!')
            print('⚠️  IMPORTANTE: Altere a senha padrão imediatamente!')
            print('   Usuário: admin')
            print('   Senha: Admin@123')
        else:
            print(f'❌ Erro ao criar admin: {resultado["message"]}')
    else:
        print('✅ Usuário admin já existe')


if __name__ == '__main__':
    # Testa o sistema
    print('🧪 Testando sistema de autenticação...')

    # Inicializa usuários
    inicializar_usuarios()

    # Teste de autenticação
    print('\n🔐 Testando autenticação...')
    resultado = autenticar_usuario('admin', 'Admin@123')
    print(f'Resultado: {resultado}')
    
