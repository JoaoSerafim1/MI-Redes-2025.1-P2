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

    decodedBytes = ""



    #print("=============================================")
    #print(mqttClientReceiver.decodedBytes)
    #print("=============================================")
    
    try:
        #Caso a mensagem nao seja vazia
        if (decodedBytes != ""):
            
            #De-serializa a mensagem decodificada 
            unserializedObj = json.loads(decodedBytes)

            #Se uma resposta valida foi recebida, a mensagem deve ter tamanho 3
            if (len(unserializedObj) == 3):

                #Separa a parte do endereco referente ao endereco IP
                add = (unserializedObj[0], unserializedObj[1])
                content = unserializedObj[2]

                #Separa a parte do endereco referente ao endereco IP
                addressString, _ = add

                #Registra no log
                registerLogEntry(fileLock, ["logs", "received"], "RVMSG", "ADDRESS", addressString)
    except:
        pass
    
    #Retorna o objeto da mensagem
    return (add, content)

#Funcao para enviar uma resposta de volta ao servidor-remetente (protocolo MQTT)
def sendServerMessage(destinyServerAddress, message):

    global serverSenderLock

    #Obtem a string do endereco do cliente
    topic = destinyServerAddress
    
    mqttMessage = [testServerIP, testPort, message]

    #print("--------------------------------------------")
    #print(topic)
    #print(mqttMessage)
    #print("--------------------------------------------")
    
    serverSenderLock.acquire()

    try:
        #Serializa a resposta utilizando json
        serializedRequest = json.dumps(mqttMessage)

        mqttClientSender = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
        
        mqttClientSender.connect(testBroker, testPort)
        mqttClientSender.loop_start()

        mqttClientSender.publish(topic, serializedRequest)
        
        mqttClientSender.loop_stop()
        mqttClientSender.disconnect()

        
    except:
        pass

    serverSenderLock.release()