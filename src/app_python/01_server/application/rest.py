###########################################################
#
# => MODULO DE COMUNICACAO VIA PROTOCOLO HTTP-REST <=
#
###########################################################


#Importa bibliotecas basicas do python 3
import threading
import json
import socket
import http.server

#Importa os modulos da aplicacao
from application.properties import *
from application.util import *
from application.chargeroute import doReservation as doReservationAlt
from application.chargeroute import undoReservation as undoReservationAlt


#Lock para modificacao da variavel que diz se o ultimo thread de recebimento de requisicoes HTTP-REST esta ocupado
httpHandlerLock = threading.Lock()

#Variavel que diz se o ultimo thread de recebimento de requisicoes HTTP-REST esta ocupado, precisando portanto da criacao de um novo (se possivel)
isInNeedOfHTTPHandler = False


#Extensao da classe de servidor HTTP
class CustomHTTPServer(http.server.HTTPServer):

    #Override do metodo chamado para linkar soquetes
    def server_bind(self):
        
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()

#Extensao da classe que lida com callbacks em requisicoes HTTP
class RequestHandler(http.server.BaseHTTPRequestHandler):

    global fileLock
    global httpHandlerLock
    global isInNeedOfHTTPHandler

    #Override para silenciar o logging de mensagens
    def log_message(self, format, *args):
        pass

    #Override do metodo chamado a cada nova requisicao tipo POST que chega ao servidor
    def do_POST(self):
        
        global fileLock
        global httpHandlerLock
        global isInNeedOfHTTPHandler

        httpHandlerLock.acquire()
        isInNeedOfHTTPHandler = True
        httpHandlerLock.release()

        #Se a URL tiver extensao /submit/ 
        if self.path == '/submit':
            
            try:

                #Obtem informacoes da requisicao
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')

                #Transforma o conteudo JSON em objeto python
                data = json.loads(post_data)
                
                clientAddressString, _ = self.client_address
                #Registra no log
                registerLogEntry(fileLock, ["logs", "received"], "HTTPREQUEST", "ADDRESS", clientAddressString)
                
                #Prepara o codigo e o cabecalho da resposta
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                #Faz acao desejada, se aplicavel, e obtem retorno
                response_data = attemptAction(data)
                self.wfile.write(json.dumps(response_data).encode())
            
            except:
                
                response_data = "ERR3"
                self.wfile.write(json.dumps(response_data).encode())
        
        else:
            
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response_data = {"ERR": "PAGE NOT FOUND => use /submit"}
            self.wfile.write(json.dumps(response_data).encode())

def attemptAction(data):
    
    #Se o formato for adequado
    try:
        
        #Dados da requisicao (Nome e parametros)
        requestName = data[0]
        requestParameters = data[1]
        
        #Executa a requisica desejada e retorna a resposta
        if (requestName == 'drr'):
            
            return doReservationAlt(fileLock, timeWindow, requestParameters)
        elif (requestName == 'urr'):
            
            return undoReservationAlt(fileLock, requestParameters)
        else:

            return "ERR1"

    except:
        
        return "ERR2"