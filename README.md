<div align="center">
  <h1>
      Relatório do Problema 2: Sistema de Reservas de Assentos com Múltiplos Servidores
  </h1>

  <h3>
    Gabriel Ribeiro Souza & Kevin Cordeiro Borges
  </h3>

  <p>
    Engenharia de Computação – (UEFS)  
    Av. Transnordestina, s/n, Novo Horizonte  
    Feira de Santana – Bahia, Brasil – 44036-900
  </p>

  <center>gabasribeirosz@gmail.com & kcordeiro539@gmail.com</center>
</div>

# 1. Introdução

<p style="text-align: justify;">
  O gerenciamento eficaz de reservas de assentos é uma necessidade comum em sistemas de transporte e turismo. Neste segundo problema, foi proposto o desenvolvimento de um sistema de reserva de assentos distribuído, com múltiplos servidores responsáveis por gerenciar diferentes trechos de uma mesma viagem. Para garantir a disponibilidade e o controle eficiente das reservas, cada servidor representa uma companhia aérea específica e é responsável pela reserva de um trecho específico dentro de uma viagem completa.
</p>

<p style="text-align: justify;">
  O sistema utiliza uma arquitetura distribuída, onde o cliente interage com diferentes servidores para realizar reservas, e as informações são armazenadas em um banco de dados centralizado. Cada servidor oferece suporte a múltiplas conexões simultâneas, permitindo que vários clientes interajam com o sistema ao mesmo tempo. A aplicação foi desenvolvida em Python utilizando Flask para a comunicação cliente-servidor via HTTP e threads para tratar as conexões concorrentes.
</p>

# 2. Metodologia

<p style="text-align: justify;">
  A arquitetura do sistema é composta por três partes principais: cliente, servidores de reservas e um banco de dados centralizado. Cada servidor representa uma companhia aérea que gerencia as reservas para um trecho específico de uma viagem, e o banco de dados centralizado armazena as reservas realizadas em todos os servidores. A comunicação entre cliente e servidor é feita via HTTP, com o cliente enviando solicitações RESTful para autenticação, escolha de servidor e reserva de assentos.
</p>

<p style="text-align: justify;">
   O diagrama a seguir, exibe como é feita a conexão entre o cliente e os servidores, por meio de uma interface principal, responsável pelo gerenciamento dos trechos ofertados por cada servidor:
</p>

![Conexão entre Servidor e Cliente](https://github.com/user-attachments/assets/9de5a24b-d21a-4861-9952-9de69e19192e)

## 2.1 Arquitetura e Protocolo de Comunicação

<p style="text-align: justify;">
  O sistema utiliza o protocolo HTTP sobre TCP/IP para garantir a confiabilidade das conexões e a entrega ordenada dos dados. As operações RESTful permitem que o cliente interaja com o sistema de maneira intuitiva, com rotas específicas para registrar, autenticar, escolher servidor, e fazer reservas. Cada reserva é realizada em um servidor específico, e os dados são armazenados em um banco de dados SQLite centralizado.
</p>

<p style="text-align: justify;">
  As principais rotas do sistema incluem:
</p>

<ul>
  <li><b>POST /registrar:</b> Permite ao cliente criar uma conta no sistema.</li>
  <li><b>POST /login:</b> Autentica o cliente com base nas credenciais fornecidas.</li>
  <li><b>POST /escolher-servidor:</b> Permite ao cliente selecionar o servidor com o qual deseja interagir para reservas.</li>
  <li><b>GET e POST /reservar/&lt;viagem_id&gt;/&lt;trecho_id&gt;:</b> Permite ao cliente visualizar detalhes do trecho e reservar um assento em uma poltrona específica.</li>
  <li><b>GET /visualizar-reservas:</b> Mostra as reservas já confirmadas para o cliente.</li>
</ul>

<p style="text-align: justify">
  O diagrama a seguir mostra o fluxo de uso do Programa a partir do momento que o cliente entra no link até a efetuação de uma compra:
</p>

  ![Fluxo de Compra](https://github.com/user-attachments/assets/888d26d7-ba83-4aba-952c-3ef1d81c0b52)

## 2.2 Controle de Concorrência e Tratamento de Conexões Simultâneas

<p style="text-align: justify;">
  Para garantir a capacidade do sistema de lidar com múltiplos acessos simultâneos, cada servidor utiliza threads para tratar as conexões de diferentes clientes. Cada cliente é gerenciado por uma thread separada, permitindo que as operações de reserva ocorram de forma paralela. Além disso, foram implementados mecanismos de verificação para evitar que múltiplos clientes reservem a mesma poltrona ao mesmo tempo, garantindo a integridade das informações no banco de dados.
</p>

<p style="text-align: justify;">
  As threads permitem que o servidor aceite e trate múltiplas requisições ao mesmo tempo, oferecendo escalabilidade e suporte a vários clientes simultâneos. Cada reserva é tratada como uma operação atômica, o que impede conflitos e garante que o sistema funcione corretamente mesmo com alta demanda.
</p>

---

# 3. Resultados

<p style="text-align: justify;">
  Foram realizados testes com múltiplos clientes simulados em diferentes servidores, utilizando threads para simular acessos concorrentes. Cada cliente foi capaz de escolher um servidor, realizar reservas e visualizar suas reservas confirmadas. O sistema foi executado com sucesso, demonstrando ser capaz de tratar múltiplos acessos simultâneos e garantir a integridade das reservas.
</p>

## 3.1 Testes com Vários Clientes e Servidores

<p style="text-align: justify;">
  Utilizamos um script de testes automatizado que lança múltiplas threads para simular clientes interagindo com o sistema de reservas em diferentes servidores. Os testes foram realizados com 10 threads simultâneas, cada uma escolhendo aleatoriamente entre os servidores disponíveis (1, 2 ou 3) para simular o uso real em um ambiente distribuído. Os resultados indicaram que o sistema conseguiu gerenciar múltiplas requisições de forma eficiente, com cada servidor respondendo corretamente ao cliente.
</p>

<p style="text-align: justify;">
  O sistema demonstrou um bom desempenho durante os testes, processando as reservas sem conflitos, mesmo com múltiplos clientes tentando reservar assentos ao mesmo tempo. A divisão das reservas por servidor foi feita de forma equilibrada, com cada servidor registrando reservas em um banco de dados centralizado, permitindo um controle unificado de todas as reservas realizadas.
</p>

## 3.2 Gerenciamento de Dispositivo

<p style="text-align: justify">
 O gerenciamento de dispositivos ou configurações remotas específicas para cada servidor (como iniciar, parar ou alterar valores) não é implementado diretamente. No entanto, as operações de autenticação e escolha de servidor permitem que o cliente selecione qual servidor acessar para realizar as reservas.
</p>

## 3.3. Desempenho
<p style="text-align: justify">
 A aplicação utiliza threads para aumentar a eficiência no atendimento a múltiplas requisições simultâneas. O desempenho é otimizado pelo uso de threads, que permite que o servidor responda a várias requisições de reserva em paralelo.
</p>

# 4. Conclusão

<p style="text-align: justify;">
  O desenvolvimento do sistema de reservas com múltiplos servidores demonstrou ser eficaz para gerenciar reservas de assentos em um ambiente distribuído, com diferentes servidores representando companhias aéreas e permitindo reservas de trechos específicos de uma viagem completa. A arquitetura baseada em threads e o uso de um banco de dados centralizado garantiram a integridade das reservas e permitiram o atendimento de múltiplos clientes simultaneamente.
</p>

<p style="text-align: justify;">
  A implementação mostrou-se robusta e escalável para o uso em situações reais, e o sistema foi capaz de evitar conflitos de reserva e garantir a consistência dos dados. Futuras melhorias podem incluir o uso de um cache para otimizar o desempenho em ambientes com alta demanda, bem como a criação de uma interface gráfica para tornar o sistema mais acessível e intuitivo para os usuários finais.
</p>

# Referências

<p style="text-align: justify;">
  Introdução a Flask e SQLAlchemy para sistemas web. Disponível em: https://flask.palletsprojects.com/en/2.0.x/. Acesso em: 17 de outubro de 2024.
</p>

<p style="text-align: justify;">
  Python Threading para Programação Concorrente, 2024. Disponível em: https://docs.python.org/3/library/threading.html. Acesso em: 20 de outubro de 2024.
</p>

<p style="text-align: justify;">
  Redes de Computadores e Comunicação Cliente-Servidor. Engenharia de Computação - Universidade Estadual de Feira de Santana (UEFS). Acesso em: 1 de outubro de 2024.
</p>

 
