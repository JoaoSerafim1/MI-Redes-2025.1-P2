#Importa bibliotecas basicas do python 3
import json
import socket
import time

#Importa os componentes utilizados da biblioteca Paho MQTT
from paho.mqtt import client as mqtt_client

#Importa as bibliotecas customizadas da aplicacao
from lib.db import *
from lib.io import *
from lib.ch import *


#Classe do usuario
class Station():
    
    #Funcao inicializadora da classe
    def __init__(self):
        
        #Atributos
        self.ID = ""
        self.unitaryPrice = 0
        self.actualVehicleID = ""
        self.remainingCharge = 0
        self.clientIP = str(socket.gethostbyname(socket.gethostname()))
    
    #Funcao para enviar uma requisicao ao servidor
    def sendRequest(self, request):

        #Globais utilizadas
        global serverAddress

        global broker
        port = 1883
        topic = ("req9a3fd59-" + str(serverAddress))
        
        mqttMessage = [self.clientIP, port, request]

        #print("--------------------------------------------")
        #print(clientAddressString)
        #print(mqttMessage)
        #print("--------------------------------------------")
        
        try:
            #Serializa a resposta utilizando json
            serializedRequest = json.dumps(mqttMessage)

            mqttClientSender = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
            mqttClientSender.connect(broker, port)
            mqttClientSender.loop_start()
            mqttClientSender.publish(topic, serializedRequest)
            mqttClientSender.loop_stop()
        except:
            pass

    #Funcao para receber uma resposta de requisicao
    def listenToResponse(self, timeout):

        global serverAddress
        global decodedBytes

        global broker
        port = 1883
        topic = ("res9a3fd59-" + str(self.clientIP))

        add = ("", 0)
        response = ""

        decodedBytes = ""

        mqttClientReceiver = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

        #Funcao que determina o que acontece quando uma mensagem e recebida em um topico assinado
        def on_message(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            
            global decodedBytes

            decodedBytes = msg.payload.decode()
    
        mqttClientReceiver.on_message = on_message

        try:
            #Conecta ao broker com os parametros desejados, assina o topico e entra no loop para esperar mensagem(s)
            mqttClientReceiver.connect(broker, port)
            mqttClientReceiver.subscribe(topic)
            mqttClientReceiver.loop_start()

            start_time = time.time()

            while (((time.time() - start_time) < 10) and (decodedBytes == "")):
                pass

            mqttClientReceiver.loop_stop()
            mqttClientReceiver.unsubscribe(topic)
            mqttClientReceiver.disconnect()

        except:
            pass

        byteCopy = ("" + decodedBytes)
        decodedBytes = ""

        #print("=============================================")
        #print(decodedBytes)
        #print("=============================================")
        
        try:
            #De-serializa a mensagem decodificada 
            unserializedObj = json.loads(byteCopy)

            #Se uma resposta valida foi recebida, a mensagem deve ter tamanho 3
            if (len(unserializedObj) == 3):

                #Separa a parte do endereco referente ao endereco IP
                add = (unserializedObj[0], unserializedObj[1])
                response = unserializedObj[2]
        except Exception:
            pass
        
        #Retorna o objeto da mensagem
        return (add, response)
    
    
    #Funcao para registrar a estacao
    def registerStation(self, coord_x, coord_y, unitary_price):
        
        global requestID

        #Garante que a criacao da estacao so acontece uma vez
        #O servidor esta condicionado a executar requisicoes de indice 0 mesmo que a ultima requisicao para certo endereco tenha indice 0
        #Assim sendo, e preciso colocar um indice distinto de zero para forcar que isso nao aconteca
        #Entretanto, indices de 1 a 63 sao utilizados no ciclo normal de requisicao, entao o numero arbitrario aqui deve estar fora do intervalo
        #Caso contrario, poderia acontecer de o cliente nao conseguir registrar um novo veiculo no endereco, pois a ultima requisicao era do indice escolhido
        requestID = 64
        
        #ID da estacao
        stationID = input("ID para a estacao de carga (como fornecido pelo servidor): ")

        #Parametros da requisicao
        requestParameters = [stationID, coord_x, coord_y, unitary_price]

        #Formula o conteudo da requisicao a ser enviada
        #O conteudo e uma lista de ao menos 3 elementos (ID da requisicao, nome da requisicao e parametros da mesma)
        requestContent = [requestID, 'rcs', requestParameters]
        
        #Envia a requisicao para o servidor da aplicacao
        self.sendRequest(requestContent)

        #Espera a resposta
        (_, response) = self.listenToResponse(10)

        #Se a resposta nao for adequada ("OK")...
        while (response != "OK"):
            
            #ID da estacao
            stationID = input("ID para a estacao de carga (como fornecido pelo servidor): ")

            #Parametros da requisicao
            requestParameters = [stationID, coord_x, coord_y, unitary_price]

            #Formula o conteudo da requisicao a ser enviada
            #O conteudo e uma lista de ao menos 3 elementos (ID da requisicao, nome da requisicao e parametros da mesma)
            requestContent = [requestID, 'rcs', requestParameters]
            
            #Envia a requisicao para o servidor da aplicacao
            self.sendRequest(requestContent)

            #Espera a resposta
            (_, response) = self.listenToResponse(10)

            #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
            if (int(requestID) < 63):
                requestID = str(int(requestID) + 1)
            else:
                requestID = "1"

        #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"

        #Retorna a resposta (ID da estacao)
        return stationID
    
    def getBookedVehicle(self):

        global requestID

        #Formula o conteudo da requisicao a ser enviada
        #O conteudo e uma lista de ao menos 3 elementos (ID da requisicao, nome da requisicao e parametros da mesma)
        requestContent = [requestID, 'gbv', [self.ID]]
        
        #Envia a requisicao para o servidor da aplicacao
        self.sendRequest(requestContent)

        #Espera a resposta
        (_, response) = self.listenToResponse(10)

        #Se a resposta nao for adequada...
        while (response == ""):
            
            #Envia a requisicao para o servidor da aplicacao
            self.sendRequest(requestContent)

            #Espera a resposta
            (_, response) = self.listenToResponse(10)

        #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"

        return response

    def chargeSequence(self):

        global requestID
        global loadedTable
        
        #Enquanto o ID do veiculo em processo de carga nao seja vazio
        while (self.actualVehicleID != ""):

            #Executa a funcao externa de carga (encontrado em lib/ch.py)
            self.remainingCharge = doCharge(self.actualVehicleID, self.remainingCharge)

            #Caso a carga restante seja 0, sabemos que acabou o processo, e resetamos o ID do veiculo para vazio
            if (self.remainingCharge == 0):
                self.actualVehicleID = ""

        #Formula o conteudo da requisicao a ser enviada
        #O conteudo e uma lista de ao menos 4 elementos (ID de quem requeriu, ID da requisicao, nome da requisicao e parametros da mesma)
        requestContent = [requestID, 'fcs', [self.ID]]
        
        #Envia a requisicao para o servidor da aplicacao
        self.sendRequest(requestContent)

        #Espera a resposta
        (_, response) = self.listenToResponse(10)

        #Se a resposta nao for adequada ("OK" ou "NF")...
        while (response != "OK" and response != "NF"):
            
            #Envia a requisicao para o servidor da aplicacao
            self.sendRequest(requestContent)

            #Espera a resposta
            (_, response) = self.listenToResponse(10)

        #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"


#Programa inicia aqui
#Cria um objeto da classe Station
station = Station()

#Endereco do broker MQTT de teste
testBroker = 'broker.emqx.io'

#Valores iniciais do programa
requestID = "0"

#Cria um dicionario dos atributos da estacao
dataTable = {}

#Pergunta endereco do servidor
serverAddress = input("Insira o endereço IP do servidor: ")

#Pergunta endereco do broker MQTT
broker = input("Insira o endereço IP do broker MQTT (OU PRESSIONE ENTER para utilizar o endereço do servidor conectado): ")

if (broker == ""):
    broker = serverAddress

elif (broker == "test"):
    broker = testBroker

#Verifica se o arquivo de texto "station_data.json" esta presente, e caso nao esteja...
if (verifyFile(["stationdata"], "station_data.json") == False):

    #Valores dos pares chave-valor sao sempre string para evitar problemas com json
    dataTable["coord_x"] = str(enterNumber("Coordenada x do posto de recarga: ", "ENTRADA INVALIDA."))
    dataTable["coord_y"] = str(enterNumber("Coordenada y do posto de recarga: ", "ENTRADA INVALIDA."))
    dataTable["unitary_price"] = str(enterNumber("Preco unitario do KWh, em BRL: ", "ENTRADA INVALIDA."))

    #E tambem cria o arquivo e preenche com as informacoes contidas no dicionario acima
    writeFile(["stationdata", "station_data.json"], dataTable)

#Caso contrario
else:

    #Carrega as informacoes gravadas
    dataTable = readFile(["stationdata", "station_data.json"])


#Verifica se o arquivo de texto "ID.txt" esta presente, e caso nao esteja...
if (verifyFile(["stationdata"], "ID.txt") == False):

    #ID da estacaodataTable["coord_x"]
    stationID = station.registerStation(dataTable["coord_x"], dataTable["coord_y"], dataTable["unitary_price"])
    
    #Cria um novo arquivo
    writeFile(["stationdata", "ID.txt"], stationID)

#Carrega as informacoes gravadas (ID)
station.ID = readFile(["stationdata", "ID.txt"])

#Carrega as informacoes gravadas (station_data)
loadedTable = readFile(["stationdata", "station_data.json"])

#Modifica as informacoes do objeto da estacao
station.unitaryPrice = float(loadedTable["unitary_price"])

#Print das informacões
print("*********************************************")
print("ID: " + str(station.ID))
print("Preço do KWh (BRL): " +  str(station.unitaryPrice))
print("*********************************************")

#Loop do programa
while True:

    #Verifica se tem veiculo com carga pendente
    bookedVehicleInfo = station.getBookedVehicle()

    #Caso tenha
    if (len(bookedVehicleInfo[0]) == 24):
        
        station.actualVehicleID = bookedVehicleInfo[0]
        station.remainingCharge = bookedVehicleInfo[1]

        station.chargeSequence()

    #Caso contrario, espera um minuto antes de fazer qualquer outra coisa
    else:

        time.sleep(60)