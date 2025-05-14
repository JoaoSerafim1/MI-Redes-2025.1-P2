#PROPRIEDADES DO SERVIDOR
####################################################################################

#Maximo de threads simultaneos para requisicoes de clientes (estacoes, veiculos)
maxClientThreads = 8

#Maximo de threads simultaneos para requisicoes de outros servidores
maxServerThreads = 8

#Porta do broker MQTT e porta para requisicoes HTTP
mqttPort = 1883
httpPort = 8025

#IP do broker MQTT de teste
testBroker = 'broker.emqx.io'

#Tempo em segundos antes e depois do horario exato marcado durante o qual um posto de recarga sera considerado como "ocupado"
timeWindow = 7200

####################################################################################