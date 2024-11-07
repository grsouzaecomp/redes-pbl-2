from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definição da tabela de reservas
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.String(100), nullable=False)
    trecho = db.Column(db.String(200), nullable=False)
    poltrona = db.Column(db.String(10), nullable=False)
    servidor = db.Column(db.String(50), nullable=False)

# Inicializa o banco de dados
with app.app_context():
    db.create_all()

# Simulação de um banco de dados de usuários
usuarios = {}

# URLs das companhias aéreas
COMPANHIA_A_URL = "http://localhost:5000"
COMPANHIA_B_URL = "http://localhost:5001"
COMPANHIA_C_URL = "http://localhost:5002"

# Definição de viagens
viagens = {
    "1": {
        "origem": "Belem",
        "destino": "Porto Alegre",
        "trechos": {
            "1": {"origem": "Belem", "destino": "São Paulo", "companhia": "Companhia A", "url": COMPANHIA_A_URL},
            "2": {"origem": "São Paulo", "destino": "Curitiba", "companhia": "Companhia B", "url": COMPANHIA_B_URL},
            "3": {"origem": "Curitiba", "destino": "Porto Alegre", "companhia": "Companhia C", "url": COMPANHIA_C_URL}
        }
    },
    "2": {
        "origem": "São Paulo",
        "destino": "Salavor",
        "trechos": {
            "4": {"origem":"São Paulo", "destino": "Brasília", "companhia": "Companhia A", "url": COMPANHIA_A_URL},
            "5": {"origem":"Brasília", "destino": "Belo Horizonte", "companhia": "Companhia B", "url": COMPANHIA_B_URL},
            "6": {"origem":"Belo Horizonte", "destino": "Salvador", "companhia": "Companhia C", "url": COMPANHIA_C_URL}
        }
    },
    "3": {
        "origem": "Rio de Janeiro",
        "destino": "Salvador",
        "trechos": {
            "7": {"origem":"Rio de Janeiro", "destino": "Recife", "companhia": "Companhia A", "url": COMPANHIA_A_URL},
            "8": {"origem":"Recife", "destino": "Maceió", "companhia": "Companhia B", "url": COMPANHIA_B_URL},
            "9": {"origem":"Maceió", "destino": "Salvador", "companhia": "Companhia C", "url": COMPANHIA_C_URL}
        }
    },
    "4": {
        "origem": "São Paulo",
        "destino": "Florianopólis",
        "trechos": {
            "10": {"origem":"São Paulo", "destino": "Curitiba", "companhia":"Companhia A", "url": COMPANHIA_A_URL},
            "11": {"origem":"Curitiba", "destino": "Porto Alegre", "companhia": "Companhia B", "url": COMPANHIA_B_URL},
            "12": {"origem":"Porto Alegre", "destino": "Florianópolis", "companhia": "Companhia C", "url": COMPANHIA_C_URL}
        }
    },
    "5": {
        "origem": "Brasília",
        "destino": "Campo Grande",
        "trechos": {
            "13": {"origem":"Brasília", "destino": "Goiânia","companhia":"Companhia A", "url": COMPANHIA_A_URL},
            "14": {"origem":"Goiânia", "destino": "Cuiabá","companhia":"Companhia B", "url": COMPANHIA_B_URL},
            "15": {"origem":"Cuiabá", "destino": "Campo Grande","companhia":"Companhia C", "url": COMPANHIA_C_URL}
        }
    },
    "6": {
        "origem": "Fortaleza",
        "destino": "Recife",
        "trechos": {
            "16": {"origem":"Fortaleza", "destino": "Natal", "companhia":"Companhia A", "url": COMPANHIA_A_URL},
            "17": {"origem":"Natal", "destino": "João Pessoa", "companhia":"Companhia B", "url": COMPANHIA_B_URL},
            "18": {"origem":"João Pessoa", "destino": "Recife", "companhia":"Companhia C", "url": COMPANHIA_C_URL}
        }
    },
    "7": {
        "origem": "Salvador",
        "destino": "São Paulo",
        "trechos": {
            "19": {"origem":"Salvador", "destino": "Belo Horizonte", "companhia":"Companhia A", "url": COMPANHIA_A_URL},
            "20": {"origem":"Belo Horizonte", "destino": "Rio de Janeiro", "companhia":"Companhia B", "url": COMPANHIA_B_URL},
            "21": {"origem":"Rio de Janeiro", "destino": "São Paulo", "companhia":"Companhia C", "url": COMPANHIA_C_URL}
        }
    },
    "8": {
        "origem": "Manaus",
        "destino": "São Paulo",
        "trechos": {
            "22": {"origem":"Manaus", "destino": "Boa Vista", "companhia":"Companhia A", "url": COMPANHIA_A_URL},
            "23": {"origem":"Boa Vista", "destino": "Brasília", "companhia":"Companhia B", "url": COMPANHIA_B_URL},
            "24": {"origem":"Brasília", "destino": "São Paulo", "companhia":"Companhia C", "url": COMPANHIA_C_URL}
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

# Rota para escolher o servidor
@app.route('/escolher-servidor', methods=['GET', 'POST'])
def escolher_servidor():
    if request.method == 'POST':
        servidor = request.form['servidor']
        session['servidor'] = servidor
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

# Rota para visualizar reservas
@app.route('/minhas_reservas')
@login_requerido
def minhas_reservas():
    cliente_id = session['cliente_id']
    servidor_atual = session['servidor']
    reservas = Reserva.query.filter_by(cliente_id=cliente_id, servidor=servidor_atual).all()
    return render_template('minhas_reservas.html', reservas=reservas)

# Rota para iniciar a reserva do primeiro trecho
@app.route('/reservar/<viagem_id>/<trecho_id>', methods=['GET', 'POST'])
@login_requerido
def reservar(viagem_id, trecho_id):
    if 'servidor' not in session:
        return redirect(url_for('escolher_servidor'))

    servidor_atual = session['servidor']
    trecho = viagens[viagem_id]["trechos"][trecho_id]

    if request.method == 'POST':
        cliente_id = session['cliente_id']
        poltrona = request.form['poltrona']

        data = {
            'cliente_id': cliente_id,
            'voo_id': trecho_id,
            'poltrona': poltrona
        }

        try:
            response = requests.post(f"{trecho['url']}/reservar-assento", json=data)
            resultado = response.json()

            if response.status_code == 200:
                # Salva no banco de dados
                reserva = Reserva(cliente_id=cliente_id, trecho=f"{trecho['origem']} → {trecho['destino']}", poltrona=poltrona, servidor=servidor_atual)
                db.session.add(reserva)
                db.session.commit()

                flash(f"Reserva feita com sucesso: {resultado['mensagem']}", 'success')

                if trecho_id == "3":
                    flash("Todos os trechos reservados com sucesso.", "success")
                    return redirect(url_for('index'))
                else:
                    next_trecho_id = str(int(trecho_id) + 1)
                    return redirect(url_for('reservar', viagem_id=viagem_id, trecho_id=next_trecho_id))

            else:
                flash(f"Erro na reserva: {resultado.get('erro', 'Erro desconhecido')}", 'danger')

        except Exception as e:
            flash(f"Erro ao conectar com a companhia: {e}", 'danger')

    # Carregar as poltronas disponíveis
    try:
        response = requests.get(f"{trecho['url']}/trechos-disponiveis")
        voos = response.json()
        poltronas_disponiveis = voos[trecho_id]['poltronas']
    except Exception as e:
        flash(f"Erro ao obter as poltronas disponíveis: {e}", 'danger')
        poltronas_disponiveis = []

    return render_template('reservar.html', trecho=trecho, voos={"poltronas": poltronas_disponiveis})

# Rota de registro
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        senha = request.form['senha']

        if cliente_id in usuarios:
            flash('Cliente ID já registrado. Escolha outro.', 'danger')
        else:
            usuarios[cliente_id] = senha
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

        if cliente_id not in usuarios:
            flash('Cliente não encontrado. Por favor, registre-se primeiro.', 'danger')
            return redirect(url_for('registrar'))

        if usuarios[cliente_id] != senha:
            flash('Senha incorreta. Por favor, tente novamente.', 'danger')
            return render_template('login.html')

        session['cliente_id'] = cliente_id
        flash('Login bem-sucedido!', 'success')
        
        if 'servidor' not in session:
            return redirect(url_for('escolher_servidor'))
        
        return redirect(url_for('index'))

    return render_template('login.html')

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('cliente_id', None)
    session.pop('servidor', None)
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5003)
