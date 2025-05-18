import time
import socket
import json
import uuid

from paho.mqtt import client as mqtt_client

client_ip = str(socket.gethostbyname(socket.gethostname()))
mqttClientSender = mqtt_client.Client(client_id=(client_ip + str(uuid.uuid4())), callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

#Funcao para enviar uma requisicao ao servidor
def sendResponse(clientAddress, request):

    global mqttClientSender
    global client_ip

    #Obtem a string do endereco do cliente
    clientAddressString, _ = clientAddress

    broker = input("Insira o IP do broker MQTT: ")
    port = 1883
    topic = 'request'
    
    mqttMessage = [client_ip, port, request]

    #print("--------------------------------------------")
    #print(clientAddressString)
    #print(mqttMessage)
    #print("--------------------------------------------")
    
    try:
        #Serializa a resposta utilizando json
        serializedRequest = json.dumps(mqttMessage)

        mqttClientSender.connect(broker, port)
        mqttClientSender.loop_start()
        mqttClientSender.publish(topic, serializedRequest)
        mqttClientSender.loop_stop()
    except Exception as ex:
        print(ex)


sendResponse(('broker.emqx.io', 4821), ["a", "b", "c"])