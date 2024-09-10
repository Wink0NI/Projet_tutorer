import math

# Retourner une valeur string en Int ou Float
def str_to_nbr(value):
    try:
        value = float(value)
        if value - math.floor(value) == 0:
            value = int(value)
        return value
    except:
        return value
    
# Retourner une valeur NULL en None
def str_to_none(value):
    if value == "NULL":
        value = None
    return value