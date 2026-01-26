# Dependências
import re

# ----------------------------------------------
# Função para normalizar CNPJ
# ----------------------------------------------
def normalize_cnpj(value: str) -> str:
    '''
    Normaliza um CNPJ removendo todos os caracteres não numéricos.
    Args:
        value (str): O CNPJ a ser normalizado.
    Returns:
        str: O CNPJ normalizado contendo apenas dígitos numéricos.
    Raises:
        ValueError: Se o CNPJ não contiver exatamente 14 dígitos numéricos.    
    '''
    digits = re.sub(r"\D", "", value)

    if len(digits) != 14:
        raise ValueError("CNPJ must contain exactly 14 numeric digits")

    return digits
