import time
import socket
import json
import uuid

from paho.mqtt import client as mqtt_client

client_ip = str(socket.gethostbyname(socket.gethostname()))
mqttClientReceiver = mqtt_client.Client(client_id=(client_ip + str(uuid.uuid4())), callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

decodedBytes = ""

#Funcao para receber uma requisicao
def listenToRequest(timeout):
    
    global mqttClientReceiver
    global decodedBytes

    broker = client_ip
    port = 1883
    topic = "request"

    decodedBytes = ""
    add = ("", 0)
    content = ""

    #Funcao que determina o que acontece quando uma mensagem e recebida em um topico assinado
    def on_message(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
        
        global decodedBytes

        decodedBytes = msg.payload.decode()
        
    mqttClientReceiver.on_message = on_message
    try:
        #Conecta ao broker com os parametros desejados, assina o topico e entra no loop para esperar mensagem(s)
        mqttClientReceiver.connect(broker, port)
        mqttClientReceiver.subscribe(topic)
        mqttClientReceiver.loop_start()
    except Exception as ex:
        print(ex)

    start_time = time.time()

    while (((time.time() - start_time) < timeout) and (decodedBytes == "")):
        time.sleep(0.1)

    mqttClientReceiver.loop_stop()

    #print("=============================================")
    #print(decodedBytes)
    #print("=============================================")
    
    try:
        #De-serializa a mensagem decodificada 
        unserializedObj = json.loads(decodedBytes)

        #Se uma resposta valida foi recebida, a mensagem deve ter tamanho 3
        if (len(unserializedObj) == 3):

            #Separa a parte do endereco referente ao endereco IP
            add = (unserializedObj[0], unserializedObj[1])
            content = unserializedObj[2]
    except Exception as ex:
        print(ex)

    print(add)
    print(content)


listenToRequest(10)