#Importa bibliotecas basicas do python
import json
import threading

#Importa customTkinter
import customtkinter as ctk

#Importa modulos da aplicacao
from application.user import *


#Cria um objeto da classe User
vehicle = User()

#Frame1 = Janela principal
ctk_frame_main = ctk.CTk()


#Inicializacao de Stringvars
strvar_vehicle_ID = ctk.StringVar()
strvar_battery_info = ctk.StringVar()
strvar_autonomy_info = ctk.StringVar()
strvar_critical_battery_warning = ctk.StringVar()
strvar_distance_info = ctk.StringVar()
strvar_next_purchase_info = ctk.StringVar()
strvar_next_purchase_result = ctk.StringVar()
strvar_purchase_history_ID = ctk.StringVar()
strvar_purchase_history_total = ctk.StringVar()
strvar_purchase_history_price = ctk.StringVar()
strvar_purchase_history_charge = ctk.StringVar()
strvar_route_node_list = ctk.StringVar()
strvar_route_name_list = ctk.StringVar()
strvar_route_reservation_result = ctk.StringVar()


#label de id do veiculo
label_user_ID = ctk.CTkLabel(ctk_frame_main,textvariable=strvar_vehicle_ID) # type: ignore

#Elementos graficos de status do veiculo
label_battery_info = ctk.CTkLabel(ctk_frame_main,textvariable=strvar_battery_info)
label_autonomy_info = ctk.CTkLabel(ctk_frame_main,textvariable=strvar_autonomy_info)
label_critical_battery_warning = ctk.CTkLabel(ctk_frame_main,textvariable=strvar_critical_battery_warning)

#Caixa de entrada do endereço do servidor local (que tambem e origem de uma rota)
box_local_server_address = ctk.CTkEntry(ctk_frame_main,placeholder_text=' insira o endereço do servidor local ',width=240)


def closeAny(frame):
    frame.destroy()
    frame.update()

#frame4 = Gerenciador de Recarga
def openRechargeManager():

    global vehicle

    frame4 = ctk.CTkToplevel(ctk_frame_main) 
    frame4.title('Gerenciador de Recarga')
    frame4.geometry('600x800')
    frame4.attributes('-topmost',True)

    spotRequestButton = ctk.CTkButton(frame4,text=' OBTER INFORMAÇÕES DA ESTAÇÃO MAIS PRÓXIMA ',command=lambda:vehicle.nearestSpotRequest())
    spotRequestButton.pack(pady=10)

    distance_info = ctk.CTkLabel(frame4,textvariable=strvar_distance_info)
    distance_info.pack(pady=20)

    simulatePayButton = ctk.CTkButton(frame4,text=' GERAR GUIA DE PAGAMENTO ',command=lambda:vehicle.simulateForNearestSpot())
    simulatePayButton.pack(pady=10)
    
    next_purchase_info = ctk.CTkLabel(frame4,textvariable=strvar_next_purchase_info)
    next_purchase_info.pack(pady=20)

    bookButton = ctk.CTkButton(frame4,text=' RECARREGAR NA ESTACÃO SELECIONADA ',command=lambda:vehicle.payForNearestSpot())
    bookButton.pack(pady=10)

    next_purchase_result = ctk.CTkLabel(frame4,textvariable=strvar_next_purchase_result)
    next_purchase_result.pack(pady=30)

button_open_recharge_manager = ctk.CTkButton(ctk_frame_main,text=' ABRIR MENU DE RECARGA ',command=openRechargeManager)


#Frame2 = Gerenciador de Rotas
def openRouteManager():

    global vehicle

    frame2 = ctk.CTkToplevel(ctk_frame_main)

    frame2.title('Gerenciador de Rotas')
    frame2.geometry('600x800')
    frame2.attributes('-topmost',True)

    #Caixas de entrada de texto compartilhadas entre diferentes sub-janelas
    box_destination_server_address = ctk.CTkEntry(frame2,placeholder_text=' digite o servidor de destino ',width=200)
    box_destination_server_address.pack(pady=10)

    label_actual_node_list = ctk.CTkLabel(frame2, textvariable= strvar_route_node_list)
    label_actual_node_list.pack(pady=10)

    def routeBackwardGet():

        #Captura o valor do servidor de destino
        tempDestinyServerAddress = box_destination_server_address.get()

        #Se for diferente, volta os indices de rota para zero e atualiza o servidor de destino
        if(tempDestinyServerAddress != vehicle.destinyServerAddress):
            
            vehicle.routeSearchIndex = "0"
            vehicle.routeReservationIndex = "0"
            vehicle.destinyServerAddress = tempDestinyServerAddress

        vehicle.routeBackward()

    def routeForwardGet():

        #Captura o valor do servidor de destino
        tempDestinyServerAddress = box_destination_server_address.get()

        #Se for diferente, volta os indices de rota para zero e atualiza o servidor de destino
        if(tempDestinyServerAddress != vehicle.destinyServerAddress):
            
            vehicle.routeSearchIndex = "0"
            vehicle.routeReservationIndex = "0"
            vehicle.destinyServerAddress = tempDestinyServerAddress

        vehicle.routeForward()

    backButton = ctk.CTkButton(frame2,text=' < ', command=routeBackwardGet)
    backButton.pack(pady=5)

    forwardButton = ctk.CTkButton(frame2,text=' > ', command=routeForwardGet)
    forwardButton.pack(pady=20)

    box_actual_time_to_add = ctk.CTkEntry(frame2,placeholder_text=' digite o horario local em formato DD/MM/AAAA-hh:mm ',width=400)
    box_actual_time_to_add.pack(pady=10)

    def addReservationGet():

        #Captura o valor do horario a ser reservado
        vehicle.routeReservationTimeToAdd = box_actual_time_to_add.get()
        print(vehicle.routeReservationTimeToAdd)

        vehicle.addReservationToList()

    def removeReservationGet():

        vehicle.removeLastReservationFromList()

    button_add_reservation = ctk.CTkButton(frame2,text=' ADICIONAR HORARIO ', command=addReservationGet)
    button_add_reservation.pack(pady=5)

    button_remove_reservation = ctk.CTkButton(frame2,text=' REMOVER HORARIO ANTERIOR ', command=removeReservationGet)
    button_remove_reservation.pack(pady=20)

    label_actual_reservation_name_list = ctk.CTkLabel(frame2, textvariable= strvar_route_name_list)
    label_actual_reservation_name_list.pack(pady=10)
    
    selectRouteButton = ctk.CTkButton(frame2,text=' REQUISITAR RESERVA NA ROTA ', command=lambda:vehicle.confirmReservation())
    selectRouteButton.pack(pady=5)

    route_selection_Result = ctk.CTkLabel(frame2,textvariable=strvar_route_reservation_result)
    route_selection_Result.pack(pady=30)

button_open_route_manager = ctk.CTkButton(ctk_frame_main,text=' ABRIR MENU DE RESERVAS ',command=openRouteManager)


#frame3 = histórico
def openHistoryWindow():

    global vehicle

    frame3 = ctk.CTkToplevel(ctk_frame_main)
    frame3.title('Historico de Compras')
    frame3.geometry('400x600')
    frame3.attributes('-topmost',True)

    
    purchaseHistoryIDLabel = ctk.CTkLabel(frame3,textvariable=strvar_purchase_history_ID)
    purchaseHistoryIDLabel.pack(pady=5)

    
    purchaseHistoryTotalLabel = ctk.CTkLabel(frame3,textvariable=strvar_purchase_history_total)
    purchaseHistoryTotalLabel.pack(pady=5)

    
    purchaseHistoryPriceLabel = ctk.CTkLabel(frame3,textvariable=strvar_purchase_history_price)
    purchaseHistoryPriceLabel.pack(pady=5)

    
    purchaseHistoryChargeLabel = ctk.CTkLabel(frame3,textvariable=strvar_purchase_history_charge)
    purchaseHistoryChargeLabel.pack(pady=10)

    bckButton = ctk.CTkButton(frame3,text=' < ',command=lambda:vehicle.purchaseBackward())
    bckButton.pack(pady=5)

    bckButton = ctk.CTkButton(frame3,text=' > ',command=lambda:vehicle.purchaseForward())
    bckButton.pack(pady=20)
    
button_open_history = ctk.CTkButton(ctk_frame_main,text=' ABRIR HISTÓRICO DE COMPRAS ',command=openHistoryWindow)


#Funcao do thread que monitora mudancas nas informacoes guardadas no arquivo de dados do veiculo
def infoUpdate():

    while True:

        #Carrega as informacoes gravadas (vehicle_data)
        loadedTable = readFile(["vehicledata", "vehicle_data.json"])

        #Modifica as informacoes do objeto do veiculo
        vehicle.battery_level = loadedTable["battery_level"]
        vehicle.capacity = loadedTable["capacity"]
        vehicle.autonomy = loadedTable["autonomy"]

        #Atualiza label do ID do veiculo
        strvar_vehicle_ID.set(" " + vehicle.ID + " ")

        #Atualiza label de autonomia do veiculo
        strvar_autonomy_info.set(" Autonomia: " + vehicle.autonomy + " Km ")

        #Atualiza label de texto do nivel da bateria e do aviso de bateria critica (menos de 30 porcento)
        strvar_battery_info.set(" Carga: " + str(float(vehicle.battery_level) * 100) + "% => " + str(float(vehicle.capacity) * float(vehicle.battery_level)) + "/" + str(vehicle.capacity) + " KWh ")
        if (float(vehicle.battery_level) < 0.3):
            strvar_critical_battery_warning.set(" BATERIA EM NÍVEL CRÍTICO! ")
        else:
            strvar_critical_battery_warning.set(" BATERIA NORMAL ")

        #Captura o valor do servidor local
        tempLocalServerAddress = box_local_server_address.get()

        #Se for diferente, volta os indices de rota para zero e atualiza o servidor de destino
        if(tempLocalServerAddress != vehicle.serverAddress):
            
            vehicle.historyPurchaseIndex = "0"
            vehicle.serverAddress = tempLocalServerAddress
        
        #Atualiza o endereco do broker de acordo com a entrada inicial e com o endereco atual do servidor
        if (vehicle.brokerCandidate == ""):
            vehicle.broker = vehicle.serverAddress
        elif (vehicle.brokerCandidate == "test"):
            vehicle.broker = vehicle.testBroker
        else:
            vehicle.broker = vehicle.brokerCandidate
        
        
        #INFORMACOES DA JANELA DE CARREGAMENTO
        #Atualiza label de texto de informacao da distancia
        if (vehicle.nearestStationID != ""):
            strvar_distance_info.set((" DISTANCIA: " + vehicle.nearestStationDistance + " Km | Preço do KWh: " + vehicle.nearestStationPrice + " "))
        else:
            strvar_distance_info.set(vehicle.nearestStationDistance)

        #Atualiza texto de informacao da proxima compra a ser realizada
        if(len(vehicle.nextPurchaseID) > 0):
            strvar_next_purchase_info.set(" UUID da compra: " + vehicle.nextPurchaseID + " / TOTAL: " + vehicle.nextAmountToPay + " ")
        else:
            strvar_next_purchase_info.set(" Não existe compra esperando confirmação. ")

        #Atualiza texto de informacao da janela de rota
        strvar_route_node_list.set(json.dumps(vehicle.routeNameList))
        strvar_route_name_list.set(json.dumps(vehicle.routeReservationNameList))
        strvar_route_reservation_result.set(vehicle.routeReservationResult)
        
        #INFORMACOES DA JANELA DE HISTORICO DE COMPRAS
        #Atualiza texto de informacao da ultima compra realizada
        strvar_next_purchase_result.set(vehicle.purchaseResult)

        #Atualiza texto das informacoes do historico de compra
        strvar_purchase_history_ID.set(" UUID da compra no histórico: " + vehicle.historyPurchaseID + " ")
        strvar_purchase_history_total.set(" Valor Total da compra no histórico (BRL): " + vehicle.historyPurchaseTotal + " ")
        strvar_purchase_history_price.set(" Preço do KWh da compra no histórico (BRL): " + vehicle.historyPurchasePrice + " ")
        strvar_purchase_history_charge.set(" Carga total da compra no histórico (KWh): " + vehicle.historyPurchaseCharge + " ")