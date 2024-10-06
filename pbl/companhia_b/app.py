from flask import Flask, jsonify, request
from threading import Lock, Timer

app = Flask(__name__)

# Trechos de voos disponíveis para a Companhia B
voos = {
    "2": {"nome": "São Paulo-Curitiba", "poltronas": [1, 2, 3]},
}

reservas_temporarias = {}
reservas_confirmadas = {}
lock = Lock()
RESERVA_TIMEOUT = 30  # Tempo limite de reserva temporária

# Função para liberar reserva temporária após expiração
def liberar_reserva(cliente_id, voo_id, poltrona):
    with lock:
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

    with lock:
        if voo_id not in voos or int(poltrona) not in voos[voo_id]['poltronas']:
            return jsonify({'erro': 'Assento indisponível ou voo inválido'}), 400

        # Reservar assento temporariamente
        voos[voo_id]['poltronas'].remove(int(poltrona))
        reservas_temporarias[cliente_id] = {'voo': voos[voo_id]['nome'], 'poltrona': poltrona, 'voo_id': voo_id}

        Timer(RESERVA_TIMEOUT, liberar_reserva, [cliente_id, voo_id, int(poltrona)]).start()

        return jsonify({'mensagem': f'Poltrona {poltrona} reservada temporariamente no voo {voos[voo_id]["nome"]}'}), 200

# Rota para confirmar reservas temporárias
@app.route('/confirmar-reserva', methods=['POST'])
def confirmar_reserva():
    data = request.get_json()
    cliente_id = data['cliente_id']

    with lock:
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
    app.run(host='0.0.0.0', port=5001)
