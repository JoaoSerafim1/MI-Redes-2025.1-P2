# Sistemas distribuído - Recarga de Veículos Elétricos

Chamamos sistemas distribuídos aqueles compostos por várias instâncias individuais de aplicação, costumeiramente de dois ou mais tipos distintos, que trabalham em conjunto para prover um serviço em massa.

No contexto do MI de Concorrência e Conectividade da UEFS, semestre 2025.1, foi requisitado aos alunos a confecção de um sistema distribuído capaz de coordenar a recarga de veículos elétricos, além de monitorar o nível de carga dos veículos no qual a versão de usuário final está instanciada, e fornecer informações acerca do histórico de compras (recargas) de um usuário final.

O sistema aqui desenvolvido conta com 3 versões, cada uma destinada a ser executada por um agente distinto:
- Servidor: Aplicação pertencente aos provedores do serviço. Recebe requisicões das aplicações-cliente (veículo/usuário final e estação de recarga), validando, executando e registrando ações das demais partes. 
- Estação de recarga: Software instalado em computadores de cada ponto de recarga. Rotineiramente "pergunta" ao servidor se existe veículo a ser recarregado, caso disponível.
- Veículo (usuário final): Programa responsável por prover a um motorista de automóvel a opção de requisitar serviços de recarga por meio de pagamento e visualizar compras bem-sucedidas registradas no pelo servidor histórico. Como dito anteriormente, também monitora o nível de carga do veículo no qual é instalado.
  
# Instalação e uso da aplicação

## Requisitos básicos
- Sistema Operacional compatível com protocolo TCP-IP e Python (ex: [Ubuntu](https://ubuntu.com/download), [Windows](https://www.microsoft.com/pt-br/windows/))
- [Python](https://www.python.org/downloads/) 3.9
  
## 📦 Instalando e utilizando as diferentes versões do sistema distribuído

As versões do sistema destinadas a usuários distintos estão disponíveis individualmente neste repositório online em formato .zip, na sessão "Releases" (encontrada no canto direito da tela inicial do repositório na maioria dos navegadores).

### ☁️ Servidor

O arquivo .zip do servidor possui ```server``` antes de seu número de versão. Para iniciar o programa do servidor, execute o arquivo ```server.py```, encontrado no diretório principal da aplicação.

![Tela inicial](/imgs/server_start_screen.png?raw=true "Instruções do programa e informação do endereço do servidor e do ID para cadastro da próxima estação de carga")

Após o cadastro de uma estação de carga, o servidor automaticamente gerará um novo ID que deverá ser utilizado na próxima operação do tipo, e em seguida exibirá na tela tal informação.

![Tela inicial apos primeira carga](/imgs/server_after_first_station.png?raw=true "Resultado no terminal de uma operação de cadastro de estação de carga")

O recebimento de mensagens, bem como a execução de ações em cima do banco de dados do servidor, são todas operações registrados em arquivos de texto (logs), os quais podem ser encontrados nas pastas ```/logs/received/``` (mensagens recebidas) e ```logs/performed/``` (ações executadas pelo servidor).

Logs possuem o seguinte formato:
- Título: YYYY-MM-DDD = Data local
- Conteúdo:
  - [YYYY-MM-DDD hh:mm:ss.ssssss] => Data e horário locais (24 horas)
  - NAME:
  - NOME-DA-ENTRADA => Informação do nome da entrada no log
    - RVMSG:         Mensagem recebida
    - RGTSTATION:    Registrar nova estação
    - RGTVEHICLE:    Registrar novo veículo
    - GETBOOKED:     Obter informações acerca de possível veículo agendado (estação)
    - FREESPOT:      Liberar estação para agendamento
    - GETDISTANCE:   Obter e retornar informações da estação dispónível mais próxima de um veículo
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

![Tela de encerramento](/imgs/server_terminating.png?raw=true "Resultado da sequência de encerramento do servidor")

### 🔋 Estação de Carga

O arquivo .zip da estação possui ```station``` antes de seu número de versão. Para iniciar o programa referente à estação de carga, execute o arquivo ```client.py```, encontrado no diretório principal da aplicação.

![Tela inicial](/imgs/station_start_screen.png?raw=true "A aplicação requer o endereço IP do servidor logo no seu início")

Ao usuário será pedida a entrada do endereço IP do servidor, seguido de informações da estação e do ID para cadastro de estação fornecido por um administrador do sistema com acesso ao terminal do servidor. É importante notar que o programa não detecta e não corrige um endereço IP incorreto, sendo necessária a reinicialização para que esse valor seja mudado. Ademais, caso um ID correto falhe em cadastrar, basta repeti-lo 1 ou 2 vezes.

Após tais informações serem fornecidas e em cada inicialização subsequente do programa, o terminal exibirá o ID da estação e o preço unitário de seu KWh.

![Tela após o cadastro](/imgs/station_after_signup.png?raw=true "Cadastro da estação e tela de boas-vindas")

Quando um veículo agenda com sucesso uma recarga, a estação agendada receberá suas informações em até 1 minuto, inicando o processo de recarga.

Na atual versão de teste do programa, a recarga é feita apenas pressionando a tecla ENTER no terminal da estação.

![Tela após agendamento de recarga](/imgs/station_recharge.png?raw=true "Processo de recarga de um veículo agendado")

### 🚘 Veículo (Usuário Final)

#### AVISO: Antes de utilizar quaisquer das interfaces gráficas presentes no módulo de veículos, certifique-se de as bibliotecas "TKinter" e "Custom TKinter" estão instaladas diretamente na máquina que exibirá tais interfaces.
```console
sudo apt-get install python3-tk -y && \
pip3 install customtkinter --break-system-packages
```
##### (Instala as bibliotecas em sistemas tipo Linux, consulte documentação do Python para fazer o mesmo em outros sistemas operacionais)

Terceiro e último módulo do sistema, a parte referente ao veículo possui ```vehicle``` antes de seu número de versão do arquivo .zip. Para iniciar a aplicação (incluindo janela gráfica), execute o arquivo ```client.py```, encontrado no diretório principal da aplicação.

![Tela inicial](/imgs/vehicle_start_screen.png?raw=true "A aplicação requer o endereço IP do servidor logo no seu início")

O processo de cadastro de um veículo só requer ao usuário inserir o endereço IP do servidor e a capacidade em KWh do veículo. Assim como para a estação de recarga, o programa não detecta e não corrige um endereço IP incorreto, e portanto pode ser necessária a reinicialização do programa caso seja feita uma entrada incorreta.

A seguir, a interface gráfica do programa será exibida, contendo todas as informações referentes ao nível de carga do veículo (incluindo aviso caso fique abaixo de 30%), estação mais próxima, próxima compra e histórico de compras, bem como botões para executar ações de busca de estação disponível mais próxima (e suas informações), geração de guia de pagamento de serviço, confirmação de pagamento e navegação do histórico de compras.

![Interface gráfica da aplicação do veículo, figura 1](/imgs/vehicle_after_signup.png?raw=true "Informações do veículo e entrada de comandos para realizar serviços de recarga")

#### IMPORTANTE: Não cabe ao usuário final, por meio da interface gráfica ou do terminal, alterar as informações referentes ao nível da bateria, da posição do veículo ou mesmo da capacidade de carga (após o cadastro). Tais informações estão salvas no arquivo ```vehicle_data.json```, presente na pasta ```/vehicledata/``` a partir do diretório principal da aplicação. A aplicação está configurada para monitorar constantemente tal arquivo de configuração e refletir quaisquer mudanças diretamente nas suas variáveis. Assim sendo, é esperado que o arquivo de propriedades seja alterado por softwares terceiros, os quais devem fazer uso de sensores que não estão presentes no atual ambiente de desenvolvimento e teste.

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
##### (Instala a biblioteca)
```console
xhost +
```
##### (Habilita a execução remota de programas, deve ser executado sempre que o sistema for reiniciado)

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
