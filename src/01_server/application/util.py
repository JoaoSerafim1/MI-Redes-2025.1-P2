###########################################################
#
# => MODULO DE FUNCIONALIDADES BASICAS DO SERVIDOR <=
#
###########################################################


#Importa bibliotecas basicas do python 3
import threading
import datetime
import string
import random

#Importa as bibliotecas customizadas da aplicacao
from application.lib.db import *

fileLock = threading.Lock()


#Funcao para obter um novo ID aleatorio
def getRandomID(fileLock: threading.Lock, randomID):

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

#Funcao para fazer entrada de requisicao processada
def registerRequestResult(fileLock: threading.Lock, clientAddress, requestID, requestResult):

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
def registerLogEntry(fileLock: threading.Lock, fileDir, entryLabel, logRequesterLabel, requester):
    
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