###########################################################
#
# => MODULO DE GERENCIAMENTO DE CLIENTES <=
#
###########################################################


#Importa bibliotecas basicas do python 3
import threading
import time

#Importa os modulos da aplicacao
from application.mqtt import *


#Funcao para registrar uma estacao de recarga
def registerChargeStation(randomID, senderLock: threading.Lock, broker, port, serverIP, requestID, stationAddress, requestParameters):

    #Funcao local, para eliminar uso de locks dentro da principal (embrulhada com lock de arquivos)
    def registerRequestResultLocal(clientAddress, requestID, requestResult):

        #Dicionario de propriedades da requisicao
        requestTable = {}
        requestTable["ID"] = requestID
        requestTable["result"] = requestResult
        
        #Obtem a string de endereco do cliente
        clientAddressString, _ = clientAddress
        
        #Concatena o nome do arquivo para a entrada da requisicao
        requestFileName = (clientAddressString.strip('.') + ".json")
        
        #Cria uma entrada referente a requisicao e ao resultado obtido
        writeFile(["clientdata", "requests", requestFileName], requestTable)

    #Funcao local, para eliminar uso de locks dentro da principal (embrulhada com lock de arquivos)
    def registerLogEntryLocal(fileDir, entryLabel, logRequesterLabel, requester):
    
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
        appendFile(fileDir, logEntry)

    #Funcao local, para eliminar uso de locks dentro da principal (embrulhada com lock de arquivos)
    def getRandomIDLocal(randomID):

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
            stationVerify = verifyFile(["clientdata", "clients", "stations"], completeFileName)
            
            #Se for o caso
            if (stationVerify == False):
                
                #Faz o mesmo processo para veiculos
                vehicleVerify = verifyFile(["clientdata", "clients", "vehicles"], completeFileName)
            
            #Caso o arquivo esperado nao exista
            if ((stationVerify == False) and (vehicleVerify == False) and (randomID != newRandomID)):

                #Retorna o novo ID aleatorio
                return newRandomID
    
    #Caso os parametros da requisicao sejam do tamanho adequado...
    if (len(requestParameters) >= 4):

        #...Recupera o ID da estacao
        stationID = requestParameters[0]

        requestSuccess = False

        #Caso o ID da estacao fornecido seja igual ao ID aleatorio atual esperado
        if (stationID == randomID):

            #Cria o dicionario das informacoes e preenche com as informacoes passadas como parametros da requisicao e com o tempo atual desde do EPOCH
            stationInfo = {}
            stationInfo["coord_x"] = requestParameters[1]
            stationInfo["coord_y"] = requestParameters[2]
            stationInfo["unitary_price"] = requestParameters[3]
            stationInfo["vehicle_bookings"] = {}
            stationInfo["actual_vehicle"] = ""
            stationInfo["remaining_charge"] = "0"
            stationInfo["last_online"] = str(time.time())
            
            #Concatena o nome do arquivo/
            fileName = (randomID + ".json")

            writeFile(["clientdata", "clients", "stations", fileName], stationInfo)
            
            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            registerRequestResultLocal(stationAddress, requestID, 'OK')

            #Registra no log
            registerLogEntryLocal(["logs", "performed"], "RGTSTATION", "S_ID", stationID)

            #Gera um novo ID aleatorio e exibe mensagem para conhecimento do mesmo
            randomID = getRandomIDLocal(randomID)
            print("ID para o proximo cadastro de estacao de carga: " + randomID)

            requestSuccess = True
        
        if(requestSuccess ==True):

            #Responde o status da requisicao para o cliente
            sendResponse(senderLock, broker, port, serverIP, stationAddress, 'OK')
        
        else:

            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            registerRequestResultLocal(stationAddress, requestID, 'ERR')

            #Responde o status da requisicao para o cliente
            sendResponse(senderLock, broker, port, serverIP, stationAddress, 'ERR')
    
    else:

        #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
        registerRequestResultLocal(stationAddress, requestID, 'ERR')

        #Responde o status da requisicao para o cliente
        sendResponse(senderLock, broker, port, serverIP, stationAddress, 'ERR')
    
    return randomID


#Funcao para registrar novo veiculo
def registerVehicle(fileLock: threading.Lock, randomIDLock: threading.Lock, randomID, senderLock: threading.Lock, broker, port, serverIP, requestID, vehicleAddress):

    #Cria um dicionario dos atributos do veiculo e preenche com valores iniciais
    #Valores dos pares chave-valor sao sempre string para evitar problemas com json
    dataTable = {}
    dataTable["purchases"] = []

    #dataTable["last_routed_at"] = "0"
    #dataTable["last_route"] = []

    randomIDLock.acquire()
        
    #Obtem um ID aleatorio para o veiculo
    vehicleRandomID = getRandomID(fileLock, randomID)

    #Concatena a string do nome do arquivo do veiculo
    vehicleFileName = (vehicleRandomID + ".json")

    #Cria um novo arquivo para o veiculo
    fileLock.acquire()
    writeFile(["clientdata", "clients", "vehicles", vehicleFileName], dataTable)
    fileLock.release()

    randomIDLock.release()

    #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
    registerRequestResult(fileLock, vehicleAddress, requestID, vehicleRandomID)

    #Registra no log
    registerLogEntry(fileLock, ["logs", "performed"], "RGTVEHICLE", "V_ID", vehicleRandomID)

    #Responde o status da requisicao para o cliente
    sendResponse(senderLock, broker, port, serverIP, vehicleAddress, vehicleRandomID)

#Funcao para verificar o veiculo atualmente reservado em determinada estacao de carga
def getBookedVehicle(fileLock: threading.Lock, senderLock: threading.Lock, broker, port, serverIP, requestID, stationAddress, requestParameters):

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
            registerRequestResult(fileLock, stationAddress, requestID, [bookedVehicle, remainingCharge])

            #Registra no log
            registerLogEntry(fileLock, ["logs", "performed"], "GETBOOKED", "S_ID", stationID)
            
            #Responde o status da requisicao para o cliente
            sendResponse(senderLock, broker, port, serverIP, stationAddress, [bookedVehicle, remainingCharge])
            
        else:
            
            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            registerRequestResult(fileLock, stationAddress, requestID, ['NF',""])
            
            #Responde o status da requisicao para o cliente
            sendResponse(senderLock, broker, port, serverIP, stationAddress, ['NF',""])

    #Funcao para retornar informacoes de uma compra em especifico
def respondWithPurchase(fileLock: threading.Lock, senderLock: threading.Lock, broker, port, serverIP, requestID, vehicleAddress, requestParameters):

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
    registerRequestResult(fileLock, vehicleAddress, requestID, [purchaseIDToReturn, totalToReturn, unitaryPriceToReturn, amountToReturn])

    #Separa a string do endereco IP do veiculo
    vehicleAddressString, _ = vehicleAddress

    #Registra no log
    registerLogEntry(fileLock, ["logs", "performed"], "PCHDETAILS", "V_ADD", vehicleAddressString)

    #Responde o status da requisicao para o cliente
    sendResponse(senderLock, broker, port, serverIP, vehicleAddress, [purchaseIDToReturn, totalToReturn, unitaryPriceToReturn, amountToReturn])