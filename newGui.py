
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
def getServerPlaceholders():
    server1 = originPlaceholder.get()
    server2 = destinationPlaceholder.get()
    tuple = (server1,server2)
    return tuple
vehicle = User()

#Frame1 = Janela principal
frame = ctk.CTk()
frame._set_appearance_mode('dark')
frame.title('Cliente')
frame.geometry('600x800')

userID = ctk.CTkLabel(frame,text=("ID do veiculo " + vehicle.ID + " "))
userID.pack(pady=20)

battery_info_text = ctk.StringVar()
battery_info = ctk.CTkLabel(frame,textvariable=battery_info_text)
battery_info.pack(pady=10)

critical_battery_text = ctk.StringVar()
critical_battery = ctk.CTkLabel(frame,textvariable=critical_battery_text)
critical_battery.pack(pady=20)

spotRequestButton = ctk.CTkButton(frame,text=' Obter a distância até a estação de recarga mais próxima e o preço do KWh ',command=lambda:vehicle.nearestSpotRequest())
spotRequestButton.pack(pady=10)

distance_info_text = ctk.StringVar()
distance_info = ctk.CTkLabel(frame,textvariable=distance_info_text)
distance_info.pack(pady=20)

simulatePayButton = ctk.CTkButton(frame,text=' Gerar guia de pagamento ',command=lambda:vehicle.simulateForNearestSpot())
simulatePayButton.pack(pady=10)

next_purchase_info_text = ctk.StringVar()
next_purchase_info = ctk.CTkLabel(frame,textvariable=next_purchase_info_text)
next_purchase_info.pack(pady=20)

bookButton = ctk.CTkButton(frame,text=' Recarregar totalmente na estação mais próxima ',command=lambda:vehicle.payForNearestSpot())
bookButton.pack(pady=10)

next_purchase_result_text = ctk.StringVar()
next_purchase_result = ctk.CTkLabel(frame,textvariable=next_purchase_result_text)
next_purchase_result.pack(pady=30)

originPlaceholder = ctk.CTkEntry(frame,placeholder_text='Digite o Servidor de origem')
originPlaceholder.pack(pady=10)

destinationPlaceholder = ctk.CTkEntry(frame,placeholder_text='Digite o Servidor de destino')
destinationPlaceholder.pack(pady=10)

validateServersButton = ctk.CTkButton(frame,text=' Selecionar servidores ',command=getServerPlaceholders) #precisa da referência da função correta
validateServersButton.pack(pady=20)

purchaseHistoryID = ctk.StringVar()
purchaseHistoryTotal = ctk.StringVar()
purchaseHistoryPrice = ctk.StringVar()
purchaseHistoryCharge = ctk.StringVar()
#Frame2 = Gerenciador de Rotas

def openRechargeRouteManager():
    frame2 = ctk.CTkToplevel(frame)
    frame2.title('Gerenciar Recargas na Rotas')
    frame2.geometry('600x800')
    frame2.attributes('-topmost',True)
    
    #comandos a serem definidos
    backButton = ctk.CTkButton(frame2,text=' < ')
    backButton.pack(pady=5)

    forwardButton = ctk.CTkButton(frame2,text=' > ')
    forwardButton.pack(pady=20)
    
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