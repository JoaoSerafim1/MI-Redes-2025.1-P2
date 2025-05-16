#modulo para geração de ID
import uuid


#PLACEHOLDER
#Funcao que simula a geracao de uma guia de pagamento
def simulatePayment(capacity, battery_level, price): #metodo que envia a solicitacao de pagamento ao servidor, recebe a confirmação e atualiza payment_history

    purchaseID = str(uuid.uuid4())

    batteryToFill = float(float(1.0) - float(battery_level))
    amountToPay = (batteryToFill * float(capacity) * float(price))

    return (purchaseID, str(amountToPay))

#PLACEHOLDER
#Funcao que simula a confirmacao de pagamento
def confirmPayment(purchaseID):

    if (len(purchaseID) > 0):

        return True
    else:

        return False