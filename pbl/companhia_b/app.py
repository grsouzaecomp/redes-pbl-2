from flask import Flask, jsonify, request
from threading import Lock, Timer
import redis
import redis_lock

app = Flask(__name__)

# Configurar conexão com o Redis distribuído
redis_client = redis.StrictRedis(host='redis_host', port=6379, db=0)

voos = {
    "2": {"nome": "Rio de Janeiro-Curitiba", "poltronas": [1, 2, 3]},
    "5": {"nome": "Belo Horizonte-Salvador", "poltronas": [9, 10, 20]},
    "8": {"nome": "Recife-Maceió", "poltronas": [13, 14, 17]},
    "11": {"nome": "Curitiba-Porto Alegre", "poltronas": [22, 23, 24]},
    "14": {"nome": "Goiânia-Cuiabá", "poltronas": [22, 23, 24]},
    "17": {"nome": "Belém-Amapá", "poltronas": [22, 23, 24]},
    "20": {"nome": "Salvador-Belo Horizonte", "poltronas": [2, 8, 10]},
    "23": {"nome": "Boa Vista-Brasília", "poltronas": [10, 19, 13]},
}

reservas_temporarias = {}
reservas_confirmadas = {}
lock = Lock()
RESERVA_TIMEOUT = 30

def liberar_reserva(cliente_id, voo_id, poltrona):
    with lock:
        if cliente_id in reservas_temporarias:
            reservas_temporarias.pop(cliente_id)
            voos[voo_id]['poltronas'].append(poltrona)
            print(f"Reserva do cliente {cliente_id} expirou. Poltrona {poltrona} liberada no voo {voos[voo_id]['nome']}")

@app.route('/trechos-disponiveis', methods=['GET'])
def listar_trechos():
    return jsonify(voos)

@app.route('/reservar-assento', methods=['POST'])
def reservar_assento():
    data = request.get_json()
    cliente_id = data['cliente_id']
    voo_id = data['voo_id']
    poltrona = data['poltrona']
    
    lock_key = f"lock_voo_{voo_id}_poltrona_{poltrona}"

    with redis_lock.Lock(redis_client, lock_key, expire=30):
        with lock:
            if voo_id not in voos or int(poltrona) not in voos[voo_id]['poltronas']:
                return jsonify({'erro': 'Assento indisponível ou voo inválido'}), 400

            voos[voo_id]['poltronas'].remove(int(poltrona))
            reservas_temporarias[cliente_id] = {'voo': voos[voo_id]['nome'], 'poltrona': poltrona, 'voo_id': voo_id}

            Timer(RESERVA_TIMEOUT, liberar_reserva, [cliente_id, voo_id, int(poltrona)]).start()

        return jsonify({'mensagem': f'Poltrona {poltrona} reservada temporariamente no voo {voos[voo_id]["nome"]}'}), 200

@app.route('/confirmar-reserva', methods=['POST'])
def confirmar_reserva():
    data = request.get_json()
    cliente_id = data['cliente_id']

    with lock:
        if cliente_id not in reservas_temporarias:
            return jsonify({'erro': 'Nenhuma reserva temporária encontrada para esse cliente'}), 400

        reserva = reservas_temporarias.pop(cliente_id)
        reservas_confirmadas[cliente_id] = reserva

        return jsonify({'mensagem': f'Reserva confirmada para o voo {reserva["voo"]} na poltrona {reserva["poltrona"]}.'}), 200

@app.route('/minhas-reservas/<cliente_id>', methods=['GET'])
def ver_reservas(cliente_id):
    reservas = []
    if cliente_id in reservas_confirmadas:
        reservas.append(reservas_confirmadas[cliente_id])
    return jsonify({'reservas': reservas})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
