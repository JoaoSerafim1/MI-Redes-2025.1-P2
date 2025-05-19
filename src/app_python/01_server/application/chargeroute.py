###########################################################
#
# => MODULO DE GERENCIAMENTO DE LEITURA DE ROTAS E RESERVA DE INTINERARIOS <=
#
###########################################################


#Importa bibliotecas basicas do python 3
import threading
import time
import requests

#Importa as bibliotecas customizadas da aplicacao
from application.lib.mf import *

#Importa os modulos da aplicacao
from application.mqtt import *
from application.rest import httpPort


#Funcao para fazer uma requisicao a partir de um servidor-remetente e ler a resposta
def httpRequest(fileLock: threading.Lock, destinyServerAddress, port, timeout, payload):

    url = 'http://' + destinyServerAddress + ':' + str(port) + '/submit'
    
    #Variavel do conteudo retornado, inicialmente string vazia
    content = ""

    #Tenta conectar ao servidor remoto e fazer a requisicao
    try:
        
        response = requests.post(url, json=payload, timeout=timeout)

        #Verifica a resposta
        if response.status_code == 200:
            content = response.json()

        #print("=============================================")
        #print(url)
        #print(payload)
        #print("+++++++++++++++++++++++++++++++++++++++++++++")
        #print(response)
        #print(content)
        #print("=============================================")
        
        #Registra no log
        registerLogEntry(fileLock, ["logs", "received"], "HTTPRESPONSE", "ADDRESS", destinyServerAddress)
    
    #Se falhar, foi devido a timeout
    except:
        pass
    
    #Retorna o objeto da mensagem
    return content


#Funcao para retornar informacoes de uma rota em especifico
def respondWithRoute(fileLock: threading.Lock, senderLock: threading.Lock, broker, port, serverAddress, requestID, vehicleAddress, requestParameters):

    #Informacoes iniciais da mensagem de resposta
    serverRouteIndex = "-1"
    routeNodeNameList = []

    #Se estiver no formato adequado
    try:
        
        routeIndex = requestParameters[0]
        routeEndAddress = str(requestParameters[1])

        #Se o indice e numerico e o endereco de destino maior que 1
        if((routeIndex.isnumeric() == True) and (int(routeIndex) >= 0) and (len(routeEndAddress) > 0)):

            routeIndex = int(routeIndex)
            
            #Le o arquivo do veiculo com o ID especificado
            fileLock.acquire()
            routeInfo = readFile(["serverdata", "routes.json"])
            fileLock.release()
            
            validRouteCount = 0
            
            #print(routeInfo)
            #Loop que percorre a lista de rotas
            for routeCount in range(0, len(routeInfo)):
                
                actualRoute = routeInfo[routeCount]
                
                actualRouteEndNode = actualRoute[(-1)]
                
                actualRouteEndAddress = actualRouteEndNode[0]
                
                #Se a origem e o destino da rota correspondem ao desejado
                if (routeEndAddress == actualRouteEndAddress):
                    
                    #Se o indice tambem for igual ao contador de rotas validas
                    if(routeIndex == validRouteCount):

                        routeNodeNameList

                        #O indice da rota como visto no servidor a ser retornado ao cliente para uso posterior
                        serverRouteIndex = str(routeCount)
                        
                        #Percorre os nos da rota
                        for nodeCount in range(0, len(actualRoute)):
                            
                            actualRouteNode = actualRoute[nodeCount]
                            actualNodeName = actualRouteNode[1]

                            #Adiciona o nome do servidor do no atual na lista de nomes de nos (elemento visual da rota)
                            routeNodeNameList.append(actualNodeName)
                            
                    #Aumenta o contador de rotas validas, para chegar ao indice requisitado
                    validRouteCount += 1
    except:
        pass
    
    #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
    registerRequestResult(fileLock, vehicleAddress, requestID, [serverRouteIndex, routeNodeNameList])
    
    #Separa a string do endereco IP do veiculo
    vehicleAddressString, _ = vehicleAddress
    
    #Registra no log
    registerLogEntry(fileLock, ["logs", "performed"], "RTDETAILS", "V_ADD", vehicleAddressString)
    
    #Responde o status da requisicao para o cliente
    sendResponse(senderLock, broker, port, serverAddress, vehicleAddress, [serverRouteIndex, routeNodeNameList])
    
#Funcao para reservar uma rota
def reserveRoute(fileLock: threading.Lock, senderLock: threading.Lock, broker, port, serverAddress, vehicleRequestID, vehicleAddress, requestParameters):
    
    #Informacoes iniciais da mensagem de resposta
    clientResponse = "ERR"

    #Se estiver no formato adequado em qualquer momento da execucao
    try:
        
        #Parametros da operacao, de acordo com a informacao recebida
        vehicleID = requestParameters[0]
        routeIndex = int(requestParameters[1])
        reservationTimeList = requestParameters[2]
        vehicleAutonomy = float(requestParameters[3])
        coordX = float(requestParameters[4])
        coordY = float(requestParameters[5])
        
        #Le o arquivo de informacoes de rotas
        fileLock.acquire()
        routeInfo = readFile(["serverdata", "routes.json"])
        fileLock.release()
        
        chosenRoute = routeInfo[routeIndex]

        nodeIndex = 0
        noNegativeResponse = True
        
        #Loop que garante que os nos serao percorridos em um dos dois sentidos (ate o final caso nao acontecam problemas ou voltando ate o inicio caso acontecam problemas)
        while ((nodeIndex < len(reservationTimeList)) and (nodeIndex < len(chosenRoute)) and (nodeIndex >= 0)):
            
            #Se nao foram encontrados problemas na reserva, deve ser continuado o processo de reservar pontos
            if (noNegativeResponse == True):
                
                #Informacoes do no atual
                chosenRouteNodeAddress = chosenRoute[nodeIndex][0]
                chosenNodeReservationTime = float(reservationTimeList[nodeIndex])
                
                #Parametros da requisicao a ser enviada ao servidor do no atual (ID do veiculo e o horario desejado)
                serverRequestParameters = [str(vehicleID), chosenNodeReservationTime, vehicleAutonomy, coordX, coordY]

                payload = [str("drr"), serverRequestParameters]
                
                #Manda a mensagem solicitando reserva de um ponto naquele servidor
                actualHttpRequestResponse = httpRequest(fileLock, chosenRouteNodeAddress, httpPort, 10, payload)
                
                #Se a resposta e positiva (lista de tamanho 2), podemos ir usar as coordenadas retornadas para fazer o processo de reserva no proximo no
                if (len(actualHttpRequestResponse) >= 2):
                    
                    coordX = float(actualHttpRequestResponse[0])
                    coordY = float(actualHttpRequestResponse[1])
                    
                    #Aumenta o indice do no
                    nodeIndex += 1
                
                #Mas se nao for, revertemos o sentido de percorrer a lista
                else:

                    noNegativeResponse = False

            #Mas se foram encontrados problemas, o indice e reduzido deve ser desfeita a reserva do no anterior (se o indice to atual for maior ou igual a 0)
            elif (noNegativeResponse == False):
                
                #Diminui o indice do no
                nodeIndex -= 1

                #Se o indice ainda for maior ou igual a zero apos reduzir, e necessario desfazer a reserva naquele servidor
                if(nodeIndex >= 0):

                    #Informacoes do no atual
                    chosenRouteNodeAddress = chosenRoute[nodeIndex][0]

                    #Parametros da requisicao a ser enviada ao servidor do no atual (ID do veiculo)
                    serverRequestParameters = [str(vehicleID)]

                    payload = [str("urr"), serverRequestParameters]
                    
                    #Manda a mensagem solicitando remocao de reserva de um ponto naquele servidor
                    httpRequest(fileLock, chosenRouteNodeAddress, httpPort, 10, payload)

            #Finalizado o loop, verifica o status da direcao novamente
            #Se ainda estiver normal, a operacao foi bem-sucedida, o que quer dizer que a rota atual do veiculo sera limpa, sera e registrada a nova
            if ((len(reservationTimeList) > 0) and (noNegativeResponse == True)):
                
                clientResponse = "OK"

    except:
        pass

    #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
    registerRequestResult(fileLock, vehicleAddress, vehicleRequestID, clientResponse)

    #Separa a string do endereco IP do veiculo
    vehicleAddressString, _ = vehicleAddress

    #Registra no log
    registerLogEntry(fileLock, ["logs", "performed"], "RESROUTE", "V_ADD", vehicleAddressString)

    #Responde o status da requisicao para o cliente
    sendResponse(senderLock, broker, port, serverAddress, vehicleAddress, clientResponse)


#Funcao para reservar um ponto de recarga
def doReservation(fileLock: threading.Lock, timeWindow, requestParameters):
    
    vehicleID = requestParameters[0]
    reservationTime = float(requestParameters[1])
    vehicleAutonomy = float(requestParameters[2])
    coordX = float(requestParameters[3])
    coordY = float(requestParameters[4])

    fileLock.acquire()

    #Adquire uma lista com o nome dos arquivos de todas as estacoes
    stationList = listFiles(["clientdata", "clients", "stations"])

    stationID = ""
    coordList = []
    actualShortestDistance = 0
    
    #Loop que percorre a lista de estacoes de carga
    for stationIndex in range(0, len(stationList)):
        
        #Nome do arquivo de estacao atual
        actualStationFileName = stationList[stationIndex]

        #Exclui arquivos invalidos (ex: .gitignore)
        if ((len(actualStationFileName) == 29)):
            
            actualID = ""
            
            #Acha o ID da estacao a retornar
            for IDIndex in range(0, 24):
                
                actualID += actualStationFileName[IDIndex]

            #Carrega as informacoes da estacao atual
            actualStationTable = readFile(["clientdata", "clients", "stations", actualStationFileName])
            
            try:
                #Calcula a distancia
                actualDistance = getDistance(float(coordX), float(coordY), float(actualStationTable["coord_x"]), float(actualStationTable["coord_y"]))
                
                isOnline = False
                zeroBookingConflicts = True
                
                #Obtem o tempo atual, para verificar informacao de agendamento
                actualTime = float(time.time())

                #Verifica se a ultima vez online foi a menos de 2 minutos e 15 segundos
                if((actualTime - (float(actualStationTable["last_online"]))) < 135):
                    
                    #Esta online
                    isOnline = True
                
                #Loop para percorrer a o dicionario de veiculos agendandos
                for actualBookedVehicleID in actualStationTable["vehicle_bookings"]:
                    
                    #Tempo atual agendado para a entrada na lista (chave=id do veiculo)
                    bookedTime = actualStationTable["vehicle_bookings"][actualBookedVehicleID]

                    #Se a entrada na agenda nao for do veiculo solicitante e a janela de tempo do agendamento (2 horas antes e depois do horario exato marcado) contemplar o tempo atual, nao podera haver recarga
                    if ((zeroBookingConflicts == True) and (vehicleID != actualBookedVehicleID) and (reservationTime > (bookedTime - timeWindow)) and (reservationTime < (bookedTime + timeWindow))):
                        
                        zeroBookingConflicts = False
                
                #print(actualDistance)
                #print(vehicleAutonomy)
                #print(isOnline)
                #print(zeroBookingConflicts)
                #print(actualShortestDistance)
                #print(stationID)

                #Se a autonomia do veiculo cobrir o trecho (distancia menor que 80% da autonomia), a estacao estiver disponivel e se estivermos no primeiro indice da lista ou se a nova menor distancia for menor que a ultima
                if ((float(actualDistance) < ((vehicleAutonomy) * 0.8)) and (isOnline == True) and (zeroBookingConflicts == True) and ((stationID == "") or (actualDistance < actualShortestDistance))):
                    
                    #Atualiza os valores a serem repassados (achou distancia menor)
                    actualShortestDistance = actualDistance
                    stationID = actualID
                    coordList.clear()
                    coordList.append(actualStationTable["coord_x"])
                    coordList.append(actualStationTable["coord_y"])
            except:
                pass
    
    clientVerify = False

    #Se os clientes possuem ID de 24 de tamanho, significa que ambas sao validos e o agendamento pode ocorrer
    if ((len(stationID) == 24) and (len(vehicleID) == 24)):
        
        clientVerify = True

    #Obtem o tempo atual, para verificar se o horario do agendamento sequer e valido
    actualTime = float(time.time())

    #Caso o ID do veiculo/estacao fornecidos sejam validos e o horario do agendamento esteja alem do horario atual mais a janela de tempo de reserva
    if ((clientVerify == True) and (reservationTime > (actualTime + timeWindow))):

        #Loop que percorre a lista de estacoes de carga
        for stationIndex in range(0, len(stationList)):

            #Nome do arquivo
            actualStationFileName = stationList[stationIndex]

            try:
                #Carrega as informacoes da estacao atual
                actualStationTable = readFile(["clientdata", "clients", "stations", actualStationFileName])

                #Tenta remover a entrada com o ID do veiculo solicitante da lista de agendamento
                del actualStationTable["vehicle_bookings"][vehicleID]

                #Grava o resultado da acao
                writeFile(["clientdata", "clients", "stations", actualStationFileName], actualStationTable)
            except:
                pass
        
        #Nome do arquivo da estacao
        stationFileName = (stationID + ".json")

        #Carrega o dicionario de informacoes da estacao a ser agendada
        stationInfo = readFile(["clientdata", "clients", "stations", stationFileName])

        #Escreve a informacao da reserva
        stationInfo["vehicle_bookings"][vehicleID] = reservationTime

        #Guardas as informacoes
        writeFile(["clientdata", "clients", "stations", stationFileName], stationInfo)

    fileLock.release()
    
    return coordList

#Funcao para desfazer a reserva de um ponto de recarga
def undoReservation(fileLock: threading.Lock, requestParameters):

    vehicleID = requestParameters[0]
    
    fileLock.acquire()
    
    #Adquire uma lista com o nome dos arquivos de todas as estacoes
    stationList = listFiles(["clientdata", "clients", "stations"])
    
    #Loop que percorre a lista de estacoes de carga
    for stationIndex in range(0, len(stationList)):
        
        #Nome do arquivo
        actualStationFileName = stationList[stationIndex]
        
        try:

            #Carrega as informacoes da estacao atual
            actualStationTable = readFile(["clientdata", "clients", "stations", actualStationFileName])
            
            #Tenta remover a entrada com o ID do veiculo solicitante da lista de agendamento
            del actualStationTable["vehicle_bookings"][vehicleID]
            
            #Grava o resultado da acao
            writeFile(["clientdata", "clients", "stations", actualStationFileName], actualStationTable)
            
        except:
            pass

    fileLock.release()

    return True