import os
import json

#Funcao que retorna uma lista dos arquivos presentes em um determinado diretorio
def listFiles(pathList):

    #String do caminho a ser aberto, inicialmente vazia
    pathString = ""

    #Percorre a lista do caminho de forma a construir a string deste
    for pathIndex in range(0, len(pathList)):
        
        pathString = os.path.join(pathString, pathList[pathIndex])

    try:
        fileList = os.listdir(pathString)
        return fileList
    except:
        return []

#Funcao que verifica se existe um arquivo especifico no diretorio fornecido
def verifyFile(pathList, fileName):

    #String do caminho a ser aberto, inicialmente vazia
    pathString = ""

    #Percorre a lista do caminho de forma a construir a string deste
    for pathIndex in range(0, len(pathList)):
        
        pathString = os.path.join(pathString, pathList[pathIndex])

    pathString = os.path.join(pathString, fileName)
    
    #Bloco try-except para verificar existencia do arquivo
    try:

        #Abre o arquivo em modo de leitura
        with open(pathString, "r") as file:
            
            #Arquivo existe, retorna verdadeiro
            return True
        
    except:

        #Arquivo nao existe, retorna falso
        return False



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