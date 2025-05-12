###########################################################
#
# => ARQUIVO PRINCIPAL DA APLICACAO (EXECUTAVEL) <=
#
###########################################################


#Importa bibliotecas basicas do python 3
import socket
import threading

#Importa os modulos da aplicacao
from application.util import *
from application.mqtt import *
from application.clientmanager import *
from application.chargeslot import *
from application.chargeroute import *


#PROPRIEDADES DO SERVIDOR
####################################################################################

#Maximo de threads simultaneos para clientes (estacoes, veiculos)
maxClientThreads = 8

#IP do servidor, IP do broker MQTT e porta do broker MQTT
serverIP = socket.gethostbyname(socket.gethostname())
broker = 'broker.emqx.io'
port = 1883

#Tempo em segundos antes e depois do horario exato marcado durante o qual um posto de recarga sera considerado como "ocupado"
timeWindow = 7200

####################################################################################


#Lock para manipulacao de arquivos (tambem controla requisicoes pois todo o processo e baseado em leitura e escrita de arquivos)
fileLock = threading.Lock()

#Locks para uso dos sockets
senderSocketLock = threading.Lock()
receiverSocketLock = threading.Lock()

#Lock para modificacao da variavel randomID
randomIDLock = threading.Lock()

#Lista de threads
threadList = []

#ID Aleatorio inicial
randomID = "*"

#Variavel de execucao do programa
isExecuting = True

#Variavel de contagem de fechamentos dos threads
threadCount = 1


#Funcao para cada thread que espera uma requisicao de um cliente
def clientRequestCatcher():

    #Globais utilizadas
    global isExecuting
    global threadCount

    global fileLock
    global randomIDLock
    global randomID
    global receiverLock
    global senderLock
    global broker
    global port
    global serverIP

    global timeWindow

    #Loop da thread
    while (isExecuting == True):

        #Espera chegar uma requisicao
        clientAddress, requestInfo = listenToRequest(fileLock, receiverLock, broker, port, 5)

        #Obtem a string de endereco do cliente
        clientAddressString, _ = clientAddress

        #Se o tamamanho da lista de requisicao for adequado
        if (len(requestInfo) >= 3):
            
            #Recupera as informacoes da lista de requisicao
            requestID = requestInfo[0]
            requestName = requestInfo[1]
            requestParameters = requestInfo[2]

            #Obtem a string de endereco do cliente
            clientAddressString, _ = clientAddress

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
                    
                    randomIDLock.acquire()

                    randomID = registerChargeStation(fileLock, randomID, senderLock, broker, port, serverIP, requestID, clientAddress, requestParameters)

                    randomIDLock.release()

                elif (requestName == 'rve'):

                    registerVehicle(fileLock, randomIDLock, randomID, senderLock, broker, port, serverIP, requestID, clientAddress)

                elif (requestName == 'gbv'):

                    getBookedVehicle(fileLock, senderLock, broker, port, serverIP, requestID, clientAddress, requestParameters)
                
                elif (requestName == 'nsr'):

                    getNearestAvailableStationInfo(fileLock, senderLock, broker, port, serverIP, timeWindow, requestID, clientAddress, requestParameters)

                elif (requestName == 'bcs'):
                    
                    attemptCharge(fileLock, senderLock, broker, port, serverIP, timeWindow, requestID, clientAddress, requestParameters)
                    
                elif (requestName == 'fcs'):

                    freeChargingStation(fileLock, senderLock, broker, port, serverIP, requestID, clientAddress, requestParameters)
                
                elif(requestName == 'gpr'):

                    respondWithPurchase(fileLock, senderLock, broker, port, serverIP, requestID, clientAddress, requestParameters)
            
            #Caso contrario, manda a resposta novamente
            else:

                sendResponse(senderLock, broker, port, serverIP, clientAddress, requestResult)

        #Caso contrario e se o endereco do cliente nao for vazio
        elif clientAddress != "":
            
            #Responde que a requisicao e invalida
            sendResponse(senderLock, broker, port, serverIP, clientAddress, 'ERR')
    
    print("THREAD ENCERRADO (" + str(threadCount) + "/" + str(maxClientThreads) + ")")
    threadCount += 1


#Inicio do programa

#Obtem e printa o endereco IP do servidor
hostAddress = socket.gethostbyname(socket.gethostname())
print("ENDERECO IP DO SERVIDOR: " + hostAddress)

#Obtem um ID aleatorio de 24 elementos alfanumericos e exibe mensagem da operacao
randomID = getRandomID(fileLock, randomID)
print("ID para o proximo cadastro de estacao de carga: " + randomID)

#Exibe mensagem que diz como sair da aplicacao
print("PRESSIONE ENTER A QUALQUER MOMENTO PARA ENCERRAR A APLICACAO")

#Loop para indexar todos os threads
for threadIndex in range(0, maxClientThreads):

    #Cria o thread, inicia e adiciona para a lista
    newThread = threading.Thread(target=clientRequestCatcher, args=())
    newThread.start()
    threadList.append(newThread)

#Fora dos threads, input() apenas segura a execucao do programa principal ate ser pressionado
input()
#Encerra o programa
print("AGUARDE O ENCERRAMENTO:")
isExecuting = False