#Importa bibliotecas basicas do python 3
import json
import socket
import time
import threading
import sys

#Importa os componentes utilizados da biblioteca Paho MQTT
from paho.mqtt import client as mqtt_client

#Importa as bibliotecas customizadas da aplicacao
from lib.db import *
from lib.io import *
from lib.pr import *

#Importa customTkinter
import customtkinter as ctk

#Classe do usuario
class User():
    
    #Funcao inicializadora da classe
    def __init__(self):
        
        #Atributos
        self.ID = ""
        self.battery_level = ""
        self.capacity = ""
        self.payment_history = {}
        self.clientIP = str(socket.gethostbyname(socket.gethostname()))
    
    #Funcao para enviar uma requisicao ao servidor
    def sendRequest(self, request):

        #Globais utilizadas
        global serverAddress

        global broker
        port = 1883
        topic = serverAddress
        
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
    def listenToResponse(self):
        
        global serverAddress
        global decodedBytes

        global broker
        port = 1883
        topic = self.clientIP

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

    
    #Funcao para registrar o veiculo
    def registerVehicle(self):
        
        global requestID

        #Garante que a criacao do veiculo so acontece uma vez
        #O servidor esta condicionado a executar requisicoes de indice 0 mesmo que a ultima requisicao para certo endereco tenha indice 0
        #Assim sendo, e preciso colocar um indice distinto de zero para forcar que isso nao aconteca
        #Entretanto, indices de 1 a 63 sao utilizados no ciclo normal de requisicao, entao o numero arbitrario aqui deve estar fora do intervalo
        #Caso contrario, poderia acontecer de o cliente nao conseguir registrar um novo veiculo no endereco, pois a ultima requisicao era do indice escolhido
        requestID = 64

        #Formula o conteudo da requisicao a ser enviada
        #O conteudo e uma lista de ao menos 4 elementos (ID de quem requeriu, ID da requisicao, nome da requisicao e parametros da mesma)
        requestContent = [requestID, 'rve', '']
        
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
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"

        #Retorna a resposta (ID do veiculo)
        return response
    
    #Solicita distancia do posto mais proximo
    def nearestSpotRequest(self):
        
        global requestID
        global nearestStationID
        global nearestStationDistance
        global nearestStationPrice

        #Le informacoes do veiculo
        localDataTable = readFile(["vehicledata", "vehicle_data.json"])
        
        #Confeccina o conteudo da requisicao e envia 1x
        requestParameters = [localDataTable["coord_x"],localDataTable["coord_y"], localDataTable["autonomy"], self.ID]
        requestContent = [requestID, 'nsr', requestParameters]
        self.sendRequest(requestContent)
        (add, response) = self.listenToResponse()

        #Atualiza o ID da requisicao
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"
        
        #Se nao receber resposta, o servidor esta indisponivel
        if (len(response) < 1):
            
            nearestStationID = ""
            nearestStationDistance = " SERVIDOR INDISPONÍVEL "
            nearestStationPrice = ""
        
        #Se receber resposta com campo do ID da estacao vazio, nenhum estacao foi encontrada (disponivel)
        elif (response[0] == "0"):
            
            nearestStationID = ""
            nearestStationDistance = " NENHUMA ESTAÇÃO DISPONÍVEL ENCONTRADA "
            nearestStationPrice = ""
        
        #Caso contrario, atualiza as informacoes de acordo com o retorno (informacoes da estacao mais proxima)
        else:
            
            nearestStationID = response[0]
            nearestStationDistance = response[1]
            nearestStationPrice = response[2]
    
    #Funca que gera a guia de pagamento para recarga
    def simulateForNearestSpot(self):

        global nearestStationID
        global nearestStationPrice

        global nextPurchaseID
        global nextAmountToPay
        
        #Se a bateria nao esta cheia e existe uma estacao para fazer a recarga, gera a guia de pagamento para encher a bateria
        if((float(self.battery_level) < 1) and (nearestStationID != "")):
            
            nextPurchaseID, nextAmountToPay = simulatePayment(self.capacity, self.battery_level, nearestStationPrice)

    #Funcao que efetua o pagamento da ultima guia gerada
    def payForNearestSpot(self):

        global requestID
        global nearestStationID

        global nextPurchaseID
        global nextAmountToPay
        global purchaseResult

        #Se a bateria nao esta cheia, existe uma estacao para fazer a recarga e o pagamento foi confirmado
        if((float(self.battery_level) < 1) and (nearestStationID != "") and (confirmPayment(nextPurchaseID) == True)):
            
            #Faz o conteudo da requisicao
            requestParameters = [nextPurchaseID, self.ID, nearestStationID, nextAmountToPay]
            requestContent = [requestID, 'bcs', requestParameters]

            #Envia a requisicao
            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

            #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
            while(response == ""):

                self.sendRequest(requestContent)
                (add, response) = self.listenToResponse()

            #Exibe resultado da operacao
            if(response == "OK"):
                purchaseResult = (" Compra de UUID <" + nextPurchaseID + "> bem-sucedida. Espere de 1 a 2 minutos para comecar o processo de recarga. ")
            else:
                purchaseResult = " O local está reservado ou é inválido. Sua compra de UUID <" + nextPurchaseID + "> foi estornada automaticamente. "

            #Atualiza o ID de requisicao
            if (int(requestID) < 63):
                requestID = str(int(requestID) + 1)
            else:
                requestID = "1"

            #Zera o ID da proxima compra
            nextPurchaseID = ""
    
    #Funcao para obter informacoes da compra no indice a seguir
    def purchaseBackward(self):
        
        global requestID
        global purchaseHistoryIndex
        global displayPurchaseID
        global displayPurchaseTotal
        global displayPurchasePrice
        global displayPurchaseCharge

        #Faz o conteudo da requisicao (ID do veiculo e indice atual de compra - 1)
        requestParameters = [self.ID, str(int(purchaseHistoryIndex) - 1)]
        requestContent = [requestID, 'gpr', requestParameters]

        #Envia a requisicao
        self.sendRequest(requestContent)
        (add, response) = self.listenToResponse()

        #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
        while(response == ""):

            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

        #Atualiza o ID de requisicao
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"

        #Caso a resposta diga que nao encontrou compra naquele indice para o veiculo
        if(response[0] == "0"):

            #Faz o conteudo da requisicao (ID do veiculo e indice atual de compra)
            requestParameters = [self.ID, str(purchaseHistoryIndex)]
            requestContent = [requestID, 'gpr', requestParameters]

            #Envia a requisicao
            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

            #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
            while(response == ""):

                self.sendRequest(requestContent)
                (add, response) = self.listenToResponse()

            #Atualiza o ID de requisicao
            if (int(requestID) < 63):
                requestID = str(int(requestID) + 1)
            else:
                requestID = "1"

        #Caso contrario, atualiza o indice atual da compra analisada
        else:

            purchaseHistoryIndex = str(int(purchaseHistoryIndex) - 1)
        
        #Atualiza informacoes da compra exibida
        displayPurchaseID = response[0]
        displayPurchaseTotal = response[1]
        displayPurchasePrice = response[2]
        displayPurchaseCharge = response[3]
    
    #Funcao para obter informacoes da compra no indice a seguir
    def purchaseForward(self):
        
        global requestID
        global purchaseHistoryIndex
        global displayPurchaseID
        global displayPurchaseTotal
        global displayPurchasePrice
        global displayPurchaseCharge

        #Faz o conteudo da requisicao (ID do veiculo e indice atual de compra + 1)
        requestParameters = [self.ID, str(int(purchaseHistoryIndex) + 1)]
        requestContent = [requestID, 'gpr', requestParameters]

        #Envia a requisicao
        self.sendRequest(requestContent)
        (add, response) = self.listenToResponse()

        #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
        while(response == ""):

            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

        #Atualiza o ID de requisicao
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"

        #Caso a resposta diga que nao encontrou compra naquele indice para o veiculo
        if(response[0] == "0"):

            #Faz o conteudo da requisicao (ID do veiculo e indice atual de compra)
            requestParameters = [self.ID, str(purchaseHistoryIndex)]
            requestContent = [requestID, 'gpr', requestParameters]

            #Envia a requisicao
            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

            #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
            while(response == ""):

                self.sendRequest(requestContent)
                (add, response) = self.listenToResponse()

            #Atualiza o ID de requisicao
            if (int(requestID) < 63):
                requestID = str(int(requestID) + 1)
            else:
                requestID = "1"

        #Caso contrario, atualiza o indice atual da compra analisada
        else:

            purchaseHistoryIndex = str(int(purchaseHistoryIndex) + 1)
        
        #Atualiza informacoes da compra exibida
        displayPurchaseID = response[0]
        displayPurchaseTotal = response[1]
        displayPurchasePrice = response[2]
        displayPurchaseCharge = response[3]
    

#Funcao do thread que monitora mudancas nas informacoes guardadas no arquivo de dados do veiculo
def infoUpdate():

    while True:

        #Carrega as informacoes gravadas (vehicle_data)
        loadedTable = readFile(["vehicledata", "vehicle_data.json"])

        #Modifica as informacoes do objeto do veiculo
        vehicle.battery_level = loadedTable["battery_level"]
        vehicle.capacity = loadedTable["capacity"]

        #Atualiza label de texto do nivel da bateria e do aviso de bateria critica (menos de 30 porcento)
        battery_info_text.set(" Carga: " + str(float(vehicle.battery_level) * 100) + "% => " + str(float(vehicle.capacity) * float(vehicle.battery_level)) + "/" + str(vehicle.capacity) + " KWh ")
        if (float(vehicle.battery_level) < 0.3):
            critical_battery_text.set(" BATERIA EM NÍVEL CRÍTICO! ")
        else:
            critical_battery_text.set(" BATERIA NORMAL ")
        
        #Atualiza label de texto de informacao da distancia
        if (nearestStationID != ""):
            distance_info_text.set((" DISTANCIA: " + nearestStationDistance + " Km | Preço do KWh: " + nearestStationPrice + " "))
        else:
            distance_info_text.set(nearestStationDistance)

        #Atualiza texto de informacao da proxima compra a ser realizada
        if(len(nextPurchaseID) > 0):
            next_purchase_info_text.set(" UUID da compra: " + nextPurchaseID + " / TOTAL: " + nextAmountToPay + " ")
        else:
            next_purchase_info_text.set(" Não existe compra esperando confirmação. ")

        #Atualiza texto de informacao da ultima compra realizada
        next_purchase_result_text.set(purchaseResult)

        #Atualiza texto das informacoes do historico de compra
        purchaseHistoryID.set(" UUID da compra no histórico: " + displayPurchaseID + " ")
        purchaseHistoryTotal.set(" Valor Total da compra no histórico (BRL): " + displayPurchaseTotal + " ")
        purchaseHistoryPrice.set(" Preço do KWh da compra no histórico (BRL): " + displayPurchasePrice + " ")
        purchaseHistoryCharge.set(" Carga total da compra no histórico (KWh): " + displayPurchaseCharge + " ")


#Programa inicia aqui
#Cria um objeto da classe User
vehicle = User()

#IP do broker MQTT de teste
testBroker = 'broker.emqx.io'

#Valores iniciais do programa
requestID = "0"
nearestStationID = ""
nearestStationDistance = ""
nearestStationPrice = ""
nextPurchaseID = ""
nextAmountToPay = ""
purchaseResult = ""
purchaseHistoryIndex = "0"
displayPurchaseID = "0"
displayPurchaseTotal = "0"
displayPurchasePrice = "0"
displayPurchaseCharge = "0"

#Cria um dicionario dos atributos do veiculo
dataTable = {}

#Pergunta endereco do servidor
serverAddress = input("Insira o endereço IP do servidor: ")

#Pergunta endereco do broker MQTT
broker = input("Insira o endereço IP do broker MQTT (OU PRESSIONE ENTER para utilizar o endereço do servidor conectado): ")

if (broker == ""):
    broker = serverAddress

elif (broker == "test"):
    broker = testBroker

#Verifica se o arquivo de texto "ID.txt" esta presente, e caso nao esteja...
if (verifyFile(["vehicledata"], "ID.txt") == False):
    
    #Cria um novo arquivo
    writeFile(["vehicledata", "ID.txt"], vehicle.registerVehicle())

#Verifica se o arquivo de texto "vehicle_data.json" esta presente, e caso nao esteja...
if (verifyFile(["vehicledata"], "vehicle_data.json") == False):
    
    try:
        dataTable["capacity"] = str(argNumber(sys.argv[1]))
    except:
        dataTable["capacity"] = "100.0"

    try:
        dataTable["autonomy"] = str(argNumber(sys.argv[2]))
    except:
        dataTable["autonomy"] = "300.0"

    try:
        dataTable["battery_level"] = str(argNumber(sys.argv[3]))
    except:
        dataTable["battery_level"] = "0.5"

    try:
        dataTable["coord_x"] = str(argNumber(sys.argv[4]))
    except:
        dataTable["coord_x"] = "1.0"
    
    try:
        dataTable["coord_y"] = str(argNumber(sys.argv[5]))
    except:
        dataTable["coord_y"] = "1.0"

    #E tambem cria o arquivo e preenche com as informacoes contidas no dicionario acima
    writeFile(["vehicledata", "vehicle_data.json"], dataTable)

#Caso esteja presente...
else:

    #Carrega as informacoes gravadas (vehicle_data)
    dataTable = readFile(["vehicledata", "vehicle_data.json"])

    try:
        newBatteryLevel = str(argNumber(sys.argv[1]))
        dataTable["battery_level"] = newBatteryLevel
    except:
        pass

    try:
        newCoordX = str(argNumber(sys.argv[2]))
        dataTable["coord_x"] = newCoordX
    except:
        pass
    
    try:
        newCoordY = str(argNumber(sys.argv[3]))
        dataTable["coord_y"] = newCoordY
    except:
        pass

    #Gravas as informacoes atualizadas passadas por parametros
    writeFile(["vehicledata", "vehicle_data.json"], dataTable)

#Carrega as informacoes gravadas (ID)
vehicle.ID = readFile(["vehicledata", "ID.txt"])


#funçõo auxiliar para obter retorno de placeholders    
def getServerPlaceholders():
    server1 = originPlaceholder.get()
    server2 = destinationPlaceholder.get()
    tuple = (server1,server2)
    return tuple

#Frame1 = Janela principal
frame = ctk.CTk()
frame._set_appearance_mode('dark')
frame.title('Cliente')
frame.geometry('600x800')

userID = ctk.CTkLabel(frame,text=("ID do veiculo " + vehicle.ID + " "))
userID.pack(pady=20)

battery_info_text = ctk.StringVar()
battery_info = ctk.CTkLabel(frame,textvariable=battery_info_text)
battery_info.pack(pady=10)

critical_battery_text = ctk.StringVar()
critical_battery = ctk.CTkLabel(frame,textvariable=critical_battery_text)
critical_battery.pack(pady=20)

spotRequestButton = ctk.CTkButton(frame,text=' Obter a distância até a estação de recarga mais próxima e o preço do KWh ',command=lambda:vehicle.nearestSpotRequest())
spotRequestButton.pack(pady=10)

distance_info_text = ctk.StringVar()
distance_info = ctk.CTkLabel(frame,textvariable=distance_info_text)
distance_info.pack(pady=20)

simulatePayButton = ctk.CTkButton(frame,text=' Gerar guia de pagamento ',command=lambda:vehicle.simulateForNearestSpot())
simulatePayButton.pack(pady=10)

next_purchase_info_text = ctk.StringVar()
next_purchase_info = ctk.CTkLabel(frame,textvariable=next_purchase_info_text)
next_purchase_info.pack(pady=20)

bookButton = ctk.CTkButton(frame,text=' Recarregar totalmente na estação mais próxima ',command=lambda:vehicle.payForNearestSpot())
bookButton.pack(pady=10)

next_purchase_result_text = ctk.StringVar()
next_purchase_result = ctk.CTkLabel(frame,textvariable=next_purchase_result_text)
next_purchase_result.pack(pady=30)

originPlaceholder = ctk.CTkEntry(frame,placeholder_text='Digite o Servidor de origem')
originPlaceholder.pack(pady=10)

destinationPlaceholder = ctk.CTkEntry(frame,placeholder_text='Digite o Servidor de destino')
destinationPlaceholder.pack(pady=10)

validateServersButton = ctk.CTkButton(frame,text=' Selecionar servidores ',command=getServerPlaceholders) #precisa da referência da função correta
validateServersButton.pack(pady=20)

purchaseHistoryID = ctk.StringVar()
purchaseHistoryTotal = ctk.StringVar()
purchaseHistoryPrice = ctk.StringVar()
purchaseHistoryCharge = ctk.StringVar()
#Frame2 = Gerenciador de Rotas

def openRechargeRouteManager():
    frame2 = ctk.CTkToplevel(frame)
    frame2.title('Gerenciar Recargas na Rotas')
    frame2.geometry('600x800')
    frame2.attributes('-topmost',True)
    
    #comandos a serem definidos
    backButton = ctk.CTkButton(frame2,text=' < ')
    backButton.pack(pady=5)

    forwardButton = ctk.CTkButton(frame2,text=' > ')
    forwardButton.pack(pady=20)
    
    def closeRRMWindow():
        frame2.destroy()
        frame2.update()
    closeRRMButton = ctk.CTkButton(frame2,text=' Fechar Gerenciador de Rotas ',command=closeRRMWindow)
    closeRRMButton.pack(pady=20)
openRRMButton = ctk.CTkButton(frame,text=' Gerenciar Recarga na Rota ',command=openRechargeRouteManager)
openRRMButton.pack(pady=10)
#frame3 = histórico
def openHistoryWindow():
    frame3 = ctk.CTkToplevel(frame)
    frame3.title('Histórico')
    frame3.geometry('400x600')
    frame3.attributes('-topmost',True)

    
    purchaseHistoryIDLabel = ctk.CTkLabel(frame3,textvariable=purchaseHistoryID)
    purchaseHistoryIDLabel.pack(pady=5)

    
    purchaseHistoryTotalLabel = ctk.CTkLabel(frame3,textvariable=purchaseHistoryTotal)
    purchaseHistoryTotalLabel.pack(pady=5)

    
    purchaseHistoryPriceLabel = ctk.CTkLabel(frame3,textvariable=purchaseHistoryPrice)
    purchaseHistoryPriceLabel.pack(pady=5)

    
    purchaseHistoryChargeLabel = ctk.CTkLabel(frame3,textvariable=purchaseHistoryCharge)
    purchaseHistoryChargeLabel.pack(pady=10)

    bckButton = ctk.CTkButton(frame3,text=' < ',command=lambda:vehicle.purchaseBackward())
    bckButton.pack(pady=5)

    bckButton = ctk.CTkButton(frame3,text=' > ',command=lambda:vehicle.purchaseForward())
    bckButton.pack(pady=20)
    
    def closeHistoryWindow():
        frame3.destroy()
        frame3.update()
    closeHistoryButton = ctk.CTkButton(frame3,text=' Fechar histórico ',command=closeHistoryWindow)
    closeHistoryButton.pack(pady=20)
    
openHistoryButton = ctk.CTkButton(frame,text=' Abrir Histórico ',command=openHistoryWindow)
openHistoryButton.pack(pady=20)
newThread = threading.Thread(target=infoUpdate, args=())
newThread.start()

frame.mainloop()