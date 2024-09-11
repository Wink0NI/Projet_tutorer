# Retourner une valeur string en Int ou Float
def str_to_none(value):
    return None if value == 'NULL' else value

def str_to_nbr(value):
    try:
        return float(value) if '.' in value else int(value)
    except:
        return value