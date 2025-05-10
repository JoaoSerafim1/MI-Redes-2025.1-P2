#Funcao para introduzir entrada numerica apenas
def argNumber(prompt):

    while True:
        
        try:
            result = float(prompt)
            return result
        except:
            pass