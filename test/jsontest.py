import json

#Abre o arquivo em modo de escrita
with open("dumptest.json", "w") as file:
    
    #Joga o conteudo do dicionario no arquivo por meio de json
    json.dump([[("172.18.0.3", "A"), ("172.18.0.4", "B")], [("172.18.0.4", "B"), ("172.18.0.5", "C")]], file)