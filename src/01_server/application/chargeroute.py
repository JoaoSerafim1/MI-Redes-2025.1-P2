###########################################################
#
# => MODULO DE GERENCIAMENTO DE LEITURA DE ROTAS E RESERVA DE INTINERARIOS <=
#
###########################################################


#Importa bibliotecas basicas do python 3
import threading
import time

#Importa as bibliotecas customizadas da aplicacao
from application.lib.mf import *

#Importa os modulos da aplicacao
from application.mqtt import *
from application.rest import *


#Funcao para retornar informacoes de uma rota em especifico
def respondWithRoute(fileLock: threading.Lock, senderLock: threading.Lock, broker, port, serverAddress, requestID, vehicleAddress, requestParameters):

    #Informacoes iniciais da mensagem de resposta
    serverRouteIndex = (-1)
    routeNodeNameList = []

    #Se estiver no formato adequado
    try:
        
        routeIndex = requestParameters[0]
        routeStartAddress = requestParameters[1]
        routeEndAddress = requestParameters[2]

        #Se o indice e numerico
        if((routeIndex.isnumeric() == True)):
            
            #Le o arquivo do veiculo com o ID especificado
            fileLock.acquire()
            routeInfo = readFile(["serverdata", "routes.json"])
            fileLock.release()

            validRouteCount = 0 
            
            #Loop que percorre a lista de rotas
            for routeCount in range(0, len(routeInfo)):
                
                actualRoute = routeInfo[routeCount]

                actualRouteStartNode = actualRoute[0]
                actualRouteEndNode = actualRoute[(-1)]

                actualRouteStartAddress, _ = actualRouteStartNode
                actualRouteEndAddress, _ = actualRouteEndNode

                #Se a origem e o destino da rota correspondem ao desejado
                if ((routeStartAddress == actualRouteStartAddress) and (routeEndAddress == actualRouteEndAddress)):

                    #Se o indice tambem for igual ao contador de rotas validas
                    if(routeIndex == validRouteCount):
                        
                        #O indice da rota como visto no servidor a ser retornado ao cliente para uso posterior
                        serverRouteIndex = routeCount

                        #Percorre os nos da rota
                        for nodeCount in range(0, len(actualRoute)):
                            
                            actualRouteNode = actualRoute[nodeCount]
                            _, actualNodeName = actualRouteNode

                            #Adiciona o nome do servidor do no atual na lista de nomes de nos (elemento visual da rota)
                            routeNodeNameList.append(actualNodeName)

                    #Caso contrario
                    else:

                        #Aumenta o contador de rotas validas, para chegar ao indice requisitado
                        validRouteCount += 1
    except:
        pass

    #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
    registerRequestResult(fileLock, vehicleAddress, requestID, [serverRouteIndex, routeNodeNameList])

    #Separa a string do endereco IP do veiculo
    vehicleAddressString, _ = vehicleAddress

    #Registra no log
    registerLogEntry(["logs", "performed"], "RTDETAILS", "V_ADD", vehicleAddressString)

    #Responde o status da requisicao para o cliente
    sendResponse(senderLock, broker, port, serverAddress, vehicleAddress, [serverRouteIndex, routeNodeNameList])

#Funcao para reservar uma rota
def reserveRoute(fileLock: threading.Lock, senderLock: threading.Lock, broker, port, serverAddress, vehicleRequestID, vehicleAddress, requestParameters):
    
    #Informacoes iniciais da mensagem de resposta
    response = "ERR"

    #Se estiver no formato adequado em qualquer momento da execucao
    try:

        #Parametros da operacao, de acordo com a informacao recebida
        vehicleID = requestParameters[0]
        routeIndex = requestParameters[1]
        reservationTimeList = requestParameters[2]
        vehicleAutonomy = requestParameters[3]
        coordX = requestParameters[5]
        coordY = requestParameters[6]
            
        #Le o arquivo de informacoes de rotas
        fileLock.acquire()
        routeInfo = readFile(["serverdata", "routes.json"])
        fileLock.release()

        chosenRoute = routeInfo[routeIndex]

        nodeIndex = 0
        noNegativeResponse = True

        #Loop que garante que os nos serao percorridos em um dos dois sentidos (ate o final caso nao acontecam problemas ou voltando ate o inicio caso acontecam problemas)
        while ((nodeIndex >= 0) and (nodeIndex < len(chosenRoute))):
            
            #Se nao foram encontrados problemas na reserva, deve ser continuado o processo de reservar pontos
            if (noNegativeResponse == True):
                
                #Informacoes do no atual
                chosenRouteNodeAddress, _ = chosenRoute[nodeIndex]
                chosenNodeReservationTime = reservationTimeList[nodeIndex]

                #Parametros da requisicao a ser enviada ao servidor do no atual (ID do veiculo e o horario desejado)
                serverRequestParameters = [vehicleID, chosenNodeReservationTime, vehicleAutonomy, coordX, coordY]
                
                #Manda a mensagem solicitando reserva de um ponto naquele servidor
                sendServerMessage(chosenRouteNodeAddress, ["drr", serverRequestParameters])

                content = listenToServerMessage(fileLock, 10)

                #Se a resposta e positiva, podemos ir usar as proximas coordenadas e ir ao proximo elemento
                if (len(content) >= 2):
                    
                    coordX = str(content[0])
                    coordY = str(content[1])
                    
                    #Aumenta o indice do no
                    nodeIndex += 1
                
                #Mas se nao for, revertemos o sentido de percorrer a lista
                else:

                    noNegativeResponse = False

            #Mas se foram encontrados problemas, deve ser desfeita a reserva do no anterior (se o indice to atual for maior ou igual a 0)
            elif ((noNegativeResponse == False) and (nodeIndex > 0)):
                
                #Diminui o indice do no
                nodeIndex -= 1

                #Informacoes do no atual
                chosenRouteNodeAddress, _ = chosenRoute[nodeIndex]

                #Parametros da requisicao a ser enviada ao servidor do no atual (ID do veiculo)
                serverRequestParameters = [vehicleID]
                
                #Manda a mensagem solicitando remocao de reserva de um ponto naquele servidor
                sendServerMessage(chosenRouteNodeAddress, ["urr", serverRequestParameters])

            #Finalizado o loop, verifica o status da direcao novamente
            #Se ainda estiver normal, a operacao foi bem-sucedida, o que quer dizer que a rota atual do veiculo sera limpa, sera e registrada a nova
            if (noNegativeResponse == True):
                
                response = "OK"

                #Nome do arquivo do veiculo
                vehicleFileName = (vehicleID + ".json")
                
                fileLock.acquire()

                #Le o arquivo do veiculo com o ID especificado
                vehicleInfo = readFile(["clientdata", "clients", "vehicles", vehicleFileName])
                
                #Le as informacoes de rota e copia
                lastRoute = vehicleInfo["last_route"]
                oldLastRoute = lastRoute.copy()

                #Registra a nova rota e o tempo atual como de reserva
                vehicleInfo["last_route"] = chosenRoute
                vehicleInfo["last_routed_at"] = int(time.time())

                #Salva as novas informacoes
                writeFile(["clientdata", "clients", "vehicles", vehicleFileName], vehicleInfo)
                
                fileLock.release()

                for lastRouteNodeIndex in range (0, len(oldLastRoute)):

                    #Informacoes do no atual
                    lastRouteNodeAddress, _ = oldLastRoute[lastRouteNodeIndex]

                    #Parametros da requisicao a ser enviada ao servidor do no atual (ID do veiculo)
                    serverRequestParameters = [vehicleID]
                    
                    #Manda a mensagem solicitando remocao de reserva de um ponto naquele servidor
                    sendServerMessage(lastRouteNodeAddress, ["urr", serverRequestParameters])

    except:
        pass

    #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
    registerRequestResult(fileLock, vehicleAddress, vehicleRequestID, response)

    #Separa a string do endereco IP do veiculo
    vehicleAddressString, _ = vehicleAddress

    #Registra no log
    registerLogEntry(["logs", "performed"], "RESROUTE", "V_ADD", vehicleAddressString)

    #Responde o status da requisicao para o cliente
    sendResponse(senderLock, broker, port, serverAddress, vehicleAddress, response)


#Funcao para reservar um ponto de recarga
def doReservation(fileLock: threading.Lock, serverAddress, timeWindow, requestParameters):
    
    vehicleID = requestParameters[0]
    reservationTime = requestParameters[1]
    vehicleAutonomy = requestParameters[4]
    coordX = requestParameters[2]
    coordY = requestParameters[3]

    fileLock.acquire()

    #Adquire uma lista com o nome dos arquivos de todas as estacoes
    stationList = listFiles(["clientdata", "clients", "stations"])

    stationID = ""
    coordList = []

    #Loop que percorre a lista de estacoes de carga
    for stationIndex in range(0, len(stationList)):
        
        #Nome 
        actualStationFileName = stationList[stationIndex]

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
                vehicleID = requestParameters[3]
                
                #Obtem o tempo atual, para verificar informacao de agendamento
                actualTime = int(time.time())

                #Verifica se a ultima vez online foi a menos de 2 minutos e 15 segundos
                if((actualTime - (float(actualStationTable["last_online"]))) < 135):

                    #Esta online
                    isOnline = True

                #Loop para percorrer a o dicionario de veiculos agendandos
                for actualBookedVehicleID in actualStationTable["vehicle_bookings"]:
                    
                    #Tempo atual agendado para a entrada na lista (chave=id do veiculo)
                    bookedTime = actualStationTable["vehicle_bookings"][actualBookedVehicleID]

                    #Se a entrada na agenda nao for do veiculo solicitante e a janela de tempo do agendamento (2 horas antes e depois do horario exato marcado) contemplar o tempo atual, nao podera haver recarga
                    if ((zeroBookingConflicts == True) and (vehicleID != actualBookedVehicleID and (actualTime > (bookedTime - timeWindow))) and (actualTime < (bookedTime + timeWindow))):
                        
                        zeroBookingConflicts = False
                
                #Se a autonomia do veiculo cobrir o trecho (distancia menor que 80% da autonomia), a estacao estiver disponivel e se estivermos no primeiro indice da lista ou se a nova menor distancia for menor que a ultima
                if ((actualDistance < ((float(vehicleAutonomy)) * 0.8)) and (isOnline == True) and (zeroBookingConflicts == True) and (actualStationTable["actual_vehicle"] == "") and ((stationIndex == 0) or (actualDistance < actualShortestDistance))):
                    
                    #Atualiza os valores a serem repassados (achou distancia menor)
                    actualShortestDistance = actualDistance
                    stationID = actualID
                    coordList = []
                    coordList.append(actualStationTable["coord_x"])
                    coordList.append(actualStationTable["coord_y"])
            except:
                pass
    
    fileLock.release()

    #Nome do arquivo do veiculo a ser analizado
    vehicleFileName = (vehicleID + ".json")
    #Nome do arquivo da estacao de carga a ser analizado
    stationFileName = (stationID + ".json")

    vehicleVerify = False
    zeroBookingConflicts = False

    if (len(stationID) == 24):
        
        #Zona de exclusao mutua referente a manipulacao de arquivos
        fileLock.acquire()
        vehicleVerify = verifyFile(["clientdata", "clients", "vehicles"], vehicleFileName)
        fileLock.release()

    #Obtem o tempo atual, para verificar se o agendamento sequer e valido
    actualTime = int(time.time())

    #Caso o ID do veiculo/estacao fornecidos sejam validos
    if ((vehicleVerify == True) and (len(vehicleID) == 24) and (reservationTime > actualTime)):

        zeroBookingConflicts = True

        fileLock.acquire()

        #Carrega o dicionario de informacoes da estacao a ser agendada
        stationInfo = readFile(["clientdata", "clients", "stations", stationFileName])

        for actualBookedVehicleID in stationInfo["vehicle_bookings"]:
            
            #Tempo atual agendado para a entrada na lista (chave=id do veiculo)
            bookedTime = stationInfo["vehicle_bookings"][actualBookedVehicleID]

            #Se a entrada na agenda nao for do veiculo solicitante e a janela de tempo do agendamento (2 horas antes e depois do horario exato marcado) contemplar o tempo atual, nao podera haver recarga
            if ((zeroBookingConflicts == True) and (vehicleID != actualBookedVehicleID) and (reservationTime > (bookedTime - timeWindow)) and (reservationTime < (bookedTime + timeWindow))):
                
                zeroBookingConflicts = False

        #Se nao existem conflitos, a reserva pode ser feita
        if (zeroBookingConflicts == True):

            stationInfo["vehicle_bookings"][vehicleID] = reservationTime

            writeFile(["clientdata", "clients", "stations", stationFileName], stationInfo)

        fileLock.release()
    
    #Manda a mensagem de resposta da solicitacao de reserva (lista com coordenadas do ponto reservado, caso seja possivel, ou uma lista vazia, caso nao seja)
    sendServerMessage(serverAddress, coordList)

    return zeroBookingConflicts

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

        #Carrega as informacoes da estacao atual
        actualStationTable = readFile(["clientdata", "clients", "stations", actualStationFileName])

        try:
            #Tenta remover a entrada com o ID do veiculo solicitante da lista de agendamento, pois o mesmo acabou de iniciar o processo de recarga
            del actualStationTable["vehicle_bookings"][vehicleID]

            #Grava o resultado da acao
            writeFile(["clientdata", "clients", "stations", actualStationFileName], actualStationTable)
        except:
            pass

    fileLock.release()

    return True