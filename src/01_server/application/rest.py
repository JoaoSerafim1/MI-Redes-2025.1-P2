###########################################################
#
# => MODULO DE COMUNICACAO VIA PROTOCOLO HTTP-REST <= (VERSAO DE TESTE QUE USA MQTT AO INVES DE REST)
#
###########################################################


#Importa bibliotecas basicas do python 3
import threading
import time
import json
import socket
import requests
#Importa os componentes utilizados da biblioteca Paho MQTT
from paho.mqtt import client as mqtt_client

#Importa os modulos da aplicacao
from application.util import *

testServerIP = socket.gethostbyname(socket.gethostname())
testBroker = 'testBroker.emqx.io'
testPort = 1883

serverReceiverLock = threading.Lock()
serverSenderLock = threading.Lock()

#Funcao para receber uma requisicao de um servidor-remetente (protocolo MQTT)
def httpRequest(fileLock: threading.Lock, destinyServerAddress, message, timeout):

    messageString = json.dumps(message)
    
    request_url = "http://"+destinyServerAddress+':8000/Empresa1/sender/' 
    decodedBytes = requests.post(request_url, data=messageString,timeout=timeout)
    decodedBytes = decodedBytes.json()
    

    print("=============================================")
    print(decodedBytes)
    print("=============================================")
    
    try:
        #Caso a mensagem nao seja vazia
        if (decodedBytes != ""):
            
            #De-serializa a mensagem decodificada 
            content = json.loads(decodedBytes)
    except:
        pass
    
    #Retorna o objeto da mensagem
    return content

