#Importa bibliotecas basicas do python 3
import json
import socket
import time
import datetime

#Importa os componentes utilizados da biblioteca Paho MQTT
from paho.mqtt import client as mqtt_client

#Importa as bibliotecas customizadas da aplicacao
from application.lib.db import *
from application.lib.pr import *

decodedBytes = ""


#Classe do usuario
class User():

    #Funcao inicializadora da classe
    def __init__(self):
        
        #Atributos
        self.ID = ""
        self.battery_level = ""
        self.capacity = ""
        self.autonomy = ""
        self.clientIP = str(socket.gethostbyname(socket.gethostname()))

        self.serverAddress = ""
        self.broker = ""
        
        self.brokerCandidate = ""
        self.testBroker = ""

        self.requestID = "0"

        self.nearestStationID = ""
        self.nearestStationDistance = ""
        self.nearestStationPrice = ""

        self.nextPurchaseID = ""
        self.nextAmountToPay = ""
        self.purchaseResult = ""

        self.destinyServerAddress = ""

        self.routeSearchIndex = "0"
        self.routeNameList = []

        self.routeReservationIndex = "0"

        self.routeReservationAddIndex = 0
        self.routeReservationTimeToAdd = "0"
        self.routeReservationNameList = []
        self.routeReservationTimeList = []
        self.routeReservationResult = ""

        self.historyPurchaseIndex = "0"
        self.historyPurchaseID = "0"
        self.historyPurchaseTotal = "0"
        self.historyPurchasePrice = "0"
        self.historyPurchaseCharge = "0"
    
    #Funcao para enviar uma requisicao ao servidor
    def sendRequest(self, request):
        
        port = 1883
        topic = ("req9a3fd59-" + str(self.serverAddress))
        
        mqttMessage = [self.clientIP, port, request]

        #print("--------------------------------------------")
        #print(str(self.broker) + " : " + str(port))
        #print(topic)
        #print(mqttMessage)
        #print("--------------------------------------------")
        
        try:
            #Serializa a resposta utilizando json
            serializedRequest = json.dumps(mqttMessage)

            mqttClientSender = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
            mqttClientSender.connect(self.broker, port)
            mqttClientSender.loop_start()
            mqttClientSender.publish(topic, serializedRequest)
            mqttClientSender.loop_stop()
        except:
            pass

    #Funcao para receber uma resposta de requisicao
    def listenToResponse(self):
        
        #Globais utilizadas
        global decodedBytes

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
            mqttClientReceiver.connect(self.broker, port)
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

        #print("=============================================")
        #print(str(self.broker) + " : " + str(port))
        #print(topic)
        #print(decodedBytes)
        #print("=============================================")
        
        try:
            #De-serializa a mensagem decodificada 
            unserializedObj = json.loads(decodedBytes)

            #Se uma resposta valida foi recebida, a mensagem deve ter tamanho 3
            if (len(unserializedObj) == 3):

                #Separa a parte do endereco referente ao endereco IP
                add = (unserializedObj[0], unserializedObj[1])
                response = unserializedObj[2]
        except Exception:
            pass
        
        #Retorna o objeto da mensagem
        return (add, response)

    
    #Funcao para registrar o veiculo
    def registerVehicle(self):

        #Garante que a criacao do veiculo so acontece uma vez
        #O servidor esta condicionado a executar requisicoes de indice 0 mesmo que a ultima requisicao para certo endereco tenha indice 0
        #Assim sendo, e preciso colocar um indice distinto de zero para forcar que isso nao aconteca
        #Entretanto, indices de 1 a 63 sao utilizados no ciclo normal de requisicao, entao o numero arbitrario aqui deve estar fora do intervalo
        #Caso contrario, poderia acontecer de o cliente nao conseguir registrar um novo veiculo no endereco, pois a ultima requisicao era do indice escolhido
        self.requestID = 64

        #Formula o conteudo da requisicao a ser enviada
        #O conteudo e uma lista de ao menos 4 elementos (ID de quem requeriu, ID da requisicao, nome da requisicao e parametros da mesma)
        requestContent = [self.requestID, 'rve', '']
        
        #Envia a requisicao para o servidor da aplicacao
        self.sendRequest(requestContent)

        #Espera a resposta
        (add, response) = self.listenToResponse()

        #Se a resposta nao for adequada (string de 24 caracteres alfanumericos)...
        while (len(response) != 24):
            
            #Envia novamente a requisicao e espera a resposta
            self.sendRequest(requestContent)

            (add, response) = self.listenToResponse()

        #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
        self.requestID = "1"

        #Retorna a resposta (ID do veiculo)
        return response
    
    #Solicita distancia do posto mais proximo
    def nearestSpotRequest(self):

        #Le informacoes do veiculo
        localDataTable = readFile(["vehicledata", "vehicle_data.json"])
        
        #Confeccina o conteudo da requisicao e envia 1x
        requestParameters = [localDataTable["coord_x"],localDataTable["coord_y"], localDataTable["autonomy"], self.ID]
        requestContent = [self.requestID, 'nsr', requestParameters]
        self.sendRequest(requestContent)
        (add, response) = self.listenToResponse()

        #Atualiza o ID da requisicao
        if (int(self.requestID) < 63):
            self.requestID = str(int(self.requestID) + 1)
        else:
            self.requestID = "1"
        
        #Se nao receber resposta, o servidor esta indisponivel
        if (len(response) < 1):
            
            self.nearestStationID = ""
            self.nearestStationDistance = " Servidor indisponível. "
            self.nearestStationPrice = ""
        
        #Se receber resposta com campo do ID da estacao vazio, nenhum estacao foi encontrada (disponivel)
        elif (response[0] == "0"):
            
            self.nearestStationID = ""
            self.nearestStationDistance = " Nenhuma estação disponível encontrada. "
            self.nearestStationPrice = ""
        
        #Caso contrario, atualiza as informacoes de acordo com o retorno (informacoes da estacao mais proxima)
        else:
            
            self.nearestStationID = str(response[0])
            self.nearestStationDistance = str(response[1])
            self.nearestStationPrice = str(response[2])
    
    #Funca que gera a guia de pagamento para recarga
    def simulateForNearestSpot(self):
        
        #Se a bateria nao esta cheia e existe uma estacao para fazer a recarga, gera a guia de pagamento para encher a bateria
        if((float(self.battery_level) < 1) and (self.nearestStationID != "")):
            
            self.nextPurchaseID, self.nextAmountToPay = simulatePayment(self.capacity, self.battery_level, self.nearestStationPrice)

    #Funcao que efetua o pagamento da ultima guia gerada
    def payForNearestSpot(self):

        #Se a bateria nao esta cheia, existe uma estacao para fazer a recarga e o pagamento foi confirmado
        if((float(self.battery_level) < 1) and (self.nearestStationID != "") and (confirmPayment(self.nextPurchaseID) == True)):
            
            #Faz o conteudo da requisicao
            requestParameters = [self.nextPurchaseID, self.ID, self.nearestStationID, self.nextAmountToPay]
            requestContent = [self.requestID, 'bcs', requestParameters]

            #Envia a requisicao
            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

            #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
            while(response == ""):

                self.sendRequest(requestContent)
                (add, response) = self.listenToResponse()

            #Atualiza resultado da operacao de compra
            if(response == "OK"):
                self.purchaseResult = (" Compra de UUID <" + self.nextPurchaseID + "> bem-sucedida. Espere de 1 a 2 minutos para comecar o processo de recarga. ")
            else:
                self.purchaseResult = " O local está reservado ou é inválido. Sua compra de UUID <" + self.nextPurchaseID + "> foi estornada automaticamente. "

            #Atualiza o ID de requisicao
            if (int(self.requestID) < 63):
                self.requestID = str(int(self.requestID) + 1)
            else:
                self.requestID = "1"

            #Zera o ID da proxima compra
            self.nextPurchaseID = ""
    

    #Funcao para obter informacoes da compra no indice anterior
    def purchaseBackward(self):

        #Faz o conteudo da requisicao (ID do veiculo e indice atual de compra - 1)
        requestParameters = [self.ID, str(int(self.historyPurchaseIndex) - 1)]
        requestContent = [self.requestID, 'gpr', requestParameters]

        #Envia a requisicao
        self.sendRequest(requestContent)
        (add, response) = self.listenToResponse()

        retry = 0
        #Se nao receber resposta valida, repete o envio mais 3 vezes (so acontece caso o servidor esteja indisponivel)
        while((response == "") and (retry < 3)):

            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()
            retry += 1

        if(retry < 3):

            #Atualiza o ID de requisicao
            if (int(self.requestID) < 63):
                self.requestID = str(int(self.requestID) + 1)
            else:
                self.requestID = "1"

        #Caso a resposta diga que nao encontrou compra naquele indice para o veiculo
        if((len(response) >= 4) and (response[0] == "0")):

            #Faz o conteudo da requisicao (ID do veiculo e indice atual de compra)
            requestParameters = [self.ID, str(self.historyPurchaseIndex)]
            requestContent = [self.requestID, 'gpr', requestParameters]

            #Envia a requisicao
            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

            retry = 0
            #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
            while((response == "") and (retry < 3)):

                self.sendRequest(requestContent)
                (add, response) = self.listenToResponse()
                retry += 1

            if(retry < 3):

                #Atualiza o ID de requisicao
                if (int(self.requestID) < 63):
                    self.requestID = str(int(self.requestID) + 1)
                else:
                    self.requestID = "1"

            #Caso a resposta diga que nao encontrou compra naquele indice para o veiculo
            if(len(response) >= 4 and response[0] != "0"):
                
                #Atualiza informacoes da compra exibida
                self.historyPurchaseID = response[0]
                self.historyPurchaseTotal = response[1]
                self.historyPurchasePrice = response[2]
                self.historyPurchaseCharge = response[3]

        #Caso contrario, atualiza o indice atual da compra analisada
        elif(len(response) >= 4):

            self.historyPurchaseIndex = str(int(self.historyPurchaseIndex) - 1)

            #Atualiza informacoes da compra exibida
            self.historyPurchaseID = response[0]
            self.historyPurchaseTotal = response[1]
            self.historyPurchasePrice = response[2]
            self.historyPurchaseCharge = response[3]

    
    #Funcao para obter informacoes da compra no indice a seguir
    def purchaseForward(self):

        #Faz o conteudo da requisicao (ID do veiculo e indice atual de compra - 1)
        requestParameters = [self.ID, str(int(self.historyPurchaseIndex) + 1)]
        requestContent = [self.requestID, 'gpr', requestParameters]

        #Envia a requisicao
        self.sendRequest(requestContent)
        (add, response) = self.listenToResponse()

        retry = 0
        #Se nao receber resposta valida, repete o envio mais 3 vezes (so acontece caso o servidor esteja indisponivel)
        while((response == "") and (retry < 3)):

            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()
            retry += 1

        if(retry < 3):

            #Atualiza o ID de requisicao
            if (int(self.requestID) < 63):
                self.requestID = str(int(self.requestID) + 1)
            else:
                self.requestID = "1"

        #Caso a resposta diga que nao encontrou compra naquele indice para o veiculo
        if((len(response) >= 4) and (response[0] == "0")):

            #Faz o conteudo da requisicao (ID do veiculo e indice atual de compra)
            requestParameters = [self.ID, str(self.historyPurchaseIndex)]
            requestContent = [self.requestID, 'gpr', requestParameters]

            #Envia a requisicao
            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

            retry = 0
            #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
            while((response == "") and (retry < 3)):

                self.sendRequest(requestContent)
                (add, response) = self.listenToResponse()
                retry += 1

            if(retry < 3):

                #Atualiza o ID de requisicao
                if (int(self.requestID) < 63):
                    self.requestID = str(int(self.requestID) + 1)
                else:
                    self.requestID = "1"

            #Caso a resposta diga que nao encontrou compra naquele indice para o veiculo
            if(len(response) >= 4 and response[0] != "0"):
                
                #Atualiza informacoes da compra exibida
                self.historyPurchaseID = response[0]
                self.historyPurchaseTotal = response[1]
                self.historyPurchasePrice = response[2]
                self.historyPurchaseCharge = response[3]

        #Caso contrario, atualiza o indice atual da compra analisada
        elif(len(response) >= 4):

            self.historyPurchaseIndex = str(int(self.historyPurchaseIndex) + 1)

            #Atualiza informacoes da compra exibida
            self.historyPurchaseID = response[0]
            self.historyPurchaseTotal = response[1]
            self.historyPurchasePrice = response[2]
            self.historyPurchaseCharge = response[3]


    #Funcao para obter informacoes da rota no indice anterior
    def routeBackward(self):

        #Faz o conteudo da requisicao (ID do veiculo e indice atual de rota - 1)
        requestParameters = [str((int(self.routeSearchIndex)) - 1), self.destinyServerAddress]
        requestContent = [self.requestID, 'rwr', requestParameters]

        #Envia a requisicao
        self.sendRequest(requestContent)
        (add, response) = self.listenToResponse()

        retry = 0
        #Se nao receber resposta valida, repete o envio mais 3 vezes (so acontece caso o servidor esteja indisponivel)
        while((response == "") and (retry < 3)):

            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()
            retry += 1

        if(retry < 3):

            #Atualiza o ID de requisicao
            if (int(self.requestID) < 63):
                self.requestID = str(int(self.requestID) + 1)
            else:
                self.requestID = "1"

        #Caso a resposta diga que nao encontrou rota naquele indice para o veiculo
        if((len(response) >= 2) and (response[0] == "-1")):

            #Faz o conteudo da requisicao (ID do veiculo e indice atual de rota - 1)
            requestParameters = [self.routeSearchIndex, self.destinyServerAddress]
            requestContent = [self.requestID, 'rwr', requestParameters]

            #Envia a requisicao
            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

            retry = 0
            #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
            while((response == "") and (retry < 3)):

                self.sendRequest(requestContent)
                (add, response) = self.listenToResponse()
                retry += 1

            if(retry < 3):

                #Atualiza o ID de requisicao
                if (int(self.requestID) < 63):
                    self.requestID = str(int(self.requestID) + 1)
                else:
                    self.requestID = "1"

            #Caso a resposta diga que nao encontrou rota naquele indice para o veiculo
            if(len(response) >= 2 and response[0] != "-1"):
                
                #Atualiza informacoes da rota exibida/seelecionada
                self.routeReservationIndex = response[0]
                self.routeNameList = response[1].copy()

        #Caso contrario, atualiza o indice atual da rota analisada
        elif(len(response) >= 2):

            self.routeSearchIndex = str(int(self.routeSearchIndex) - 1)

            #Atualiza informacoes da rota exibida/seelecionada
            self.routeReservationIndex = response[0]
            self.routeNameList = response[1].copy()

    #Funcao para obter informacoes da rota no indice anterior
    def routeForward(self):

        #Faz o conteudo da requisicao (ID do veiculo e indice atual de rota - 1)
        requestParameters = [str((int(self.routeSearchIndex)) + 1), self.destinyServerAddress]
        requestContent = [self.requestID, 'rwr', requestParameters]

        #Envia a requisicao
        self.sendRequest(requestContent)
        (add, response) = self.listenToResponse()

        retry = 0
        #Se nao receber resposta valida, repete o envio mais 3 vezes (so acontece caso o servidor esteja indisponivel)
        while((response == "") and (retry < 3)):

            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()
            retry += 1

        if(retry < 3):

            #Atualiza o ID de requisicao
            if (int(self.requestID) < 63):
                self.requestID = str(int(self.requestID) + 1)
            else:
                self.requestID = "1"

        #Caso a resposta diga que nao encontrou rota naquele indice para o veiculo
        if((len(response) >= 2) and (response[0] == "-1")):

            #Faz o conteudo da requisicao (ID do veiculo e indice atual de rota - 1)
            requestParameters = [self.routeSearchIndex, self.destinyServerAddress]
            requestContent = [self.requestID, 'rwr', requestParameters]

            #Envia a requisicao
            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

            retry = 0
            #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
            while((response == "") and (retry < 3)):

                self.sendRequest(requestContent)
                (add, response) = self.listenToResponse()
                retry += 1

            if(retry < 3):

                #Atualiza o ID de requisicao
                if (int(self.requestID) < 63):
                    self.requestID = str(int(self.requestID) + 1)
                else:
                    self.requestID = "1"

            #Caso a resposta diga que nao encontrou rota naquele indice para o veiculo
            if(len(response) >= 2 and response[0] != "-1"):
                
                #Atualiza informacoes da rota exibida/seelecionada
                self.routeReservationIndex = response[0]
                self.routeNameList = response[1].copy()

        #Caso contrario, atualiza o indice atual da rota analisada
        elif(len(response) >= 2):

            self.routeSearchIndex = str(int(self.routeSearchIndex) + 1)

            #Atualiza informacoes da rota exibida/seelecionada
            self.routeReservationIndex = response[0]
            self.routeNameList = response[1].copy()
    
    #Funcao para adicionar um novo horario na lista de horario a agendar
    def addReservationToList(self):

        #Verifica se o horario atual e numerico, pois se for, trata-se de EPOCH
        if(self.routeReservationTimeToAdd.isnumeric() == True):
            
            #Tenta primeiro adicionar o nome do no (servidor) indexado no indice atual da lista em construcao
            #Se for bem-sucedido, adiciona tambem o horario na lista de reserva em construcao e atualiza o indice
            try:

                self.routeReservationNameList.append(self.routeNameList[self.routeReservationAddIndex])
                self.routeReservationTimeList.append(str(self.routeReservationTimeToAdd))
                
                self.routeReservationAddIndex += 1
            
            except:
                pass
        
        #Se nao for, trata-se de datetime (formato DD-MM-AAAA/hh:mm)
        else:

            #Tenta obter todos os elementos da tupla datetime
            #Se for bem-sucedido, adiciona tambem o horario na lista de reserva em construcao e atualiza o indice
            try:
                
                dayPortion = int(self.routeReservationTimeToAdd[0] + self.routeReservationTimeToAdd[1])
                monthPortion = int(self.routeReservationTimeToAdd[3] + self.routeReservationTimeToAdd[4])
                yearPortion = int(self.routeReservationTimeToAdd[6] + self.routeReservationTimeToAdd[7] + self.routeReservationTimeToAdd[8] + self.routeReservationTimeToAdd[9])
                hourPortion = int(self.routeReservationTimeToAdd[11] + self.routeReservationTimeToAdd[12])
                minutePortion = int(self.routeReservationTimeToAdd[14] + self.routeReservationTimeToAdd[15])
                
                datetimeTime = datetime.datetime(day=dayPortion, month=monthPortion, year=yearPortion, hour=hourPortion, minute=minutePortion, second=0, tzinfo=datetime.timezone.utc)
                epochTime = datetimeTime.timestamp()
                
                self.routeReservationNameList.append(self.routeNameList[self.routeReservationAddIndex])
                self.routeReservationTimeList.append(str(epochTime))
                
                self.routeReservationAddIndex += 1
                
            except:
                pass
    
    #Funcao para remover o ultimo horario da lista de horarios para agendar
    def removeLastReservationFromList(self):

            #Tenta remover o ultimo elemento na lista
            try:
                tempItem = self.routeReservationTimeList.pop()

                try:
                    self.routeReservationNameList.pop()
                    self.routeReservationAddIndex -= 1
                
                except:
                    self.routeReservationTimeList.append(tempItem)

            except:
                pass
                
    
    #Funcao para confirmar a reserva no indice do servidor atual
    def confirmReservation(self):

        #Le informacoes do veiculo
        localDataTable = readFile(["vehicledata", "vehicle_data.json"])

        #Faz o conteudo da requisicao (informacoes utilizada para iniciar o processo de reserva)
        requestParameters = [self.ID, self.routeReservationIndex, self.routeReservationTimeList, self.autonomy, localDataTable["coord_x"], localDataTable["coord_y"]]
        requestContent = [self.requestID, 'rrt', requestParameters]

        #Envia a requisicao
        self.sendRequest(requestContent)
        (add, response) = self.listenToResponse()

        retry = 0
        #Se nao receber resposta valida, repete o envio mais 3 vezes (so acontece caso o servidor esteja indisponivel)
        while((response == "") and (retry < 3)):

            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()
            retry += 1

        #Se saiu antes de gastar as 3 tentativas, foi bem-sucedido
        if(retry < 3):

            #Atualiza o ID de requisicao
            if (int(self.requestID) < 63):
                self.requestID = str(int(self.requestID) + 1)
            else:
                self.requestID = "1"

            #Muda o texto de resposta de acordo com a resposta do servidor e limpa o conteudo dos elementos
            if(response == "OK"):
                self.routeReservationResult = " Reserva bem-sucedida. Tenha uma boa viagem. "
                
                self.routeReservationNameList.clear()
                self.routeReservationTimeList.clear()
                self.routeReservationAddIndex = 0
            else:
                self.routeReservationResult = " Não foi possível completar a reserva. Tente novamente mais tarde. "
        
        #Caso contrario, nao conseguiu conexao
        else:

            self.routeReservationResult = " Servidor indisponível. "