from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from functools import wraps
import redis
import redis_lock

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuração do Redis para descentralização
redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

# URLs das companhias aéreas
COMPANHIA_A_URL = "http://localhost:5003"
COMPANHIA_B_URL = "http://localhost:5001"
COMPANHIA_C_URL = "http://localhost:5002"

# Definição de viagens (cada viagem tem 3 trechos)
viagens = {
    "1": {
        "origem": "São Paulo",
        "destino": "Porto Alegre",
        "trechos": {
            "1": {"origem": "São Paulo", "destino": "Rio de Janeiro", "companhia": "Companhia A", "url": COMPANHIA_A_URL},
            "2": {"origem": "Rio de Janeiro", "destino": "Curitiba", "companhia": "Companhia B", "url": COMPANHIA_B_URL},
            "3": {"origem": "Curitiba", "destino": "Porto Alegre", "companhia": "Companhia C", "url": COMPANHIA_C_URL}
        }
    },
    "2": {
        "origem": "Brasília",
        "destino": "Feira de Santana",
        "trechos": {
            "1": {"origem": "Brasília", "destino": "Belo Horizonte", "companhia": "Companhia A", "url": COMPANHIA_A_URL},
            "2": {"origem": "Belo Horizonte", "destino": "Salvador", "companhia": "Companhia B", "url": COMPANHIA_B_URL},
            "3": {"origem": "Salvador", "destino": "Feira de Santana", "companhia": "Companhia C", "url": COMPANHIA_C_URL}
        }
    },
    "3": {
        "origem": "Uberlândia",
        "destino": "Salvador",
        "trechos": {
            "1": {"origem": "Uberlândia", "destino": "Recife", "companhia": "Companhia A", "url": COMPANHIA_A_URL},
            "2": {"origem": "Recife", "destino": "Maceió", "companhia": "Companhia B", "url": COMPANHIA_B_URL},
            "3": {"origem": "Maceió", "destino": "Salvador", "companhia": "Companhia C", "url": COMPANHIA_C_URL}
        }
    },
    "4": {
        "origem": "São Paulo",
        "destino": "Florianópolis",
        "trechos": {
            "1": {"origem": "São Paulo", "destino": "Curitiba", "companhia": "Companhia A", "url": COMPANHIA_A_URL},
            "2": {"origem": "Curitiba", "destino": "Porto Alegre", "companhia": "Companhia B", "url": COMPANHIA_B_URL},
            "3": {"origem": "Porto Alegre", "destino": "Florianópolis", "companhia": "Companhia C", "url": COMPANHIA_C_URL}
        }
    },
    "5": {
        "origem": "Goiania",
        "destino": "Amazonas",
        "trechos": {
            "1": {"origem": "Goiania", "destino": "Cuiabá", "companhia": "Companhia B", "url": COMPANHIA_B_URL},
            "2": {"origem": "Cuiabá", "destino": "Campo Grande", "companhia": "Companhia C", "url": COMPANHIA_C_URL},
            "3": {"origem": "Campo Grande", "destino": "Amazonas", "companhia": "Companhia A", "url": COMPANHIA_A_URL}
        }
    },
     "6": {
        "origem": "Natal",
        "destino": "Amapá",
        "trechos": {
            "1": {"origem": "Fortaleza", "destino": "Natal", "companhia": "Companhia C", "url": COMPANHIA_C_URL},
            "2": {"origem": "Natal", "destino": "Belém", "companhia": "Companhia A", "url": COMPANHIA_A_URL},
            "3": {"origem": "Belém", "destino": "Amapá", "companhia": "Companhia B", "url": COMPANHIA_B_URL}
        }
     },
      "7": {
        "origem": "Salvador",
        "destino": "São Paulo",
        "trechos": {
            "1": {"origem": "Salvador", "destino": "Belo Horizonte", "companhia": "Companhia B", "url": COMPANHIA_B_URL},
            "2": {"origem": "Belo Horizonte", "destino": "Rio de Janeiro", "companhia": "Companhia C", "url": COMPANHIA_C_URL},
            "3": {"origem": "Rio de Janeiro", "destino": "São Paulo", "companhia": "Companhia A", "url": COMPANHIA_A_URL}
        }
      },
       "8": {
        "origem": "Manaus",
        "destino": "Cuiabá",
        "trechos": {
            "1": {"origem": "Manaus", "destino": "Boa Vista", "companhia": "Companhia C", "url": COMPANHIA_C_URL},
            "2": {"origem": "Boa Vista", "destino": "Brasília", "companhia": "Companhia B", "url": COMPANHIA_B_URL},
            "3": {"origem": "Brasília", "destino": "Cuiabá", "companhia": "Companhia A", "url": COMPANHIA_A_URL}
        }
     }
}

# Simulação de um banco de dados de usuários
usuarios = {}

# Função para verificar se o usuário está logado
def login_requerido(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'cliente_id' not in session:
            flash('Por favor, faça login.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# Rota para escolher o servidor
@app.route('/escolher-servidor', methods=['GET', 'POST'])
def escolher_servidor():
    if request.method == 'POST':
        servidor = request.form['servidor']
        session['servidor'] = servidor  # Armazenar o servidor na sessão
        flash(f"Conectado ao servidor {servidor}", 'success')
        return redirect(url_for('index'))

    servidores_disponiveis = {
        "1": "Servidor 1",
        "2": "Servidor 2",
        "3": "Servidor 3"
    }
    return render_template('escolher_servidor.html', servidores=servidores_disponiveis)

# Página inicial com as viagens
@app.route('/')
@login_requerido
def index():
    if 'servidor' not in session:
        return redirect(url_for('escolher_servidor'))
    return render_template('viagens.html', viagens=viagens)

# Rota para iniciar a reserva do primeiro trecho
@app.route('/reservar/<viagem_id>/<trecho_id>', methods=['GET', 'POST'])
@login_requerido
def reservar(viagem_id, trecho_id):
    # Verificar se o servidor foi escolhido
    if 'servidor' not in session:
        return redirect(url_for('escolher_servidor'))

    servidor_atual = session['servidor']
    trecho = viagens[viagem_id]["trechos"][trecho_id]

    if request.method == 'POST':
        cliente_id = session['cliente_id']
        poltrona = request.form['poltrona']

        # Enviar requisição de reserva para a companhia aérea correspondente
        data = {
            'cliente_id': cliente_id,
            'voo_id': trecho_id,
            'poltrona': poltrona
        }

        try:
            # Faça a requisição para a companhia
            response = requests.post(f"{trecho['url']}/reservar-assento", json=data)
            resultado = response.json()

            if response.status_code == 200:
                # Armazenar a reserva no Redis
                reserva_key = f"reserva:{cliente_id}:{servidor_atual}"
                redis_client.hset(reserva_key, mapping={
                    'trecho': f"{trecho['origem']} → {trecho['destino']}",
                    'poltrona': poltrona,
                    'status': 'Reservado'
                })

                flash(f"Reserva feita com sucesso: {resultado['mensagem']}", 'success')

                # Verificar se é o último trecho
                if trecho_id == "3":
                    flash("Todos os trechos reservados com sucesso.", "success")
                    return redirect(url_for('index'))  # Redireciona para a página inicial
                else:
                    next_trecho_id = str(int(trecho_id) + 1)
                    return redirect(url_for('reservar', viagem_id=viagem_id, trecho_id=next_trecho_id))  # Próximo trecho

            else:
                flash(f"Erro na reserva: {resultado.get('erro', 'Erro desconhecido')}", 'danger')

        except Exception as e:
            flash(f"Erro ao conectar com a companhia: {e}", 'danger')
            print(f"Erro ao conectar com a companhia: {e}")

    # Obter dados do voo atual para exibir ao cliente
    response = requests.get(f"{trecho['url']}/trechos-disponiveis")
    voos = response.json()

    return render_template('reservar.html', trecho=trecho, voos=voos[trecho_id])

# Rota de registro
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        senha = request.form['senha']

        if cliente_id in usuarios:
            flash('Cliente ID já registrado. Escolha outro.', 'danger')
        else:
            usuarios[cliente_id] = senha  # Armazenando a senha (não recomendado em produção)
            session['cliente_id'] = cliente_id
            flash('Registro bem-sucedido! Agora você pode escolher um servidor.', 'success')
            return redirect(url_for('escolher_servidor'))

    return render_template('registrar.html')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        senha = request.form['senha']

        # Verificar se o cliente existe
        if cliente_id not in usuarios:
            flash('Cliente não encontrado. Por favor, registre-se primeiro.', 'danger')
            return redirect(url_for('registrar'))

        # Verificar se a senha está correta
        if usuarios[cliente_id] != senha:
            flash('Senha incorreta. Por favor, tente novamente.', 'danger')
            return render_template('login.html')

        # Login bem-sucedido, armazenar o cliente na sessão
        session['cliente_id'] = cliente_id
        flash('Login bem-sucedido!', 'success')
        
        # Redirecionar para a escolha de servidor se ainda não foi escolhido
        if 'servidor' not in session:
            return redirect(url_for('escolher_servidor'))
        
        return redirect(url_for('index'))

    return render_template('login.html')

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('cliente_id', None)
    session.pop('servidor', None)  # Remover também o servidor da sessão
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('login'))

# Rota para visualizar reservas feitas
@app.route('/visualizar-reservas', methods=['GET'])
@login_requerido
def visualizar_reservas():
    cliente_id = session['cliente_id']
    servidor_atual = session['servidor']

    # Verificar se o servidor foi escolhido
    if not servidor_atual:
        flash('Você precisa escolher um servidor antes de visualizar as reservas.', 'danger')
        return redirect(url_for('escolher_servidor'))

    # Buscar reservas no Redis
    reserva_key = f"reserva:{cliente_id}:{servidor_atual}"
    reservas = [redis_client.hgetall(reserva_key)] if redis_client.exists(reserva_key) else []
    reservas_formatadas = [
        {
            'trecho': reserva[b'trecho'].decode(),
            'poltrona': reserva[b'poltrona'].decode(),
            'status': reserva[b'status'].decode()
        }
        for reserva in reservas
    ]

    return render_template('reservar.html', reservas=reservas_formatadas)

if __name__ == '__main__':
    app.run(debug=True)
