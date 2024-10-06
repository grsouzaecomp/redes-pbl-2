from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Simulação de um banco de dados de usuários
usuarios = {}
# Simulação de um banco de dados de reservas
reservas = {}

# URLs das companhias aéreas
COMPANHIA_A_URL = "http://localhost:5000"
COMPANHIA_B_URL = "http://localhost:5001"
COMPANHIA_C_URL = "http://localhost:5002"

# Definição de viagens (cada viagem tem 3 trechos)
viagens = {
    "1": {
        "origem": "Belem",
        "destino": "Porto Alegre",
        "trechos": {
            "1": {"origem": "Belem", "destino": "São Paulo", "companhia": "A", "url": COMPANHIA_A_URL},
            "2": {"origem": "São Paulo", "destino": "Curitiba", "companhia": "B", "url": COMPANHIA_B_URL},
            "3": {"origem": "Curitiba", "destino": "Porto Alegre", "companhia": "C", "url": COMPANHIA_C_URL}
        }
    },
    "2": {
        "origem": "Rio de Janeiro",
        "destino": "São Paulo",
        "trechos": {
            "1": {"origem": "Rio de Janeiro", "destino": "São Paulo", "companhia": "A", "url": COMPANHIA_A_URL},
            "2": {"origem": "São Paulo", "destino": "Porto Alegre", "companhia": "B", "url": COMPANHIA_B_URL},
            "3": {"origem": "Porto Alegre", "destino": "Curitiba", "companhia": "C", "url": COMPANHIA_C_URL}
        }
    }
}

# Função para verificar se o usuário está logado
def login_requerido(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'cliente_id' not in session:
            flash('Por favor, faça login.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# Página inicial com as viagens
@app.route('/')
def index():
    return render_template('viagens.html', viagens=viagens)

# Rota para iniciar a reserva do primeiro trecho
@app.route('/reservar/<viagem_id>/<trecho_id>', methods=['GET', 'POST'])
@login_requerido
def reservar(viagem_id, trecho_id):
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

            # Mensagem de depuração
            print(f"Response do servidor para reserva: {resultado}, Status: {response.status_code}")

            if response.status_code == 200:
                # Armazenar a reserva
                if cliente_id not in reservas:
                    reservas[cliente_id] = []
                reservas[cliente_id].append({
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
            flash('Registro bem-sucedido! Agora você pode fazer login.', 'success')
            return redirect(url_for('login'))

    return render_template('registrar.html')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        senha = request.form['senha']

        # Verificar credenciais
        if cliente_id in usuarios and usuarios[cliente_id] == senha:
            session['cliente_id'] = cliente_id
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login ou senha incorretos', 'danger')

    return render_template('login.html')

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('cliente_id', None)
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('login'))

# Rota para visualizar reservas feitas
@app.route('/visualizar-reservas', methods=['GET'])
@login_requerido
def visualizar_reservas():
    cliente_id = session['cliente_id']
    usuario_reservas = reservas.get(cliente_id, [])
    return render_template('minhas_reservas.html', reservas=usuario_reservas)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
