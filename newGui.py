
#Importa customTkinter
import customtkinter as ctk

#Classe do usuario
class User():
    
    #Funcao inicializadora da classe
    def __init__(self):
        
        #Atributos
        self.ID = ""
        self.battery_level = ""
        self.capacity = ""
        self.vehicle = ""
        self.payment_history = {}
        #self.clientIP = str(socket.gethostbyname(socket.gethostname()))
        
    def nearestSpotRequest(self):
        return
    def simulateForNearestSpot(self):
        return
    def payForNearestSpot(self):
        return
#funçõo auxiliar para obter retorno de placeholders    
def getOriginServerPlaceholders():
    server1 = originPlaceholder.get()
    return server1

vehicle = User()

#Frame1 = Janela principal
frame = ctk.CTk()
frame._set_appearance_mode('dark')
frame.title('Cliente')
frame.geometry('600x800')

#id do veiculo
userID = ctk.CTkLabel(frame,text=("" + vehicle.ID + " "))
userID.pack(pady=20)

#info
battery_info_text = ctk.StringVar()
battery_info = ctk.CTkLabel(frame,textvariable=battery_info_text)
battery_info.pack(pady=10)

critical_battery_text = ctk.StringVar()
critical_battery = ctk.CTkLabel(frame,textvariable=critical_battery_text)
critical_battery.pack(pady=20)


originPlaceholder = ctk.CTkEntry(frame,placeholder_text='Digite o Servidor de origem',width=180)
originPlaceholder.pack(pady=10)

validateServersButton = ctk.CTkButton(frame,text=' Selecionar servidor ',command=getOriginServerPlaceholders) #precisa da referência da função correta
validateServersButton.pack(pady=20)
#TopLevelStatus

#Recharge StringVar
distance_info_text = ctk.StringVar()
next_purchase_info_text = ctk.StringVar()
next_purchase_result_text = ctk.StringVar()
#History StringVar
purchaseHistoryID = ctk.StringVar()
purchaseHistoryTotal = ctk.StringVar()
purchaseHistoryPrice = ctk.StringVar()
purchaseHistoryCharge = ctk.StringVar()
#Route StringVar
routeInfo = ctk.StringVar()
routeSelectionResult = ctk.StringVar()
routeServer = None
#frame4 = Gerenciador de Recarga

def closeAny(frame):
    frame.destroy()
    frame.update()

def openRechargeManager():

    frame4 = ctk.CTkToplevel(frame) 
    frame4.title('Gerenciar Recarga')
    frame4.geometry('600x800')
    frame4.attributes('-topmost',True)

    spotRequestButton = ctk.CTkButton(frame4,text=' Obter a distância até a estação de recarga mais próxima e o preço do KWh ',command=lambda:vehicle.nearestSpotRequest())
    spotRequestButton.pack(pady=10)

    distance_info = ctk.CTkLabel(frame4,textvariable=distance_info_text)
    distance_info.pack(pady=20)

    simulatePayButton = ctk.CTkButton(frame4,text=' Gerar guia de pagamento ',command=lambda:vehicle.simulateForNearestSpot())
    simulatePayButton.pack(pady=10)
    
    next_purchase_info = ctk.CTkLabel(frame4,textvariable=next_purchase_info_text)
    next_purchase_info.pack(pady=20)

    bookButton = ctk.CTkButton(frame4,text=' Recarregar totalmente na estação mais próxima ',command=lambda:vehicle.payForNearestSpot())
    bookButton.pack(pady=10)

    next_purchase_result = ctk.CTkLabel(frame4,textvariable=next_purchase_result_text)
    next_purchase_result.pack(pady=30)

    def closeRRMWindow():
        frame4.destroy()
        frame4.update()
    closeRRButton = ctk.CTkButton(frame4,text=' Fechar Gerenciador de Recargas ',command=closeRRMWindow)
    closeRRButton.pack(pady=20)

openRM = ctk.CTkButton(frame,text=' Recarregar ',command=openRechargeManager)
openRM.pack(pady=20)

#Frame2 = Gerenciador de Rotas
def openRechargeRouteManager():

    frame2 = ctk.CTkToplevel(frame)
    frame2.title('Gerenciar Recargas na Rotas')
    frame2.geometry('600x800')
    frame2.attributes('-topmost',True)
    
    def getDestinationPlaceholders():
        server2 = destinationPlaceholder.get()
        global routeServer
        routeServer = server2
        return server2
    
    destinationPlaceholder = ctk.CTkEntry(frame2,placeholder_text='Digite o Servidor de destino',width=180)
    destinationPlaceholder.pack(pady=10)

    routeInfoLabel = ctk.CTkLabel(frame2,textvariable=routeInfo)
    routeInfoLabel.pack(pady=30)
    #comandos a serem definidos
    
    backButton = ctk.CTkButton(frame2,text=' < ')
    backButton.pack(pady=5)

    forwardButton = ctk.CTkButton(frame2,text=' > ')
    forwardButton.pack(pady=20)
    
    selectRouteButton = ctk.CTkButton(frame2,text=' Selecionar Rota ',command=getDestinationPlaceholders)
    selectRouteButton.pack(pady=5)

    route_selection_ResultLabel = ctk.CTkLabel(frame2,textvariable=routeSelectionResult)
    route_selection_ResultLabel.pack(pady=30)
    
    def closeRRMWindow():
        frame2.destroy()
        frame2.update()
    closeRRMButton = ctk.CTkButton(frame2,text=' Fechar Gerenciador de Rotas ',command=closeRRMWindow)
    closeRRMButton.pack(pady=20)

openRRMButton = ctk.CTkButton(frame,text=' Gerenciar Recarga na Rota ',command=openRechargeRouteManager)
openRRMButton.pack(pady=10)

#frame3 = histórico
def openHistoryWindow():

    frame3 = ctk.CTkToplevel(frame)
    frame3.title('Histórico')
    frame3.geometry('400x600')
    frame3.attributes('-topmost',True)

    purchaseHistoryIDLabel = ctk.CTkLabel(frame3,textvariable=purchaseHistoryID)
    purchaseHistoryIDLabel.pack(pady=5)

    
    purchaseHistoryTotalLabel = ctk.CTkLabel(frame3,textvariable=purchaseHistoryTotal)
    purchaseHistoryTotalLabel.pack(pady=5)

    
    purchaseHistoryPriceLabel = ctk.CTkLabel(frame3,textvariable=purchaseHistoryPrice)
    purchaseHistoryPriceLabel.pack(pady=5)

    
    purchaseHistoryChargeLabel = ctk.CTkLabel(frame3,textvariable=purchaseHistoryCharge)
    purchaseHistoryChargeLabel.pack(pady=10)

    bckButton = ctk.CTkButton(frame3,text=' < ',command=lambda:vehicle.purchaseBackward())
    bckButton.pack(pady=5)

    bckButton = ctk.CTkButton(frame3,text=' > ',command=lambda:vehicle.purchaseForward())
    bckButton.pack(pady=20)
    
    def closeHistoryWindow():
        frame3.destroy()
        frame3.update()
    closeHistoryButton = ctk.CTkButton(frame3,text=' Fechar histórico ',command=closeHistoryWindow)
    closeHistoryButton.pack(pady=20)
    
openHistoryButton = ctk.CTkButton(frame,text=' Abrir Histórico ',command=openHistoryWindow)
openHistoryButton.pack(pady=20)


    
frame.mainloop()