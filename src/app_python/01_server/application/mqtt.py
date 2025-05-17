###########################################################
#
# => MODULO DE COMUNICACAO VIA PROTOCOLO MQTT <=
#
###########################################################


#Importa bibliotecas basicas do python 3
import threading
import time
import json

#Importa os componentes utilizados da biblioteca Paho MQTT
from paho.mqtt import client as mqtt_client

#Importa os modulos da aplicacao
from application.util import *


#Classe para passagem de variavel de execucao do programa
class isExecutingClass():

    #Funcao inicializadora da classe
    def __init__(self):
        
        #Atributos
        self.isExecutingVariable = True


#Funcao para receber uma requisicao de um cliente (protocolo MQTT)
def listenToRequest(fileLock: threading.Lock, receiverLock: threading.Lock, isExecutingInstance: isExecutingClass, serverIP, broker, port, timeout):
    
    topic = ("req9a3fd59-" + str(serverIP))

    add = ("", 0)
    content = ""

    mqttClientReceiver = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    
    setattr(mqttClientReceiver, "decodedBytes", "")

    #Funcao que determina o que acontece quando uma mensagem e recebida em um topico assinado
    def on_message(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
        setattr(client, "decodedBytes", msg.payload.decode())
        
        #print("=============================================")
        #print(topic)
        #print(mqttClientReceiver.decodedBytes)
        #print("=============================================")
        
    mqttClientReceiver.on_message = on_message

    receiverLock.acquire()

    try:
        #Conecta ao broker com os parametros desejados, assina o topico e entra no loop para esperar mensagem(s)
        mqttClientReceiver.connect(broker, port)
        mqttClientReceiver.subscribe(topic)
        mqttClientReceiver.loop_start()

        start_time = time.time()

        while (((time.time() - start_time) < timeout) and (mqttClientReceiver.decodedBytes == "") and (isExecutingInstance.isExecutingVariable == True)):
            pass
            
        mqttClientReceiver.loop_stop()
        mqttClientReceiver.unsubscribe(topic)
        mqttClientReceiver.disconnect()

    except:
        pass

    receiverLock.release()
    
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
                registerLogEntry(fileLock, ["logs", "received"], "RVMQTT", "ADDRESS", addressString)
    except:
        pass
    
    #Retorna o objeto da mensagem
    return (add, content)

#Funcao para enviar uma resposta de volta ao cliente (protocolo MQTT)
def sendResponse(senderLock: threading.Lock, broker, port, serverIP, clientAddress, response):

    #Obtem a string do endereco do cliente
    clientAddressString, _ = clientAddress
    topic = ("res9a3fd59-" + str(clientAddressString))
    
    mqttMessage = [serverIP, port, response]

    #print("--------------------------------------------")
    #print(topic)
    #print(mqttMessage)
    #print("--------------------------------------------")
    
    senderLock.acquire()

    try:
        #Serializa a resposta utilizando json
        serializedRequest = json.dumps(mqttMessage)

        mqttClientSender = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
        
        mqttClientSender.connect(broker, port)
        mqttClientSender.loop_start()

        mqttClientSender.publish(topic, serializedRequest)
        
        mqttClientSender.loop_stop()
        mqttClientSender.disconnect()

        
    except:
        pass

    senderLock.release()