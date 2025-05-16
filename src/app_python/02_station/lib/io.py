#Funcao para introduzir entrada numerica apenas
def enterNumber(prompt, error):
    
    result = ""

    while True:
        
        try:
            result = float(input(prompt))
            return result
        except:
            print(error)

#Funcao para introduzir entrada numerica inteira apenas
def enterInt(prompt, error):
    
    result = ""

    while True:
        
        try:
            result = int(input(prompt))
            return result
        except:
            print(error)