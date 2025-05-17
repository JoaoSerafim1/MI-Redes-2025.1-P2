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
from application.rest import *
from application.clientmanager import *
from application.chargeslot import *
from application.chargeroute import *


#Locks para uso dos sockets
senderLock = threading.Lock()
receiverLock = threading.Lock()

#Lock para modificacao da variavel randomID
randomIDLock = threading.Lock()

#Listas de threads
threadList = []

#ID Aleatorio inicial
randomID = "*"

#Variavel de contagem de fechamentos dos threads de requisicoes de clientes
clientThreadCount = 1

#Variavel de contagem dos threads de requisicoes de outros servidores
serverThreadCount = 0

#Variavel de execucao do programa
isExecuting = True

#Instancia para passagem automatica de variavel de encerramento
isExecutingInstance = isExecutingClass()

#Funcao para cada thread que espera uma requisicao de um cliente
def clientRequestCatcher():

    #Globais utilizadas
    global isExecuting
    global clientThreadCount

    global fileLock
    global randomIDLock
    global randomID
    global receiverLock
    global senderLock
    global broker
    global mqttPort
    global localServerIP

    global timeWindow

    #Loop da thread
    while (isExecuting == True):

        #Espera chegar uma requisicao
        clientAddress, requestInfo = listenToRequest(fileLock, receiverLock, isExecutingInstance, localServerIP, broker, mqttPort, 5)

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
                    
                    randomIDLock.acquire()

                    randomID = registerChargeStation(randomID, senderLock, broker, mqttPort, localServerIP, requestID, clientAddress, requestParameters)

                    randomIDLock.release()

                elif (requestName == 'rve'):

                    registerVehicle(fileLock, randomIDLock, randomID, senderLock, broker, mqttPort, localServerIP, requestID, clientAddress)

                elif (requestName == 'gbv'):

                    getBookedVehicle(fileLock, senderLock, broker, mqttPort, localServerIP, requestID, clientAddress, requestParameters)
                
                elif (requestName == 'nsr'):

                    getNearestAvailableStationInfo(fileLock, senderLock, broker, mqttPort, localServerIP, timeWindow, requestID, clientAddress, requestParameters)

                elif (requestName == 'bcs'):
                    
                    attemptCharge(fileLock, senderLock, broker, mqttPort, localServerIP, timeWindow, requestID, clientAddress, requestParameters)
                    
                elif (requestName == 'fcs'):

                    freeChargingStation(fileLock, senderLock, broker, mqttPort, localServerIP, requestID, clientAddress, requestParameters)
                
                elif(requestName == 'gpr'):

                    respondWithPurchase(fileLock, senderLock, broker, mqttPort, localServerIP, requestID, clientAddress, requestParameters)
                
                elif(requestName == 'rwr'):

                    respondWithRoute(fileLock, senderLock, broker, mqttPort, localServerIP, requestID, clientAddress, requestParameters)
                
                elif(requestName == 'rrt'):

                    reserveRoute(fileLock, senderLock, broker, mqttPort, localServerIP, requestID, clientAddress, requestParameters)
            
            #Caso contrario, manda a resposta novamente
            else:

                sendResponse(senderLock, broker, mqttPort, localServerIP, clientAddress, requestResult)

        #Caso contrario e se o endereco do cliente nao for vazio
        elif clientAddressString != "":
            
            #Responde que a requisicao e invalida
            sendResponse(senderLock, broker, mqttPort, localServerIP, clientAddress, 'ERR')
    
    print("THREAD ENCERRADO (" + str(clientThreadCount) + "/" + str(maxClientThreads) + ")")
    clientThreadCount += 1

#Funcao para receber UMA requisicao de outro servidor
def serverRequestCatcher():

    global httpHandlerLock
    global serverThreadCount
    global localServerIP
    global httpPort

    #Endereco do servidor (tupla com IP e porta)
    server_address = (localServerIP, httpPort)
    
    #Objeto de servidor HTTP-REST
    httpd = CustomHTTPServer(server_address, RequestHandler)
    
    httpd.handle_request()

    #Diminui a contagem de threads ativos
    httpHandlerLock.acquire()
    serverThreadCount -= 1
    httpHandlerLock.release()
    

#Funcao apra gerenciar as threads de requisicoes HTTP
def serverRequestHandlerThreadManager():

    global serverThreadCount
    global maxServerThreads
    global isInNeedOfHTTPHandler
    global httpHandlerLock
    global threadList

    while (isExecuting == True):

        #Variavel que diz se deve ser criado novo thread
        createNewThread = False

        httpHandlerLock.acquire()

        #O novo thread sera criado caso o limite nao esteja estourado e seja requisitado OU caso nao existam threads ativos
        if (((serverThreadCount < maxServerThreads) and (isInNeedOfHTTPHandler == True)) or serverThreadCount == 0):
            createNewThread = True
            isInNeedOfHTTPHandler = False

        httpHandlerLock.release()

        if(createNewThread == True):

            #Aumenta a contagem de threads ativos
            httpHandlerLock.acquire()
            serverThreadCount += 1
            httpHandlerLock.release()

            #Cria o thread, inicia, adiciona para a lista e aumenta o contador
            newThread = threading.Thread(target=serverRequestCatcher, args=())
            newThread.start()
            threadList.append(newThread)

def end(isExecutingInstance: isExecutingClass):

    global isExecuting

    print("AGUARDE O ENCERRAMENTO:")

    isExecuting = False
    isExecutingInstance.isExecutingVariable = False

    while (clientThreadCount <= maxClientThreads):
        pass

    print("ESPERANDO REQUISICAO QUALQUER PARA ENCERRAR OUVINTE DE REQUISICAO HTTP ATIVO")


#Inicio do programa

#IP do servidor, porta do broker MQTT e porta para requisicoes HTTP
localServerIP = socket.gethostbyname(socket.gethostname())

#Pergunta endereco do broker MQTT
broker = input("Insira o endereço IP do broker MQTT (OU PRESSIONE ENTER para utilizar o endereço do proprio servidor): ")

if (broker == ""):
    broker = localServerIP

elif (broker == "test"):
    broker = testBroker
    

#Printa o endereco IP do servidor
print("ENDERECO IP DO SERVIDOR: " + localServerIP)

#Obtem um ID aleatorio de 24 elementos alfanumericos e exibe mensagem da operacao
randomID = getRandomID(fileLock, randomID)
print("ID para o proximo cadastro de estacao de carga: " + randomID)

#Exibe mensagem que diz como sair da aplicacao
print("PRESSIONE ENTER A QUALQUER MOMENTO PARA ENCERRAR A APLICACAO")

#Loop para indexar todos os threads dos clientes
for threadIndex in range(0, maxClientThreads):

    #Cria o thread, inicia e adiciona para a lista
    newThread = threading.Thread(target=clientRequestCatcher, args=())
    newThread.start()
    threadList.append(newThread)

#Thread de gerenciamento dos subthreads de requisicoes HTTP
httpManagerThread = threading.Thread(target=serverRequestHandlerThreadManager, args=())
httpManagerThread.start()
threadList.append(httpManagerThread)

#Fora dos threads, input() apenas segura a execucao do programa principal ate ser pressionado
input()

#Encerra o programa
end(isExecutingInstance)