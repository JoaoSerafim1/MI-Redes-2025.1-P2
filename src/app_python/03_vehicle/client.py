#Importa bibliotecas basicas do python 3
import threading
import sys

#Importa as bibliotecas customizadas da aplicacao
from application.lib.io import *

#Importa modulos da aplicacao
from application.gui import *


#IP do broker MQTT de teste
vehicle.testBroker = 'broker.emqx.io'

#Cria um dicionario dos atributos do veiculo
dataTable = {}


#Verifica se o arquivo de texto "ID.txt" esta presente, e caso nao esteja...
if (verifyFile(["vehicledata"], "ID.txt") == False):
    
    #Pergunta o endereco do servidor
    vehicle.serverAddress = input("Insira o endereço IP do servidor: ")

    #Pergunta endereco do broker MQTT
    vehicle.brokerCandidate = input("Insira o endereço IP do broker MQTT (OU PRESSIONE ENTER para utilizar o endereço do servidor conectado): ")

    if (vehicle.brokerCandidate == ""):
        vehicle.broker = vehicle.serverAddress
    elif (vehicle.brokerCandidate == "test"):
        vehicle.broker = vehicle.testBroker
    else:
        vehicle.broker = vehicle.brokerCandidate

    #Cria um novo arquivo
    writeFile(["vehicledata", "ID.txt"], vehicle.registerVehicle())

#Caso contrario...
else:

    #Apenas pergunta endereco do broker MQTT
    vehicle.brokerCandidate = input("Insira o endereço IP do broker MQTT (OU PRESSIONE ENTER para utilizar o endereço do servidor conectado): ")

    if (vehicle.brokerCandidate == ""):
        vehicle.broker = vehicle.serverAddress
    elif (vehicle.brokerCandidate == "test"):
        vehicle.broker = vehicle.testBroker
    else:
        vehicle.broker = vehicle.brokerCandidate


#Verifica se o arquivo de texto "vehicle_data.json" esta presente, e caso nao esteja...
if (verifyFile(["vehicledata"], "vehicle_data.json") == False):
    
    try:
        dataTable["capacity"] = str(argNumber(sys.argv[1]))
    except:
        dataTable["capacity"] = "100.0"

    try:
        dataTable["autonomy"] = str(argNumber(sys.argv[2]))
    except:
        dataTable["autonomy"] = "300.0"

    try:
        dataTable["battery_level"] = str(argNumber(sys.argv[3]))
    except:
        dataTable["battery_level"] = "0.5"

    try:
        dataTable["coord_x"] = str(argNumber(sys.argv[4]))
    except:
        dataTable["coord_x"] = "1.0"
    
    try:
        dataTable["coord_y"] = str(argNumber(sys.argv[5]))
    except:
        dataTable["coord_y"] = "1.0"

    #E tambem cria o arquivo e preenche com as informacoes contidas no dicionario acima
    writeFile(["vehicledata", "vehicle_data.json"], dataTable)

#Caso esteja presente...
else:

    #Carrega as informacoes gravadas (vehicle_data)
    dataTable = readFile(["vehicledata", "vehicle_data.json"])

    try:
        newBatteryLevel = str(argNumber(sys.argv[1]))
        dataTable["battery_level"] = newBatteryLevel
    except:
        pass

    try:
        newCoordX = str(argNumber(sys.argv[2]))
        dataTable["coord_x"] = newCoordX
    except:
        pass
    
    try:
        newCoordY = str(argNumber(sys.argv[3]))
        dataTable["coord_y"] = newCoordY
    except:
        pass

    #Gravas as informacoes atualizadas passadas por parametros
    writeFile(["vehicledata", "vehicle_data.json"], dataTable)

#Carrega as informacoes gravadas (ID)
vehicle.ID = readFile(["vehicledata", "ID.txt"])

#Inicia janela principal
ctk_frame_main._set_appearance_mode('dark')
ctk_frame_main.title('EVClient v2.0.0')
ctk_frame_main.geometry('600x800')

#Insere elementos graficos da janela principal
label_user_ID.pack(pady=20)
label_battery_info.pack(pady=10)
label_autonomy_info.pack(pady=10)
label_critical_battery_warning.pack(pady=20)
box_local_server_address.pack(pady=10)
button_open_recharge_manager.pack(pady=20)
button_open_route_manager.pack(pady=10)
button_open_history.pack(pady=20)

#Inicia o thread responsavel por atualizar as informacoes exibidas nas diversas janelas
newThread = threading.Thread(target=infoUpdate, args=())
newThread.start()

ctk_frame_main.mainloop()