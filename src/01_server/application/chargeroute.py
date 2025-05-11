###########################################################
#
# => MODULO DE GERENCIAMENTO DE LEITURA DE ROTAS E RESERVA DE INTINERARIOS <=
#
###########################################################


#Importa bibliotecas basicas do python 3
import threading
import time

#Importa os modulos da aplicacao
from application.mqtt import *


def reserveRoute():
    pass

#Funcao para retornar informacoes de uma rota em especifico
def respondWithRoute(fileLock: threading.Lock, senderLock, broker, port, serverIP, requestID, vehicleAddress, requestParameters):

    #Informacoes iniciais da mensagem de resposta
    serverRouteIndex = (-1)
    routeNodeNameList = []

    #Se estiver no formato adequado
    if(len(requestParameters) >= 2):
        
        routeIndex = requestParameters[0]
        routeStartIP = requestParameters[1]
        routeEndIP = requestParameters[2]

        #Se existe veiculo valido no ID e o indice e numerico
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

                actualRouteStartIP, _ = actualRouteStartNode
                actualRouteEndIP, _ = actualRouteEndNode

                #Se a origem e o destino da rota correspondem ao desejado
                if ((routeStartIP == actualRouteStartIP) and (routeEndIP == actualRouteEndIP)):

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

    #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
    registerRequestResult(fileLock, vehicleAddress, requestID, [serverRouteIndex, routeNodeNameList])

    #Separa a string do endereco IP do veiculo
    vehicleAddressString, _ = vehicleAddress

    #Registra no log
    registerLogEntry(["logs", "performed"], "RTDETAILS", "V_ADD", vehicleAddressString)

    #Responde o status da requisicao para o cliente
    sendResponse(senderLock, broker, port, serverIP, vehicleAddress, [serverRouteIndex, routeNodeNameList])


#Funcao para reservar um ponto de recarga
def doReservation(fileLock, serverAddress, stationID, vehicleID, reservationTime):

    #Nome do arquivo do veiculo de carga a ser analizado
    vehicleFileName = (vehicleID + ".json")
    #Nome do arquivo da estacao de carga a ser analizado
    stationFileName = (stationID + ".json")

    stationVerify = False
    vehicleVerify = False
    zeroBookingConflicts = False

    fileLock.acquire()
    stationVerify = verifyFile(["clientdata", "clients", "stations"], stationFileName)
    fileLock.release()

    if ((stationVerify == True) and (len(stationID) == 24)):
        
        #Zona de exclusao mutua referente a manipulacao de arquivos
        fileLock.acquire()
        vehicleVerify = verifyFile(["clientdata", "clients", "vehicles"], vehicleFileName)
        fileLock.release()

    #Obtem o tempo atual, para verificar se o agendamento sequer e valido
    actualTime = int(time.time())

    #Caso o ID do veiculo/estacao fornecidos sejam validos
    if ((vehicleVerify == True) and (len(vehicleID) == 24) and (stationVerify == True) and (reservationTime > actualTime)):

        zeroBookingConflicts = True

        fileLock.acquire()

        #Carrega o dicionario de informacoes da estacao a ser agendada
        stationInfo = readFile(["clientdata", "clients", "stations", stationFileName])

        for actualBookedVehicleID in stationInfo["vehicle_bookings"]:
            
            #Tempo atual agendado para a entrada na lista (chave=id do veiculo)
            bookedTime = stationInfo["vehicle_bookings"][actualBookedVehicleID]

            #Se a entrada na agenda nao for do veiculo solicitante e a janela de tempo do agendamento (2 horas antes e depois do horario exato marcado) contemplar o tempo atual, nao podera haver recarga
            if ((zeroBookingConflicts == True) and (vehicleID != actualBookedVehicleID and (reservationTime > (bookedTime - 7200))) and (reservationTime < (bookedTime + 7200))):
                
                zeroBookingConflicts = False

        #Se nao existem conflitos, a reserva pode ser feita
        if (zeroBookingConflicts == True):

            stationInfo["vehicle_bookings"][vehicleID] = reservationTime

            writeFile(["clientdata", "clients", "stations", stationFileName], stationInfo)

        fileLock.release()

    #######################################################################################
    #INSIRA AQUI A RESPOSTA COM REFERENCIA A API REST PARA O SERVIDOR com IP na variavel "serverAddress"
    #######################################################################################

    return zeroBookingConflicts
    
def undoReservation(fileLock, serverAddress, vehicleID):
    
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

    #######################################################################################
    #INSIRA AQUI A RESPOSTA COM REFERENCIA A API REST PARA O SERVIDOR com IP na variavel "serverAddress"
    #######################################################################################

    return True