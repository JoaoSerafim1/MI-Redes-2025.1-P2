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
def listenToServerMessage(fileLock: threading.Lock, timeout):
    
    global serverReceiverLock

    global testServerIP
    global testBroker
    global testPort
    
    topic = testServerIP

    add = ("", 0)
    content = ""

    mqttClientReceiver = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    
    setattr(mqttClientReceiver, "decodedBytes", "")

    #Funcao que determina o que acontece quando uma mensagem e recebida em um topico assinado
    def on_message(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
        setattr(client, "decodedBytes", msg.payload.decode())
        
        #print("=============================================")
        #print(mqttClientReceiver.decodedBytes)
        #print("=============================================")
        
    mqttClientReceiver.on_message = on_message

    serverReceiverLock.acquire()

    try:
        #Conecta ao testBroker com os parametros desejados, assina o topico e entra no loop para esperar mensagem(s)
        mqttClientReceiver.connect(testBroker, testPort)
        mqttClientReceiver.subscribe(topic)
        mqttClientReceiver.loop_start()

        start_time = time.time()

        while (((time.time() - start_time) < timeout) and (mqttClientReceiver.decodedBytes == "")):
            pass
            
        mqttClientReceiver.loop_stop()
        mqttClientReceiver.unsubscribe(topic)
        mqttClientReceiver.disconnect()

    except:
        pass

    serverReceiverLock.release()
    
    try:
        #Caso a mensagem nao seja vazia
        if (mqttClientReceiver.decodedBytes != ""):
            
            #De-serializa a mensagem decodificada 
            unserializedObj = json.loads(mqttClientReceiver.decodedBytes)

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