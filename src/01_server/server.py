#Importa bibliotecas basicas do python 3
import json
import string
import random
import socket
import datetime
import time
import threading

#Importa os componentes utilizados da biblioteca Paho MQTT
from paho.mqtt import client as mqtt_client

#Importa as bibliotecas customizadas da aplicacao
from lib.db import *
from lib.mf import *
from lib.pr import *

#Lock para manipulacao de arquivos (tambem controla requisicoes pois todo o processo e baseado em leitura e escrita de arquivos)
fileLock = threading.Lock()

#Locks para uso dos sockets
senderLock = threading.Lock()
receiverLock = threading.Lock()

#Lock para modificacao da variavel randomID
randomIDLock = threading.Lock()

#Maximo de threads simultaneos
maxThreads = 8

#Lista de threads
threadList = []

#ID Aleatorio inicial
randomID = "*"

#Variavel de execucao do programa
isExecuting = True

#Variavel de contagem de fechamentos dos threads
threadCount = 1

serverIP = socket.gethostbyname(socket.gethostname())
broker = 'broker.emqx.io'


#Funcao para obter um novo ID aleatorio
def getRandomID():

    #Globais utilizadas
    global fileLock
    global randomID

    lettersanddigits = string.ascii_uppercase + string.digits

    #Loop para gerar IDs ate satisfazer certas condicoes
    while True:

        newRandomID = ""

        #Concatena os os digitos ou letras aleatorios para um novo ID
        for count in range(0,24):
            newRandomID += random.choice(lettersanddigits)

        #Concatena com ".json" para saber qual e o nome do arquivo a ser analisado
        completeFileName = (newRandomID + ".json")
        
        stationVerify = False
        vehicleVerify = False

        #Verifica se o ID aleatorio ja tem registro em estacoes (raro, mas pode acontecer)
        fileLock.acquire()
        stationVerify = verifyFile(["clientdata", "clients", "stations"], completeFileName)
        fileLock.release()
        
        #Se for o caso
        if (stationVerify == False):
            
            #Faz o mesmo processo para veiculos
            fileLock.acquire()
            vehicleVerify = verifyFile(["clientdata", "clients", "vehicles"], completeFileName)
            fileLock.release()
        
        #Caso o arquivo esperado nao exista
        if ((stationVerify == False) and (vehicleVerify == False) and (randomID != newRandomID)):

            #Retorna o novo ID aleatorio
            return newRandomID
        

#Funcao para receber uma requisicao
def listenToRequest(timeout):
    
    global broker
    port = 1883
    topic = "request"

    add = ("", 0)
    content = ""

    mqttClientReceiver = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    
    setattr(mqttClientReceiver, "decodedBytes", "")

    #Funcao que determina o que acontece quando uma mensagem e recebida em um topico assinado
    def on_message(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
        setattr(client, "decodedBytes", msg.payload.decode())
        
    mqttClientReceiver.on_message = on_message

    receiverLock.acquire()

    try:
        #Conecta ao broker com os parametros desejados, assina o topico e entra no loop para esperar mensagem(s)
        mqttClientReceiver.connect(broker, port)
        mqttClientReceiver.subscribe(topic)
        mqttClientReceiver.loop_start()

        start_time = time.time()

        while (((time.time() - start_time) < timeout) and (mqttClientReceiver.decodedBytes == "")):
            pass
            
        mqttClientReceiver.loop_stop()
        mqttClientReceiver.unsubscribe(topic)
        mqttClientReceiver.disconnect()

    except:
        pass

    receiverLock.release()

    #print("=============================================")
    #print(decodedBytes)
    #print("=============================================")
    
    try:
        #De-serializa a mensagem decodificada 
        unserializedObj = json.loads(mqttClientReceiver.decodedBytes)

        #Se uma resposta valida foi recebida, a mensagem deve ter tamanho 3
        if (len(unserializedObj) == 3):

            #Separa a parte do endereco referente ao endereco IP
            add = (unserializedObj[0], unserializedObj[1])
            content = unserializedObj[2]
    except Exception:
        pass
    
    #Retorna o objeto da mensagem
    return (add, content)

#Funcao para enviar uma resposta de volta ao cliente
def sendResponse(clientAddress, response):

    #Globais utilizadas
    global senderLock
    global serverIP

    #Obtem a string do endereco do cliente
    clientAddressString, _ = clientAddress

    global broker
    port = 1883
    topic = clientAddressString
    
    mqttMessage = [serverIP, port, response]

    #print("--------------------------------------------")
    #print(clientAddressString)
    #print(mqttMessage)
    #print("--------------------------------------------")
    
    try:
        #Serializa a resposta utilizando json
        serializedRequest = json.dumps(mqttMessage)

        senderLock.acquire()

        mqttClientSender = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
        mqttClientSender.connect(broker, port)
        mqttClientSender.loop_start()
        mqttClientSender.publish(topic, serializedRequest)
        mqttClientSender.loop_stop()

        senderLock.release()
    except:
        pass


#Funcao para fazer entrada de requisicao processada
def registerRequestResult(clientAddress, requestID, requestResult):
    
    #Globais utilizadas
    global fileLock

    #Dicionario de propriedades da requisicao
    requestTable = {}
    requestTable["ID"] = requestID
    requestTable["result"] = requestResult
    
    #Obtem a string de endereco do cliente
    clientAddressString, _ = clientAddress
    
    #Concatena o nome do arquivo para a entrada da requisicao
    requestFileName = (clientAddressString.strip('.') + ".json")
    
    #Cria uma entrada referente a requisicao e ao resultado obtido
    fileLock.acquire()
    writeFile(["clientdata", "requests", requestFileName], requestTable)
    fileLock.release()

#Funcao para registrar uma entrada no log
def registerLogEntry(fileDir, entryLabel, logRequesterLabel, requester):
    
    #Acha a data local de hoje
    localDate = str(datetime.date.today())

    #Concatena o nome do arquivo e faz append com a lista do diretorio
    logFileName = localDate + ".txt"
    fileDir.append(logFileName)

    #Acha o tempo preciso local do momento
    localTimeStamp = str(datetime.datetime.now())

    #Concatena a entrada que sera registrada no log
    #Formato: [TIMESTAMP] NAME: nome-da-entrada ; ADDRESS/ID: 
    logEntry = ("[" + localTimeStamp + "] NAME: " + entryLabel + " ; " + logRequesterLabel + ": " + requester + "\n")
    
    #Adiciona a entrada no arquivo de log correspondente
    fileLock.acquire()
    appendFile(fileDir, logEntry)
    fileLock.release()


#Funcao para registrar uma estacao de recarga
def registerChargeStation(requestID, stationAddress, requestParameters):
    
    #Globais utilizadas
    global fileLock
    global randomIDLock
    global randomID

    #Caso os parametros da requisicao sejam do tamanho adequado...
    if (len(requestParameters) >= 4):
        
        #...Recupera o ID da estacao
        stationID = requestParameters[0]

        requestSuccess = False

        randomIDLock.acquire()

        #Caso o ID da estacao fornecido seja igual ao ID aleatorio atual esperado
        if (stationID == randomID):

            #Cria o dicionario das informacoes e preenche com as informacoes passadas como parametros da requisicao e com o tempo atual desde do EPOCH
            stationInfo = {}
            stationInfo["coord_x"] = requestParameters[1]
            stationInfo["coord_y"] = requestParameters[2]
            stationInfo["unitary_price"] = requestParameters[3]
            stationInfo["actual_vehicle"] = ""
            stationInfo["remaining_charge"] = "0"
            stationInfo["last_online"] = str(time.time())
            
            #Concatena o nome do arquivo/
            fileName = (randomID + ".json")

            #Grava as informacoes em arquivo de texto
            fileLock.acquire()
            writeFile(["clientdata", "clients", "stations", fileName], stationInfo)
            fileLock.release()
            
            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            registerRequestResult(stationAddress, requestID, 'OK')

            #Registra no log
            registerLogEntry(["logs", "performed"], "RGTSTATION", "S_ID", stationID)

            #Gera um novo ID aleatorio e exibe mensagem para conhecimento do mesmo
            randomID = getRandomID()
            print("ID para o proximo cadastro de estacao de carga: " + randomID)

            requestSuccess = True

        randomIDLock.release()
        
        if(requestSuccess ==True):

            #Responde o status da requisicao para o cliente
            sendResponse(stationAddress, 'OK')
        
        else:

            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            registerRequestResult(stationAddress, requestID, 'ERR')

            #Responde o status da requisicao para o cliente
            sendResponse(stationAddress, 'ERR')
    
    else:

        #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
        registerRequestResult(stationAddress, requestID, 'ERR')

        #Responde o status da requisicao para o cliente
        sendResponse(stationAddress, 'ERR')


#Funcao para registrar novo veiculo
def registerVehicle(requestID, vehicleAddress):
    
    #Globais utilizadas
    global fileLock
    global randomIDLock

    #...cria um dicionario dos atributos do veiculo e preenche com valores iniciais
    #Valores dos pares chave-valor sao sempre string para evitar problemas com json
    dataTable = {}
    dataTable["purchases"] = []

    randomIDLock.acquire()
        
    #Obtem um ID aleatorio para o veiculo
    vehicleRandomID = getRandomID()

    #Concatena a string do nome do arquivo do veiculo
    vehicleFileName = (vehicleRandomID + ".json")

    #Cria um novo arquivo para o veiculo
    fileLock.acquire()
    writeFile(["clientdata", "clients", "vehicles", vehicleFileName], dataTable)
    fileLock.release()

    randomIDLock.release()

    #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
    registerRequestResult(vehicleAddress, requestID, vehicleRandomID)

    #Registra no log
    registerLogEntry(["logs", "performed"], "RGTVEHICLE", "V_ID", vehicleRandomID)

    #Responde o status da requisicao para o cliente
    sendResponse(vehicleAddress, vehicleRandomID)

#Funcao para verificar o veiculo atualmente reservado em determinada estacao de carga
def getBookedVehicle(requestID, stationAddress, requestParameters):
    
    #Globais utilizadas
    global fileLock

    #Caso os parametros da requisicao sejam do tamanho adequado...
    if (len(requestParameters) >= 1):

        #...Recupera o ID da estacao
        stationID = requestParameters[0]

        #Concatena o nome do arquivo/
        fileName = (stationID + ".json")

        #Verifica se existe a estacao de carga com o ID fornecido (por meio de verificacao do arquivo de nome exato)
        fileLock.acquire()
        stationVerify = verifyFile(["clientdata", "clients", "stations"], fileName)
        fileLock.release()

        #Caso o ID da estacao seja valido
        if((stationVerify == True) and (len(stationID) == 24)):

            #Obtem o tempo atual, para marcar como online
            lastOnline = str(time.time())

            fileLock.acquire()

            #Recupera informacoes da estacao de carga
            stationInfo = readFile(["clientdata", "clients", "stations", fileName])
            
            #Insere a informacao de ultimo momento online
            stationInfo["last_online"] = lastOnline
            
            #Grava a informacao atualizada (controle de estacoes online)
            writeFile(["clientdata", "clients", "stations", fileName], stationInfo)
            
            fileLock.release()

            #Separa as informacoes desejadas
            bookedVehicle = stationInfo["actual_vehicle"]
            remainingCharge = stationInfo["remaining_charge"]
            
            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            registerRequestResult(stationAddress, requestID, [bookedVehicle, remainingCharge])

            #Registra no log
            registerLogEntry(["logs", "performed"], "GETBOOKED", "S_ID", stationID)
            
            #Responde o status da requisicao para o cliente
            sendResponse(stationAddress, [bookedVehicle, remainingCharge])
            
        else:
            
            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            registerRequestResult(stationAddress, requestID, ['NF',""])
            
            #Responde o status da requisicao para o cliente
            sendResponse(stationAddress, ['NF',""])

#Funcao para liberar estacao de carga
def freeChargingStation(requestID, stationAddress, requestParameters):
    
    #Globais utilizadas
    global fileLock

    #Caso os parametros da requisicao sejam do tamanho adequado...
    if (len(requestParameters) >= 1):

        #...Recupera o ID da estacao
        stationID = requestParameters[0]

        #Concatena o nome do arquivo/
        fileName = (stationID + ".json")

        fileLock.acquire()

        #Verifica se existe estacao com o ID fornecido
        stationVerify = verifyFile(["clientdata", "clients", "stations"], fileName)

        #Caso o ID da estacao seja valido
        if((stationVerify == True) and (len(stationID) == 24)):
            
            #Recupera informacoes da estacao de carga
            stationInfo = readFile(["clientdata", "clients", "stations", fileName])

            #Insere as novas informacoes
            stationInfo["last_online"] = str(time.time())
            stationInfo["actual_vehicle"] = ""
            stationInfo["remaining_charge"] = "0"

            #Grava as informacoes em arquivo de texto
            writeFile(["clientdata", "clients", "stations", fileName], stationInfo)

        fileLock.release()

        if(stationVerify == True):
            
            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            registerRequestResult(stationAddress, requestID, 'OK')

            #Registra no log
            registerLogEntry(["logs", "performed"], "FREESPOT", "S_ID", stationID)
            
            #Responde o status da requisicao para o cliente
            sendResponse(stationAddress, 'OK')
            
        else:
            
            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            registerRequestResult(stationAddress, requestID, 'NF')
            
            #Responde o status da requisicao para o cliente
            sendResponse(stationAddress, 'NF')
            

#Funcao para retornar a distancia ate o posto de recarga mais proximo e seu ID
def respondWithDistance(requestID, vehicleAddress, requestParameters):

    #Globais utilizadas
    global fileLock

    #Informacoes iniciais da mensagem de resposta
    IDToReturn = "0"
    distanceToReturn = 0
    unitaryPriceToReturn = "0"

    fileLock.acquire()

    #Adquire uma lista com o nome dos arquivos de todas as estacoes
    stationList = listFiles(["clientdata", "clients", "stations"])

    #Loop que percorre a lista de estacoes de carga
    for stationIndex in range(0, len(stationList)):
        
        #Nome 
        actualStationFileName = stationList[stationIndex]

        if (len(actualStationFileName) == 29):

            actualID = ""
            
            #Acha o ID da estacao a retornar
            for IDIndex in range(0, 24):
                    
                actualID += actualStationFileName[IDIndex]

            #Carrega as informacoes da estacao atual
            actualStationTable = readFile(["clientdata", "clients", "stations", actualStationFileName])

            #Calcula a distancia
            actualDistance = getDistance(float(requestParameters[0]), float(requestParameters[1]), float(actualStationTable["coord_x"]), float(actualStationTable["coord_y"]))

            isOnline = False

            #Verifica se a ultima vez online foi a menos de 2 minutos e 15 segundos
            if(((float(time.time())) - (float(actualStationTable["last_online"]))) < 135):

                #Esta online
                isOnline = True

            #Se a estacao estiver disponivel e se estivermos no primeiro indice da lista ou se a nova menor distancia for menor que a ultima
            if ((isOnline == True) and (actualStationTable["actual_vehicle"] == "") and ((IDToReturn == "0") or (actualDistance < distanceToReturn))):
                
                #Atualiza os valores a serem retornados (achou distancia menor)
                distanceToReturn = actualDistance
                unitaryPriceToReturn = actualStationTable["unitary_price"]
                IDToReturn = actualID

    fileLock.release()

    #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
    registerRequestResult(vehicleAddress, requestID, [IDToReturn, str(distanceToReturn), unitaryPriceToReturn])

    #Separa a string do endereco IP do veiculo
    vehicleAddressString, _ = vehicleAddress

    #Registra no log
    registerLogEntry(["logs", "performed"], "GETDISTANCE", "V_ADD", vehicleAddressString)

    #Responde o status da requisicao para o cliente
    sendResponse(vehicleAddress, [IDToReturn, str(distanceToReturn), unitaryPriceToReturn])

#Funcao para tentar realizar (reserva de) abastecimento
def attemptCharge(requestID, vehicleAddress, requestParameters):

    #Globais utilizadas
    global fileLock

    #Caso os parametros da requisicao sejam do tamanho adequado...
    if (len(requestParameters) >= 4):

        #Recupera as informacoes
        purchaseID = requestParameters[0]
        vehicleID = requestParameters[1]
        stationID = requestParameters[2]
        paidAmmount = requestParameters[3]

        #Nome do arquivo do veiculo de carga a ser analizado
        vehicleFileName = (vehicleID + ".json")
        #Nome do arquivo da estacao de carga a ser analizado
        stationFileName = (stationID + ".json")

        stationVerify = False
        vehicleVerify = False

        fileLock.acquire()
        stationVerify = verifyFile(["clientdata", "clients", "stations"], stationFileName)
        fileLock.release()
            
        if ((stationVerify == True) and (len(stationID) == 24)):
            
            #Zona de exclusao mutua referente a manipulacao de arquivos
            fileLock.acquire()
            vehicleVerify = verifyFile(["clientdata", "clients", "vehicles"], vehicleFileName)
            fileLock.release()

        #Caso o ID do veiculo/estacao fornecidos sejam validos e a compra seja confirmada
        if ((vehicleVerify == True) and (len(vehicleID) == 24) and (stationVerify == True) and confirmPurchase(purchaseID) == True):

            purchaseDone = False

            fileLock.acquire()
                
            #Carrega o dicionario de informacoes da estacao
            stationInfo = readFile(["clientdata", "clients", "stations", stationFileName])

            #Caso o ponto de carga esteja disponivel para a operacao
            if (stationInfo["actual_vehicle"] == ""):

                #Nome do arquivo da compra
                purchaseFileName = (purchaseID + ".json")

                chargeAmount = str((float(paidAmmount))/float(stationInfo["unitary_price"]))

                #Cria um dicionario das informacoes da compra, adiciona informacoes e grava um arquivo
                purchaseTable = {}
                purchaseTable["vehicle_ID"] = vehicleID
                purchaseTable["station_ID"] = stationID
                purchaseTable["total"] = paidAmmount
                purchaseTable["unitary_price"] = stationInfo["unitary_price"]
                purchaseTable["charge_amount"] = chargeAmount

                #Carrega o dicionario de informacoes do veiculo, Adiciona a compra a lista de compras do veiculo (cliente) e grava o resultado
                vehicleInfo = readFile(["clientdata", "clients", "vehicles", vehicleFileName])
                vehicleInfo["purchases"].append(purchaseID)

                #Modifica o veiculo atual na estacao de carga e grava o resultado
                stationInfo["actual_vehicle"] = vehicleID
                stationInfo["remaining_charge"] = chargeAmount

                #Grava o resultado das acoes
                writeFile(["clientdata", "purchases", purchaseFileName], purchaseTable)
                writeFile(["clientdata", "clients", "vehicles", vehicleFileName], vehicleInfo)
                writeFile(["clientdata", "clients", "stations", stationFileName], stationInfo)

                #Marca a compra como feita
                purchaseDone = True

            fileLock.release()

            #Caso a compra seja feita
            if (purchaseDone == True):

                #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
                registerRequestResult(vehicleAddress, requestID, 'OK')

                #Registra no log
                registerLogEntry(["logs", "performed"], "PHCCHARGE", "P_ID", purchaseID)
                
                #Envia mensagem de resposta ao veiculo
                sendResponse(vehicleAddress, 'OK')

            else:
                
                #Caso contrario (slot de carga ocupado durante a compra), cancela a compra
                cancelPurchase(purchaseID)

                #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
                registerRequestResult(vehicleAddress, requestID, 'ERR')

                #Envia mensagem de resposta ao veiculo
                sendResponse(vehicleAddress, 'ERR')

        else:

            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            registerRequestResult(vehicleAddress, requestID, 'ERR')

            #Responde o status da requisicao para o cliente
            sendResponse(vehicleAddress, 'ERR')

    else:

        #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
        registerRequestResult(vehicleAddress, requestID, 'ERR')

        #Responde o status da requisicao para o cliente
        sendResponse(vehicleAddress, 'ERR')

#Funcao para retornar informacoes de uma compra em especifico
def respondWithPurchase(requestID, vehicleAddress, requestParameters):

    #Globais utilizadas
    global fileLock

    #Informacoes iniciais da mensagem de resposta
    purchaseIDToReturn = "0"
    totalToReturn = "0"
    unitaryPriceToReturn = "0"
    amountToReturn = "0"

    #Se estiver no formato adequado
    if(len(requestParameters) >= 2):
        
        #Le as informacoes nos parametros da requisicao e concatena o nome do arquivo do veiculo
        vehicleFileName = (requestParameters[0] + ".json")
        purchaseIndex = requestParameters[1]

        #Verifica se existe veiculo com o ID especificado
        fileLock.acquire()
        verifyVehicle = verifyFile(["clientdata", "clients", "vehicles"], vehicleFileName)
        fileLock.release()

        #Se existe veiculo valido no ID e o indice e numerico
        if((purchaseIndex.isnumeric() == True) and (verifyVehicle == True) and (len(vehicleFileName) == 29)):
            
            #Le o arquivo do veiculo com o ID especificado
            fileLock.acquire()
            vehicleInfo = readFile(["clientdata", "clients", "vehicles", vehicleFileName])
            fileLock.release()

            #Lista as compras feitas pelo veiculo
            purchaseList = vehicleInfo["purchases"]
            
            #Verifica se existe compra no indice especificado da lista
            if ((len(purchaseList) > int(purchaseIndex)) and (int(purchaseIndex) >= 0)):
                
                #Resgata o ID da compra e concatena o nome do arquivo da compra
                purchaseID = purchaseList[int(purchaseIndex)]
                purchaseFileName = (purchaseID + ".json")

                #Carrega o arquivo de compra
                fileLock.acquire()
                purchaseInfo = readFile(["clientdata", "purchases", purchaseFileName])
                fileLock.release()
                
                #Atualiza informacoes da resposta de acordo com o que foi carregado
                purchaseIDToReturn = purchaseID
                totalToReturn = purchaseInfo["total"]
                unitaryPriceToReturn = purchaseInfo["unitary_price"]
                amountToReturn = purchaseInfo["charge_amount"]

    #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
    registerRequestResult(vehicleAddress, requestID, [purchaseIDToReturn, totalToReturn, unitaryPriceToReturn, amountToReturn])

    #Separa a string do endereco IP do veiculo
    vehicleAddressString, _ = vehicleAddress

    #Registra no log
    registerLogEntry(["logs", "performed"], "PCHDETAILS", "V_ADD", vehicleAddressString)

    #Responde o status da requisicao para o cliente
    sendResponse(vehicleAddress, [purchaseIDToReturn, totalToReturn, unitaryPriceToReturn, amountToReturn])


#Funcao para cada thread que espera uma requisicao
def requestCatcher():

    #Globais utilizadas
    global isExecuting
    global threadCount

    #Loop da thread
    while (isExecuting == True):

        #Espera chegar uma requisicao
        clientAddress, requestInfo = listenToRequest(5)

        #Obtem a string de endereco do cliente
        clientAddressString, _ = clientAddress

        #Se o tamamanho da lista de requisicao for adequado
        if (len(requestInfo) >= 3):
            
            #Recupera as informacoes da lista de requisicao
            requestID = requestInfo[0]
            requestName = requestInfo[1]
            requestParameters = requestInfo[2]

            #Concatena o nome do arquivo para a entrada da requisicao
            requestFileName = (clientAddressString.strip('.') + ".json")

            #Variavel que diz se a requisicao sera executada
            willExecute = True

            #Resultado da requisicao, inicialmente vazio
            requestResult = ""

            requestVerify = False
            
            #Verifica se a requisicao atual tem ID diferente de 0 e se vem de um endereco que ja fez requisicoes
            if ((requestID != "0" )):
                
                #Verifica se ja existe um arquivo de requisicao para o endereco
                fileLock.acquire()
                requestVerify = verifyFile(["clientdata", "requests"], requestFileName)
                fileLock.release()

                if(requestVerify == True):
            
                    #Recupera informacoes da ultima requisicao
                    fileLock.acquire()
                    requestTable = readFile(["clientdata", "requests", requestFileName])
                    fileLock.release()
                    storedRequestID = requestTable["ID"]
                    requestResult = requestTable["result"]

                    #Verifica se o ID da ultima requisicao e o mesmo da atual
                    if(requestID == storedRequestID):

                        #Se for, nao sera executada requisicao
                        willExecute = False     
            
            #Caso a intencao de execucao da requisicao ainda estiver de pe
            if (willExecute == True):
                
                #Executa diferente requisicoes dependendo do nome da requisicao (acronimo)
                if (requestName == 'rcs'):
                    
                    registerChargeStation(requestID, clientAddress, requestParameters)
                
                elif (requestName == 'rve'):

                    registerVehicle(requestID, clientAddress)

                elif (requestName == 'gbv'):

                    getBookedVehicle(requestID, clientAddress, requestParameters)

                elif (requestName == 'fcs'):

                    freeChargingStation(requestID, clientAddress, requestParameters)
                
                elif (requestName == 'bcs'):
                    
                    attemptCharge(requestID, clientAddress, requestParameters)
                
                elif (requestName == 'nsr'):

                    respondWithDistance(requestID,clientAddress,requestParameters)
                
                elif(requestName == 'gpr'):

                    respondWithPurchase(requestID, clientAddress, requestParameters)
            
            #Caso contrario, manda a resposta novamente
            else:

                sendResponse(clientAddress, requestResult)

        #Caso contrario e se o endereco do cliente nao for vazio
        elif clientAddressString != "":
            
            #Responde que a requisicao e invalida
            sendResponse(clientAddress, 'ERR')
    
    print("THREAD ENCERRADO (" + str(threadCount) + "/" + str(maxThreads) + ")")
    threadCount += 1


#Inicio do programa

#Obtem e printa o endereco IP do servidor
hostAddress = socket.gethostbyname(socket.gethostname())
print("ENDERECO IP DO SERVIDOR: " + hostAddress)

#Obtem um ID aleatorio de 24 elementos alfanumericos e exibe mensagem da operacao
randomID = getRandomID()
print("ID para o proximo cadastro de estacao de carga: " + randomID)

#Exibe mensagem que diz como sair da aplicacao
print("PRESSIONE ENTER A QUALQUER MOMENTO PARA ENCERRAR A APLICACAO")

#Loop para indexar todos os threads
for threadIndex in range(0, maxThreads):

    #Cria o thread, inicia e adiciona para a lista
    newThread = threading.Thread(target=requestCatcher, args=())
    newThread.start()
    threadList.append(newThread)

#Fora dos threads, input() apenas segura a execucao do programa principal ate ser pressionado
input()
#Encerra o programa
print("AGUARDE O ENCERRAMENTO:")
isExecuting = False