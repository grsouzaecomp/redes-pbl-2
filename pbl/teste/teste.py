import threading
import requests
import time
import random

# URL base da aplicação Flask
BASE_URL = "http://127.0.0.1:5003"

# Credenciais de exemplo para o login
CLIENTE_ID = "cliente_teste"
SENHA = "senha_teste"

# Número de threads para o teste
NUM_THREADS = 10

# Lista de servidores para escolher
SERVIDORES = ["1", "2", "3"]

def simular_cliente(thread_id):
    session = requests.Session()  # Cria uma sessão para cada cliente
    print(f"Thread {thread_id}: Iniciando sessão de teste.")

    # 1. Registrar o cliente (somente na primeira vez)
    response = session.post(f"{BASE_URL}/registrar", data={"cliente_id": f"{CLIENTE_ID}_{thread_id}", "senha": SENHA})
    if response.status_code == 200:
        print(f"Thread {thread_id}: Cliente registrado com sucesso.")
    else:
        print(f"Thread {thread_id}: Cliente já registrado ou erro.")

    # 2. Fazer login
    response = session.post(f"{BASE_URL}/login", data={"cliente_id": f"{CLIENTE_ID}_{thread_id}", "senha": SENHA})
    if response.status_code == 200:
        print(f"Thread {thread_id}: Login realizado com sucesso.")
    else:
        print(f"Thread {thread_id}: Erro ao fazer login.")
        return

    # 3. Escolher um servidor aleatoriamente
    servidor_escolhido = random.choice(SERVIDORES)
    response = session.post(f"{BASE_URL}/escolher-servidor", data={"servidor": servidor_escolhido})
    if response.status_code == 200:
        print(f"Thread {thread_id}: Escolheu o servidor {servidor_escolhido} com sucesso.")
    else:
        print(f"Thread {thread_id}: Erro ao escolher servidor.")
        return

    # 4. Fazer uma reserva de assento em um trecho específico
    viagem_id = "1"
    trecho_id = "1"
    response = session.get(f"{BASE_URL}/reservar/{viagem_id}/{trecho_id}")
    if response.status_code == 200:
        # Selecionar uma poltrona
        poltrona = f"{random.randint(1, 30)}A"  # Gera um número de poltrona aleatório para cada thread
        response = session.post(f"{BASE_URL}/reservar/{viagem_id}/{trecho_id}", data={"poltrona": poltrona})
        if response.status_code == 200:
            print(f"Thread {thread_id}: Reserva realizada com sucesso para a poltrona {poltrona} no servidor {servidor_escolhido}.")
        else:
            print(f"Thread {thread_id}: Falha ao reservar poltrona.")
    else:
        print(f"Thread {thread_id}: Erro ao acessar a página de reserva.")

    # 5. Finalizar a sessão
    session.close()
    print(f"Thread {thread_id}: Sessão finalizada.")

# Função principal para iniciar as threads
def main():
    threads = []
    for i in range(NUM_THREADS):
        thread = threading.Thread(target=simular_cliente, args=(i,))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # Intervalo pequeno entre o início de cada thread

    for thread in threads:
        thread.join()  # Aguarda todas as threads terminarem

if __name__ == "__main__":
    main()