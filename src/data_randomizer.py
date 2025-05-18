import os
import json
import random

#Funcao que cria um arquivo baseando em uma lista com o caminho dele e um dicionario do conteudo a ser adicionado 
def writeFile(pathList, contentTable):

    #String do caminho a ser aberto, inicialmente vazia
    pathString = ""

    #Percorre a lista do caminho de forma a construir a string deste
    for pathIndex in range(0, len(pathList)):
        
        pathString = os.path.join(pathString, pathList[pathIndex])

    #Abre o arquivo em modo de escrita
    with open(pathString, "w") as file:
        
        #Joga o conteudo do dicionario no arquivo por meio de json
        json.dump(contentTable, file)


#Funcao que le um arquivo baseado em uma lista com o caminho dele
def readFile(pathList):

    #String do caminho a ser aberto, inicialmente vazia
    pathString = ""

    #Percorre a lista do caminho de forma a construir a string deste
    for pathIndex in range(0, len(pathList)):
        
        pathString = os.path.join(pathString, pathList[pathIndex])
    
    #Abre o arquivo em modo de leitura
    with open(pathString, "r") as file:
        
        #Retorna o conteudo carregado por meio de json
        return json.load(file)
    
#Funcao para retornar um numero aleatorio dentro de um intervalo, por distribuicao binomial
def getBinomialRandomInt(minimumValue: int, maximumValue: int) -> int:

    rollNumber = (maximumValue - minimumValue)
    
    #Soma para retornar
    randSum = minimumValue

    #Itera pelo numero de rolagens
    for iteration in range(0, rollNumber):
        
        #Sorteia com 50% de chace de aumentar o numero
        incrementRandomInt = random.randint(0,1)

        #Se sortear positivo (1), aumenta pelo incremento
        if incrementRandomInt == 1:

            randSum += 1

    #Retorna a soma inteira
    return int(randSum)


#Itera por todos os veiculos
for vehicleIndex in range(0, 4):

    #Gera dados aleatorios do veiculo
    randomVehicleConsumption = (getBinomialRandomInt(12, 25) / 100)
    randomVehicleCapacity = getBinomialRandomInt(40, 120)
    randomVehicleAutonomy = int(randomVehicleCapacity / randomVehicleConsumption)
    randomVehicleBatteryLevel = (getBinomialRandomInt(15, 100) / 100)

    #Abre arquivo do veiculo
    vehicleFolderName = ("vehicle_0" + str(vehicleIndex + 1))
    vehicleTable = readFile(["files_test", vehicleFolderName, "vehicledata", "vehicle_data.json"])

    #Coloca as informacoes no dicionario
    vehicleTable["capacity"] = str(randomVehicleCapacity)
    vehicleTable["autonomy"] = str(randomVehicleAutonomy)
    vehicleTable["battery_level"] = str(randomVehicleBatteryLevel)

    #Grava as informacoes geradas
    writeFile(["files_test", vehicleFolderName, "vehicledata", "vehicle_data.json"], vehicleTable)

#Itera por todas as estacoes
for stationIndex in range(0, 10):

    #Gera dados aleatorios da estacao
    randomUnitaryPrice = (getBinomialRandomInt(60, 90) / 100)

    stationFolderName = ""
    if stationIndex < 9:
        stationFolderName = ("station_0" + str(stationIndex + 1))
    else:
        stationFolderName = "station_10"

    #Abre arquivo da estacao
    stationTable = readFile(["files_test", stationFolderName, "stationdata", "station_data.json"])
    
    #Coloca a informacao no dicionario
    stationTable["unitary_price"] = str(randomUnitaryPrice)

    #Gravas as informacoes geradas
    writeFile(["files_test", stationFolderName, "stationdata", "station_data.json"], stationTable)


'''for randomRollIndex in range(0, 20):

    print((getBinomialRandomInt(12, 30, 50)/100))'''