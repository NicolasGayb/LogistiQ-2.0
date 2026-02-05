from fastapi import Request

def get_real_ip(request: Request) -> str:
    """Obtém o endereço IP real do cliente, considerando possíveis proxies."""
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.client.host
    return ip