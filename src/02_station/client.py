#Importa bibliotecas basicas do python 3
import json
import socket
import time

#Importa as bibliotecas customizadas da aplicacao
from lib.db import *
from lib.io import *
from lib.ch import *


#Classe do usuario
class Station():
    
    #Funcao inicializadora da classe
    def __init__(self):
        
        #Atributos
        self.ID = ""
        self.unitaryPrice = 0
        self.actualVehicleID = ""
        self.remainingCharge = 0
    
    #Funcao para enviar uma requisicao ao servidor
    def sendRequest(self, request):

        global serverAddress

        #Cria o soquete e torna a conexao reciclavel
        socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        #Serializa a requisicao utilizando json
        serializedRequest = json.dumps(request)

        #print("--------------------------------------------")
        #print(serverAddress)
        #print(serializedRequest)
        #print("--------------------------------------------")
        
        try:
            #Tenta fazer a conexao (endereco do servidor, porta 8001), envia a requisicao em formato "bytes", codec "UTF-8", pela conexao
            socket_sender.connect((serverAddress, 8001))
            socket_sender.send(bytes(serializedRequest, 'UTF-8'))
        except:
            pass

        #Fecha a conexao (desfaz o soquete)
        socket_sender.close()

    #Funcao para receber uma resposta de requisicao
    def receiveResponse(self, timeout):

        #Cria o soquete, torna a conexao reciclavel, estabelece um timeout (10 segundos), reserva a porta local 8002 para a conexao e liga o modo de escuta
        socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        if (timeout != 0):
            socket_receiver.settimeout(timeout)

        socket_receiver.bind((socket.gethostbyname(socket.gethostname()), 8002))
        socket_receiver.listen(2)

        #Valores iniciais da mensagem de resposta (mensagem vazia)
        msg = bytes([])
        add = ""
        
        try:
            #Espera a mensagem pelo tempo estipulado no timeout
            conn, add = socket_receiver.accept()
            msg = conn.recv(1024)
        except:
            pass
        
        #Fecha a conexao (desfaz o soquete)
        socket_receiver.close()
        
        #Decodifica a mensagem (a qual foi enviada em formato "bytes", codec "UTF-8")
        decodedBytes = msg.decode('UTF-8')
        
        #Se uma resposta valida foi recebida, a mensagem nao deve ser vazia
        if (len(decodedBytes) > 0):

            #print("=============================================")
            #print(add)
            #print(msg)
            #print(decodedBytes)
            #print("=============================================")

            #De-serializa a mensagem decodificada 
            unserializedObj = json.loads(decodedBytes)

            #Retorna o objeto da mensagem
            return (add, unserializedObj)
        
        #Retorna atributos de uma mensagem nao-recebida ou vazia
        return (add, "")
    
    #Funcao para registrar a estacao
    def registerStation(self, coord_x, coord_y, unitary_price):
        
        global requestID

        #Garante que a criacao da estacao so acontece uma vez
        #O servidor esta condicionado a executar requisicoes de indice 0 mesmo que a ultima requisicao para certo endereco tenha indice 0
        #Assim sendo, e preciso colocar um indice distinto de zero para forcar que isso nao aconteca
        #Entretanto, indices de 1 a 63 sao utilizados no ciclo normal de requisicao, entao o numero arbitrario aqui deve estar fora do intervalo
        #Caso contrario, poderia acontecer de o cliente nao conseguir registrar um novo veiculo no endereco, pois a ultima requisicao era do indice escolhido
        requestID = 64
        
        #ID da estacao
        stationID = input("ID para a estacao de carga (como fornecido pelo servidor): ")

        #Parametros da requisicao
        requestParameters = [stationID, coord_x, coord_y, unitary_price]

        #Formula o conteudo da requisicao a ser enviada
        #O conteudo e uma lista de ao menos 3 elementos (ID da requisicao, nome da requisicao e parametros da mesma)
        requestContent = [requestID, 'rcs', requestParameters]
        
        #Envia a requisicao para o servidor da aplicacao
        self.sendRequest(requestContent)

        #Espera a resposta
        (_, response) = self.receiveResponse(10)

        #Se a resposta nao for adequada ("OK")...
        while (response != "OK"):
            
            #ID da estacao
            stationID = input("ID para a estacao de carga (como fornecido pelo servidor): ")

            #Parametros da requisicao
            requestParameters = [stationID, coord_x, coord_y, unitary_price]

            #Formula o conteudo da requisicao a ser enviada
            #O conteudo e uma lista de ao menos 3 elementos (ID da requisicao, nome da requisicao e parametros da mesma)
            requestContent = [requestID, 'rcs', requestParameters]
            
            #Envia a requisicao para o servidor da aplicacao
            self.sendRequest(requestContent)

            #Espera a resposta
            (_, response) = self.receiveResponse(10)

            #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
            if (int(requestID) < 63):
                requestID = str(int(requestID) + 1)
            else:
                requestID = "1"

        #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"

        #Retorna a resposta (ID da estacao)
        return stationID
    
    def getBookedVehicle(self):

        global requestID

        #Formula o conteudo da requisicao a ser enviada
        #O conteudo e uma lista de ao menos 3 elementos (ID da requisicao, nome da requisicao e parametros da mesma)
        requestContent = [requestID, 'gbv', [self.ID]]
        
        #Envia a requisicao para o servidor da aplicacao
        self.sendRequest(requestContent)

        #Espera a resposta
        (_, response) = self.receiveResponse(10)

        #Se a resposta nao for adequada...
        while (response == ""):
            
            #Envia a requisicao para o servidor da aplicacao
            self.sendRequest(requestContent)

            #Espera a resposta
            (_, response) = self.receiveResponse(10)

        #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"

        return response

    def chargeSequence(self):

        global requestID
        global loadedTable
        
        #Enquanto o ID do veiculo em processo de carga nao seja vazio
        while (self.actualVehicleID != ""):

            #Executa a funcao externa de carga (encontrado em lib/ch.py)
            self.remainingCharge = doCharge(self.actualVehicleID, self.remainingCharge)

            #Caso a carga restante seja 0, sabemos que acabou o processo, e resetamos o ID do veiculo para vazio
            if (self.remainingCharge == 0):
                self.actualVehicleID = ""

        #Formula o conteudo da requisicao a ser enviada
        #O conteudo e uma lista de ao menos 4 elementos (ID de quem requeriu, ID da requisicao, nome da requisicao e parametros da mesma)
        requestContent = [requestID, 'fcs', [self.ID]]
        
        #Envia a requisicao para o servidor da aplicacao
        self.sendRequest(requestContent)

        #Espera a resposta
        (_, response) = self.receiveResponse(10)

        #Se a resposta nao for adequada ("OK" ou "NF")...
        while (response != "OK" and response != "NF"):
            
            #Envia a requisicao para o servidor da aplicacao
            self.sendRequest(requestContent)

            #Espera a resposta
            (_, response) = self.receiveResponse(10)

        #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"


#Programa inicia aqui
#Cria um objeto da classe Station
station = Station()

#Valores iniciais do programa
requestID = "0"

#Cria um dicionario dos atributos da estacao
dataTable = {}

#Pergunta endereco do servidor
serverAddress = input("Insira o endereço IP do servidor: ")

#Verifica se o arquivo de texto "station_data.json" esta presente, e caso nao esteja...
if (verifyFile(["stationdata"], "station_data.json") == False):

    #Valores dos pares chave-valor sao sempre string para evitar problemas com json
    dataTable["coord_x"] = str(enterNumber("Coordenada x do posto de recarga: ", "ENTRADA INVALIDA."))
    dataTable["coord_y"] = str(enterNumber("Coordenada y do posto de recarga: ", "ENTRADA INVALIDA."))
    dataTable["unitary_price"] = str(enterNumber("Preco unitario do KWh, em BRL: ", "ENTRADA INVALIDA."))

    #E tambem cria o arquivo e preenche com as informacoes contidas no dicionario acima
    writeFile(["stationdata", "station_data.json"], dataTable)

#Caso contrario
else:

    #Carrega as informacoes gravadas
    dataTable = readFile(["stationdata", "station_data.json"])


#Verifica se o arquivo de texto "ID.txt" esta presente, e caso nao esteja...
if (verifyFile(["stationdata"], "ID.txt") == False):

    #ID da estacaodataTable["coord_x"]
    stationID = station.registerStation(dataTable["coord_x"], dataTable["coord_y"], dataTable["unitary_price"])
    
    #Cria um novo arquivo
    writeFile(["stationdata", "ID.txt"], stationID)

#Carrega as informacoes gravadas (ID)
station.ID = readFile(["stationdata", "ID.txt"])

#Carrega as informacoes gravadas (station_data)
loadedTable = readFile(["stationdata", "station_data.json"])

#Modifica as informacoes do objeto da estacao
station.unitaryPrice = float(loadedTable["unitary_price"])

#Print das informacões
print("*********************************************")
print("ID: " + str(station.ID))
print("Preço do KWh (BRL): " +  str(station.unitaryPrice))
print("*********************************************")

#Loop do programa
while True:

    #Verifica se tem veiculo com carga pendente
    bookedVehicleInfo = station.getBookedVehicle()

    #Caso tenha
    if (bookedVehicleInfo[0] != ""):
        
        station.actualVehicleID = bookedVehicleInfo[0]
        station.remainingCharge = bookedVehicleInfo[1]

        station.chargeSequence()

    #Caso contrario, espera um minuto antes de fazer qualquer outra coisa
    else:

        time.sleep(60)