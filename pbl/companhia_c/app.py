from flask import Flask, jsonify, request
import redis
from threading import Timer

app = Flask(__name__)

# Conectar ao Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Trechos de voos disponíveis para a Companhia C
voos = {
    "3": {"nome": "Curitiba-Porto Alegre", "poltronas": [1, 2, 3]},
    "6": {"nome": "Belo Horizonte-Salvador", "poltronas": [4, 5, 6]},
    "9": {"nome": "Maceió-Salvador", "poltronas": [20, 23, 29]},
    "12": {"nome": "Porto Alegre-Florianópolis", "poltronas": [12, 17, 19]},
    "15": {"nome": "Cuiabá-Campo Grande", "poltronas": [21, 24, 27]},
    "18": {"nome": "João Pessoa-Recife", "poltronas": [1, 2, 3]},
    "21": {"nome": "Rio de Janeiro-São Paulo", "poltronas": [2, 9, 24]},
    "24": {"nome": "Brasília-São Paulo", "poltronas": [10, 12, 33]},
}

reservas_temporarias = {}
reservas_confirmadas = {}
RESERVA_TIMEOUT = 30  # Tempo limite de reserva temporária

# Função para liberar reserva temporária após expiração
def liberar_reserva(cliente_id, voo_id, poltrona):
    if cliente_id in reservas_temporarias:
        reservas_temporarias.pop(cliente_id)
        voos[voo_id]['poltronas'].append(poltrona)
        print(f"Reserva do cliente {cliente_id} expirou. Poltrona {poltrona} liberada no voo {voos[voo_id]['nome']}")

# Rota para listar trechos e assentos disponíveis
@app.route('/trechos-disponiveis', methods=['GET'])
def listar_trechos():
    return jsonify(voos)

# Rota para reservar um assento temporariamente
@app.route('/reservar-assento', methods=['POST'])
def reservar_assento():
    data = request.get_json()
    cliente_id = data['cliente_id']
    voo_id = data['voo_id']
    poltrona = data['poltrona']

    # Tenta obter um lock no Redis
    lock_key = f"lock:{voo_id}:{poltrona}"
    if redis_client.set(lock_key, "locked", nx=True, ex=RESERVA_TIMEOUT):
        if voo_id not in voos or int(poltrona) not in voos[voo_id]['poltronas']:
            redis_client.delete(lock_key)  # Libera o lock
            return jsonify({'erro': 'Assento indisponível ou voo inválido'}), 400

        # Reservar assento temporariamente
        voos[voo_id]['poltronas'].remove(int(poltrona))
        reservas_temporarias[cliente_id] = {'voo': voos[voo_id]['nome'], 'poltrona': poltrona, 'voo_id': voo_id}

        Timer(RESERVA_TIMEOUT, liberar_reserva, [cliente_id, voo_id, int(poltrona)]).start()

        return jsonify({'mensagem': f'Poltrona {poltrona} reservada temporariamente no voo {voos[voo_id]["nome"]}'}), 200
    else:
        return jsonify({'erro': 'Assento já reservado por outro cliente'}), 400

# Rota para confirmar reservas temporárias
@app.route('/confirmar-reserva', methods=['POST'])
def confirmar_reserva():
    data = request.get_json()
    cliente_id = data['cliente_id']

    if cliente_id not in reservas_temporarias:
        return jsonify({'erro': 'Nenhuma reserva temporária encontrada para esse cliente'}), 400

    # Confirmar a reserva e movê-la para reservas confirmadas
    reserva = reservas_temporarias.pop(cliente_id)
    reservas_confirmadas[cliente_id] = reserva

    return jsonify({'mensagem': f'Reserva confirmada para o voo {reserva["voo"]} na poltrona {reserva["poltrona"]}.'}), 200

# Rota para visualizar reservas feitas
@app.route('/minhas-reservas/<cliente_id>', methods=['GET'])
def ver_reservas(cliente_id):
    reservas = []
    if cliente_id in reservas_confirmadas:
        reservas.append(reservas_confirmadas[cliente_id])
    return jsonify({'reservas': reservas})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
