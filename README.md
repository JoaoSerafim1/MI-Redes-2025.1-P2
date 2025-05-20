# Sistemas distribuídos - Recarga de Veículos Elétricos com protocolo MQTT e HTTP-REST

Chamamos sistemas distribuídos aqueles compostos por várias instâncias individuais de aplicação, costumeiramente de dois ou mais tipos distintos, que trabalham em conjunto para prover um serviço em massa.

No contexto do MI de Concorrência e Conectividade da UEFS, semestre 2025.1, foi requisitado aos alunos a confecção de um sistema distribuído capaz de coordenar a recarga de veículos elétricos, além de monitorar o nível de carga dos veículos no qual a versão de usuário final está instanciada, e fornecer informações acerca do histórico de compras (recargas) de um usuário final.

O sistema aqui desenvolvido conta com 3 versões, cada uma destinada a ser executada por um agente distinto:
- Servidor: Aplicação pertencente aos provedores do serviço. Recebe requisicões das aplicações-cliente (veículo/usuário final e estação de recarga) e de outros servidores, validando, executando e registrando tão requisições.
- Estação de recarga: Software instalado em computadores de cada ponto de recarga. Rotineiramente "pergunta" ao servidor se existe veículo a ser recarregado, caso disponível.
- Veículo (usuário final): Programa responsável por prover a um motorista de automóvel a opção de requisitar serviços de recarga por meio de pagamento, reservar pontos em horários desejado e visualizar compras bem-sucedidas registradas em um determinado servidor. Como dito anteriormente, também monitora o nível de carga do veículo no qual é instalado.
  
# Instalação e uso da aplicação

## Requisitos básicos
- Sistema Operacional compatível com protocolo TCP-IP e Python (ex: [Ubuntu](https://ubuntu.com/download), [Windows](https://www.microsoft.com/pt-br/windows/))
- [Python](https://www.python.org/downloads/) 3.9
- [Biblioteca Paho-MQTT](https://pypi.org/project/paho-mqtt/) para Python:

  ```
  pip3 install requests --break-system-packages
  ```
  ##### (Instala, DE FORMA FORÇADA, a biblioteca em sistemas tipo Linux, consulte documentação do componente para fazer o mesmo em outros sistemas operacionais)

## Recursos Adicionais
- Servidor: Broker MQTT (ex: [Eclipse Mosquitto](https://mosquitto.org/download/))
  
## 📦 Instalando e utilizando as diferentes versões do sistema distribuído

As versões do sistema destinadas a usuários distintos estão disponíveis individualmente neste repositório online, em formato .zip, na sessão "Releases" (encontrada no canto direito da tela inicial do repositório na maioria dos navegadores).

### ☁️ Servidor
#### AVISO: O servidor faz uso da [biblioteca requests](https://pypi.org/project/requests/) do Python para a comunicação com outros servidores. Tal biblioteca não faz parte do pacote básico da linguagem.
```
  pip3 install requests --break-system-packages
```
##### (Instala, DE FORMA FORÇADA, a biblioteca em sistemas tipo Linux, consulte documentação do componente para fazer o mesmo em outros sistemas operacionais)

O arquivo .zip do servidor possui ```server``` antes de seu número de versão. Para iniciar o programa do servidor, execute o arquivo ```server.py```, encontrado no diretório principal da aplicação. Após a inicialização, será pedido au usuário do sistema que insira um endereço para o broker MQTT, sempre na porta TCP 1883. Caso deseje usar um broker MQTT que está rodando com o mesmo endereço do servidor, também na porta TCP 1883, pressione ENTER sem prover entrada alguma.

Nota: Utilizar a entrada "test" resulta na escolha de um broker MQTT de teste pre-definido, por padrão aquele da [EMQX](https://www.emqx.com/en/mqtt/public-mqtt5-broker) (endereço: broker.emqx.io, porta TCP 1883).

![Tela inicial](/imgs/server_waiting.png?raw=true "Instruções do início do programa e prompt de entrada do broker MQTT")

Após o cadastro de uma estação de carga, o servidor automaticamente gerará um novo ID que deverá ser utilizado na próxima operação do tipo, e em seguida exibirá na tela tal informação.

![Tela inicial apos cadastrar primeira estação de carga](/imgs/server_after_station.png?raw=true "Resultado no terminal de uma operação de cadastro de estação de carga")

O recebimento de mensagens, bem como a execução de ações em cima do banco de dados do servidor, são todas operações registrados em arquivos de texto (logs), os quais podem ser encontrados nas pastas ```/logs/received/``` (recados/requisições lidos/recebidas) e ```logs/performed/``` (ações executadas pelo servidor).

Logs possuem o seguinte formato:
- Título: YYYY-MM-DDD = Data local
- Conteúdo:
  - [YYYY-MM-DDD hh:mm:ss.ssssss] => Data e horário locais (24 horas)
  - NAME:
  - NOME-DA-ENTRADA => Informação do nome da entrada no log
    - RVMQTT:        Recado MQTT lido
    - HTTPREQUEST:   Requisição HTTP recebida
    - RGTSTATION:    Registrar nova estação
    - RGTVEHICLE:    Registrar novo veículo
    - GETBOOKED:     Obter informações acerca de possível veículo agendado (estação)
    - FREESPOT:      Liberar estação para agendamento
    - GETDISTANCE:   Obter e retornar informações da estação dispónível mais próxima de um veículo
    - RTDETAILS:     Obter informações de uma rota em específico
    - RESROUTE:      Reservar uma rota
    - PHCCHARGE:     Confirmar pagamento e agendar recarga
    - PCHDETAILS:    Obter e retornar informações de uma determinada compra (de acordo com o ID do veículo vinculado à compra e ao índice da compra)
  - TIPO-DA-ENTIDADE => Tipo do identificador da entidade que gerou a entrada
    - ADDRESS:       Endereço IP (tipo de usuário não-definido)
    - S_ID:          ID de estação de carga
    - V_ID:          ID de veículo
    - V_ADD:         Endereço IP de um usuário que supõe-se ser um veículo
  - IDENTIFICADOR-DA-ENTIDADE => Identificador da entidade que gerou a entrada

![Tela do arquivo de texto de um log](/imgs/server_log.png?raw=true "Log referentes às ações executadas pelo servidor no dia 04 de Abril de 2025, data local")

Pressionar a tecla ENTER durante a execução do servidor inicia o processo de encerramento da aplicação, como já explicitado anteriormente na saída do terminal.

Nota: Por questões de limitações do código, é necessário enviar uma requisição HTTP qualquer ao endereço do servidor, porta 2025, para que ocorra o encerramento correto do programa. No entanto, reiniciar o sistema da máquina do servidor também soluciona o impasse (caso seja impossível o envio de uma requisição HTTP). Tendo em vista que todas as operações de dados ocorrem em cima do sistema de arquivos, é seguro reiniciar o sistema a qualquer momento após iniciar o processo de encerramento do programa, mesmo que este não seja concluído.

![Tela de encerramento](/imgs/server_termination.png?raw=true "Resultado da sequência de encerramento do servidor")

### 🔋 Estação de Carga

O arquivo .zip da estação possui ```station``` antes de seu número de versão. Para iniciar o programa referente à estação de carga, execute o arquivo ```client.py```, encontrado no diretório principal da aplicação. Ao usuário será pedida a entrada do endereço IP do servidor, seguido do endereço do broker MQTT (porta 1883, entrada vazia para utilizar o broker do servidor conectado), de informações da estação e do ID para cadastro de estação fornecido por um administrador do sistema com acesso ao terminal do servidor. É importante notar que o programa não detecta e não corrige um endereço IP incorreto, sendo necessária a reinicialização para que esse valor seja mudado, em caso de entrada incorreta.

Caso um ID correto falhe em cadastrar, basta repetir a entrada.

Caso seja a primeira vez que a estação foi utilizada, será pedido ao usuário também informações referentes às coordenadas da estação e o preço de seu KWh, os quais deverão ser inseridos como números, possivemente incluindo decimais.

Nota: Utilizar a entrada "test" para o campo de broker MQTT resulta na escolha de um broker de teste pre-definido, por padrão aquele da [EMQX](https://www.emqx.com/en/mqtt/public-mqtt5-broker) (endereço: broker.emqx.io, porta TCP 1883). Ademais, note que não é necessário que um broker MQTT esteja em execução na máquina da estação sob hipótese alguma, visto que a entrada vazia, como dito anteriormente, resulta na utilização de um broker em execução na máquina do servidor conectado.

![Tela inicial](/imgs/station_waiting.png?raw=true "Resultado caso a estação já tenha sido inicializada anteriormente.")

Após tais informações serem fornecidas e em cada inicialização subsequente do programa, o terminal exibirá o ID da estação e o preço unitário de seu KWh.

Quando um veículo agenda com sucesso uma recarga, a estação agendada receberá suas informações em até 1 minuto, inicando o processo de recarga.

![Tela de recarga](/imgs/station_recharge.png?raw=true "Realizando recarga")

Na atual versão de teste do programa, a recarga é feita apenas pressionando a tecla ENTER no terminal da estação.

### 🚘 Veículo (Usuário Final)

#### AVISO: Antes de utilizar quaisquer das interfaces gráficas presentes no módulo de veículos, certifique-se de as bibliotecas [TKinter](https://pypi.org/project/tk/) e [Custom TKinter](https://pypi.org/project/customtkinter/) estão instaladas diretamente na máquina que exibirá tais interfaces:
```console
sudo apt-get install python3-tk -y && \
pip3 install customtkinter --break-system-packages
```
##### (Instala, DE FORMA FORÇADA, as bibliotecas em sistemas tipo Linux, consulte documentação do componente para fazer o mesmo em outros sistemas operacionais)

Terceiro e último módulo do sistema, a parte referente ao veículo possui ```vehicle``` antes de seu número de versão do arquivo .zip. Para iniciar a aplicação (incluindo janela gráfica), execute o arquivo ```client.py```, encontrado no diretório principal da aplicação. O processo de cadastro de um veículo só requer ao usuário inserir o endereço IP do servidor (e tal entrada só é requisitada no cadastro, sendo "pulada" em execuções seguintes da aplicação). Assim como para a estação de recarga, o programa não detecta e não corrige um endereço IP incorreto, e portanto pode ser necessária a reinicialização do programa caso seja feita uma entrada incorreta.

Em seguida, é perguntado ao usuário o endereço do broker MQTT (porta 1883, entrada vazia para utilizar o broker do servidor conectado).

Nota: Utilizar a entrada "test" para o campo de broker MQTT resulta na escolha de um broker de teste pre-definido, por padrão aquele da [EMQX](https://www.emqx.com/en/mqtt/public-mqtt5-broker) (endereço: broker.emqx.io, porta TCP 1883). Ademais, note que não é necessário que um broker MQTT esteja em execução na máquina da estação sob hipótese alguma, visto que a entrada vazia, como dito anteriormente, resulta na utilização de um broker em execução na máquina do servidor conectado.

![Tela inicial](/imgs/vehicle_waiting.png?raw=true "A aplicação requer o endereço IP do servidor (em caso de cadastro) e uma entrada do broker MQTT (sempre) logo no seu início")

Após sua entrada, a aplicação será exibida em janela gráfica (caso trata-se da primeira execução, ou seja, cadastro, será necessário estabelecer conexão com um servidor antes que a aplicação seja exibida. o que resulta na espera de alguns segundos).

![GUI principal](/imgs/vehicle_gui_main.png?raw=true "Janela principal da aplicação.")


A seguir, a interface gráfica do programa será exibida, contendo todas as informações referentes ao nível de carga do veículo (incluindo aviso caso fique abaixo de 30%), estação mais próxima, próxima compra e histórico de compras, bem como botões para executar ações de busca de estação disponível mais próxima (e suas informações), geração de guia de pagamento de serviço, confirmação de pagamento e navegação do histórico de compras.

![Interface gráfica da aplicação do veículo, figura 1](/imgs/vehicle_after_signup.png?raw=true "Informações do veículo e entrada de comandos para realizar serviços de recarga")

#### IMPORTANTE: Não cabe ao usuário final, por meio da interface gráfica ou do terminal, alterar as informações referentes ao nível da bateria, da autonomia do veículo, de sua posição do veículo ou mesmo da capacidade de carga (após o cadastro). Tais informações estão salvas no arquivo ```vehicle_data.json```, presente na pasta ```/vehicledata/``` a partir do diretório principal da aplicação. A aplicação está configurada para monitorar constantemente tal arquivo de configuração e refletir quaisquer mudanças diretamente nas suas variáveis. Assim sendo, é esperado que o arquivo de propriedades seja alterado por softwares terceiros (e não pelo usuário da aplicação), os quais devem fazer uso de sensores que não estão presentes no atual ambiente de desenvolvimento e teste.

Um processo de recarga bem-sucedido inicia-se com a busca pela estação disponível mais próxima, utilizando para tal o botão ```Obter a distância até a estação de recarga mais próxima e o preço do KWh"```.
As informações obtidas em tal passo serão utilizadas na geração da guia de pagamento e na tentativa de agendamento subsequentes.

Em seguida, o usuário deve gerar uma guia de pagamento por meio do botão ```Gerar guia de pagamento```. O processo de geração de guia de pagamento é tão somente um PLACEHOLDER para a utilização de uma API de serviço de pagamento real (ex: BoaCompra), e gera um identificador único uuid4.

Por fim, o usuário deve confirmar que efetuou o pagamento pressionando o botão ```Recarregar totalmente na estação mais próxima```.

Se entre a busca da estação e a confirmação do pagamento nenhum outro veículo agendar com sucesso o local de recarga, o usuário conseguirá agendar a recarga de seu próprio veículo, cabendo ao software de controle do equipamento da estação de carga verificar o ID do veículo quando este chegar até o ponto e então realizar a recarga.

![Interface gráfica da aplicação do veículo, figura 2](/imgs/vehicle_recharge_success.png?raw=true "Resultado de um agendamento de recarga bem-sucedido")

No entanto, caso outro veículo consiga agendar o local de recarga durante a compra, o usuário em questão será notificado de que não conseguiu agendamento e que sua compra foi automaticamente cancelada (estornada), o que de fato acontece no servidor (é chamada uma função PLACEHOLDER para API de serviço de pagamentos).

Qualquer usuário com ao menos uma compra bem-sucedida realizada pode navegar seu histórico de compras por meio dos botões ```<``` e ```>```. Note que os espaços referentes às informações da compra permanecem vazios até que um dos botões seja pressionado, mesmo após ao menos uma compra ser feita.

![Interface gráfica da aplicação do veículo, figura 3](/imgs/vehicle_recharge_fail.png?raw=true "Resultado de um agendamento de recarga mal-sucedido e informações de uma compra realizada anteriormente")

## 🐧 🐢 Como utilizar o arquivo shell script (dockerscript.sh) para executar ações de construção, modificação e acesso interativo do/ao ambiente docker:
```console
bash dockerscript.sh ACAO NUM
```

### Utilize o comando no terminal Linux como descrito acima, sendo `ACAO` um paramêtro obrigatório para todas as ações, enquanto que `NUM` so é utilizado em uma destas.

### $${\color{yellow}"build"}$$  compila a imagem e cria a rede necessária.

- Formato fixo:
```console
bash dockerscript.sh build
```

### $${\color{green}"run"}$$ instancia os containers para as diferentes versões da aplicação (1 de servidor, 2 de estações e 4 de veículos).

- Formato fixo:
```console
bash dockerscript.sh run
```

### $${\color{orange}"stop"}$$ apaga os containers instanciados.

- Formato fixo:
```console
bash dockerscript.sh stop
```

### $${\color{lightgreen}"update"}$$ copia os varios arquivos da aplicação para os containers em execução. Pode e deve ser utilizado toda vez que houver alguma mudança nos arquivos da própria aplicacão (para atualizar os arquivos gerados durante a execução da aplicação, utilize o comando ´export´ como descrito mais abaixo).

- Formato fixo:
```console
bash dockerscript.sh update
```

### $${\color{black}"control"}$$ Assume o controle do terminal do container especificado no parâmetro `NUM`, sendo 0 referente ao container do servidor, 1-2 referente aos containers das estações, e 3-6 referente aos containers dos veículos.

- Exemplo:
```console
bash dockerscript.sh control 2
```
#### AVISO: Antes de realizar um acesso remoto a interfaces gráficas, certifique-se de a biblioteca "x11 Server Utils" para Linux está instalada diretamente na máquina que exibirá tais interfaces, e em seguida habilite a execução remota de programas.
```console
sudo apt-get install x11-xserver-utils -y
```
##### (Instala a biblioteca em sistemas do tipo Linux. O acesso remoto a containers por outros tipos de sistemas operacionais NÃO é previsto pelo kit de desenvolvimento deste programa.)
```console
xhost +
```
##### (Habilita a visualização remota de elementos gráficos, deve ser executado sempre que o sistema operacional sofrer reinicialização.)

### $${\color{blue}"import"}$$ Copia os arquivos e/ou diretórios gerados pelas aplicações em execução nos containers para a pasta `/files/imported`.

- Formato fixo:
```console
bash dockerscript.sh import
```

### $${\color{lightblue}"export"}$$ Copia os arquivos da pasta `/files/export` para suas respectivas pastas em seus respectivos containers, de acordo com a organização dentro da própria pasta `/files/export`.
Para re-inserir arquivos modificados nos containers, certifique-se de que a hierarquia em `/files/export` é a mesma encontrada em `/files/imported`, ou seja, tal como encontrado após o processo de importação.

- Formato fixo:
```console
bash dockerscript.sh export
```

### $${\color{red}"scrap"}$$ Apaga todos os containers, redes e imagens criadas pelas ações `build` e `run`.

- Formato fixo:
```console
bash dockerscript.sh scrap
```

### NOTA: O kit de desenvolvimento inclui um arquivo DOS-batch (dockerscript.bat) com comandos idênticos, exceto aqueles relacionados a interfaces gráficas, os quais estão totalmente ausentes.

# Bibliografia

## 🔧 📚 Paginas web consultadas para instalacao, solucao de problemas e aprendizado:
- **Instalacao:**
  - [_Install Docker Engine on Ubuntu_](https://docs.docker.com/engine/install/ubuntu)
- **Como resolver problemas ao executar o Docker**:
  - [_Cannot connect to the Docker daemon at unix:/var/run/docker.sock. Is the docker daemon running?_](https://stackoverflow.com/questions/44678725/cannot-connect-to-the-docker-daemon-at-unix-var-run-docker-sock-is-the-docker)
  - [_Is it possible to use docker without sudo?_](https://askubuntu.com/questions/1165877/is-it-possible-to-use-docker-without-sudo)
  - [_can i install customtkinter on linux_](https://www.reddit.com/r/Tkinter/comments/15sqnvx/can_i_install_customtkinter_on_linux/)
  - [_docker \_tkinter.TclError: couldn't connect to display_](https://stackoverflow.com/questions/49169055/docker-tkinter-tclerror-couldnt-connect-to-display/49229627#49229627)
- **Tutoriais**:
  - [_Docker Containers: IPC using Sockets — Part 2_](https://medium.com/techanic/docker-containers-ipc-using-sockets-part-2-834e8ea00768)
  - [_How to get bash or ssh into a running container in background mode?_](https://askubuntu.com/questions/505506/how-to-get-bash-or-ssh-into-a-running-container-in-background-mode/543057#543057)
