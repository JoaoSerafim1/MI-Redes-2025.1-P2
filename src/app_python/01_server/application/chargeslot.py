###########################################################
#
# => MODULO DE GERENCIAMENTO DO PROCESSO DE RECARGA <=
#
###########################################################


#Importa bibliotecas basicas do python 3
import threading
import time

#Importa as bibliotecas customizadas da aplicacao
from application.lib.mf import *
from application.lib.pr import *

#Importa os modulos da aplicacao
from application.mqtt import *


#Funcao para retornar a distancia ate o posto de recarga disponivel mais proximo e seu ID
def getNearestAvailableStationInfo(fileLock: threading.Lock, senderLock: threading.Lock, broker, port, serverIP, timeWindow, requestID, vehicleAddress, requestParameters):

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

        if ((len(actualStationFileName) == 29)):

            actualID = ""
            
            #Acha o ID da estacao a retornar
            for IDIndex in range(0, 24):
                    
                actualID += actualStationFileName[IDIndex]

            #Carrega as informacoes da estacao atual
            actualStationTable = readFile(["clientdata", "clients", "stations", actualStationFileName])

            try:
                #Calcula a distancia
                actualDistance = getDistance(float(requestParameters[0]), float(requestParameters[1]), float(actualStationTable["coord_x"]), float(actualStationTable["coord_y"]))

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
                
                #print("+++++++++++++++++++++++++++++++++++++++")
                #print(str(actualDistance))
                #print(str(requestParameters[2]))
                #print(str(isOnline))
                #print(str(zeroBookingConflicts))
                #print(str(actualStationTable["actual_vehicle"]))
                #print("+++++++++++++++++++++++++++++++++++++++")
                
                #Se a autonomia do veiculo cobrir o trecho (distancia menor que 80% da autonomia), a estacao estiver disponivel e se estivermos no primeiro indice da lista ou se a nova menor distancia for menor que a ultima
                if ((actualDistance < ((float(requestParameters[2])) * 0.8)) and (isOnline == True) and (zeroBookingConflicts == True) and (actualStationTable["actual_vehicle"] == "") and ((IDToReturn == "0") or (actualDistance < distanceToReturn))):
                    
                    #Atualiza os valores a serem retornados (achou distancia menor)
                    distanceToReturn = actualDistance
                    unitaryPriceToReturn = actualStationTable["unitary_price"]
                    IDToReturn = actualID
            except:
                pass
    
    fileLock.release()

    #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
    registerRequestResult(fileLock, vehicleAddress, requestID, [IDToReturn, str(distanceToReturn), unitaryPriceToReturn])

    #Separa a string do endereco IP do veiculo
    vehicleAddressString, _ = vehicleAddress

    #Registra no log
    registerLogEntry(fileLock, ["logs", "performed"], "GETDISTANCE", "V_ADD", vehicleAddressString)

    #Responde o status da requisicao para o cliente
    sendResponse(senderLock, broker, port, serverIP, vehicleAddress, [IDToReturn, str(distanceToReturn), unitaryPriceToReturn])

#Funcao para tentar realizar (reserva de) abastecimento
def attemptCharge(fileLock: threading.Lock, senderLock: threading.Lock, broker, port, serverIP, timeWindow, requestID, vehicleAddress, requestParameters):

    #Caso os parametros da requisicao sejam adequados
    try:
        
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

        fileLock.acquire()
        stationVerify = verifyFile(["clientdata", "clients", "stations"], stationFileName)
        fileLock.release()

        #Caso o ID do veiculo/estacao fornecidos sejam validos e a compra seja confirmada
        if ((stationVerify == True) and (len(stationID) == 24) and (len(vehicleID) == 24) and confirmPurchase(purchaseID) == True):
            
            zeroBookingConflicts = True
            purchaseDone = False

            fileLock.acquire()

            #Obtem o tempo atual, para verificar informacao de agendamento
            actualTime = int(time.time())

            try:
                #Carrega o dicionario de informacoes da estacao a ser agendada
                stationInfo = readFile(["clientdata", "clients", "stations", stationFileName])

                for actualBookedVehicleID in stationInfo["vehicle_bookings"]:
                    
                    #Tempo atual agendado para a entrada na lista (chave=id do veiculo)
                    bookedTime = stationInfo["vehicle_bookings"][actualBookedVehicleID]

                    #Se a entrada na agenda nao for do veiculo solicitante e a janela de tempo do agendamento (2 horas antes e depois do horario exato marcado) contemplar o tempo atual, nao podera haver recarga
                    if ((zeroBookingConflicts == True) and (vehicleID != actualBookedVehicleID and (actualTime > (bookedTime - timeWindow))) and (actualTime < (bookedTime + timeWindow))):
                        
                        zeroBookingConflicts = False

                #Caso o ponto de carga esteja disponivel para a operacao (nenhum veiculo recarregando e a janela de agendamento esta livre)
                if ((stationInfo["actual_vehicle"] == "") and (zeroBookingConflicts == True)):

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

                    vehicleInfo = {}

                    #Carrega o dicionario de informacoes do veiculo, se possivel
                    if (verifyFile(["clientdata", "clients", "vehicles"], vehicleFileName) == True):
                        
                        vehicleInfo = readFile(["clientdata", "clients", "vehicles", vehicleFileName])
                    
                    else:

                        vehicleInfo["purchases"] = []

                    #Adiciona a compra a lista de compras do veiculo (cliente) e grava o resultado
                    vehicleInfo["purchases"].append(purchaseID)

                    #Modifica o veiculo atual na estacao de carga e grava o resultado
                    stationInfo["actual_vehicle"] = vehicleID
                    stationInfo["remaining_charge"] = chargeAmount

                    #Grava o resultado das acoes
                    writeFile(["clientdata", "purchases", purchaseFileName], purchaseTable)
                    writeFile(["clientdata", "clients", "vehicles", vehicleFileName], vehicleInfo)
                    writeFile(["clientdata", "clients", "stations", stationFileName], stationInfo)

                    #Adquire uma lista com o nome dos arquivos de todas as estacoes
                    stationList = listFiles(["clientdata", "clients", "stations"])
                    
                    #Loop que percorre a lista de estacoes de carga
                    for stationIndex in range(0, len(stationList)):
                        
                        #Nome do arquivo
                        actualStationFileName = stationList[stationIndex]
                        
                        try:

                            #Carrega as informacoes da estacao atual (falha caso o arquivo nao seja valido para carregar)
                            actualStationTable = readFile(["clientdata", "clients", "stations", actualStationFileName])
                            
                            try:
                                
                                #Tenta remover a entrada com o ID do veiculo solicitante da lista de agendamento, pois o mesmo acabou de iniciar o processo de recarga
                                del actualStationTable["vehicle_bookings"][vehicleID]
                                
                                #Grava o resultado da acao
                                writeFile(["clientdata", "clients", "stations", actualStationFileName], actualStationTable)
                                
                            except:
                                pass
                        except:
                            pass

                    #Marca a compra como feita
                    purchaseDone = True
            except:
                pass

            fileLock.release()
            
            #Caso a compra seja feita
            if (purchaseDone == True):
                
                #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
                registerRequestResult(fileLock, vehicleAddress, requestID, 'OK')
                
                #Registra no log
                registerLogEntry(fileLock, ["logs", "performed"], "PHCCHARGE", "P_ID", purchaseID)
                
                #Envia mensagem de resposta ao veiculo
                sendResponse(senderLock, broker, port, serverIP, vehicleAddress, 'OK')
                
            else:
                
                #Caso contrario (slot de carga ocupado durante a compra), cancela a compra
                cancelPurchase(purchaseID)

                #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
                registerRequestResult(fileLock, vehicleAddress, requestID, 'ERR')

                #Envia mensagem de resposta ao veiculo
                sendResponse(senderLock, broker, port, serverIP, vehicleAddress, 'ERR')

        else:

            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            registerRequestResult(fileLock, vehicleAddress, requestID, 'ERR')

            #Responde o status da requisicao para o cliente
            sendResponse(senderLock, broker, port, serverIP, vehicleAddress, 'ERR')

    except:

        #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
        registerRequestResult(fileLock, vehicleAddress, requestID, 'ERR')

        #Responde o status da requisicao para o cliente
        sendResponse(senderLock, broker, port, serverIP, vehicleAddress, 'ERR')

#Funcao para liberar estacao de carga
def freeChargingStation(fileLock: threading.Lock, senderLock: threading.Lock, broker, port, serverIP, requestID, stationAddress, requestParameters):

    #Caso os parametros da requisicao sejam do tamanho adequado
    try:

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
            registerRequestResult(fileLock, stationAddress, requestID, 'OK')

            #Registra no log
            registerLogEntry(fileLock, ["logs", "performed"], "FREESPOT", "S_ID", stationID)
            
            #Responde o status da requisicao para o cliente
            sendResponse(senderLock, broker, port, serverIP, stationAddress, 'OK')
            
        else:
            
            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            registerRequestResult(fileLock, stationAddress, requestID, 'NF')
            
            #Responde o status da requisicao para o cliente
            sendResponse(senderLock, broker, port, serverIP, stationAddress, 'NF')
            
    except:
        pass