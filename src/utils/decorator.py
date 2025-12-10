from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify
from Application.models import Produtor
from functools import wraps

def produtor_required(f):
    """
    Decorator que:
    1. Verifica se tem JWT válido
    2. Pega o produtor logado
    3. Coloca o objeto produtor no request (ou retorna erro se não existir)
    Uso:
        @produtor_required
        def minha_rota(produtor):
            return f"Olá {produtor.nome}"
    """
    @wraps(f)
    @jwt_required()
    def wrapper(*args, **kwargs):
        produtor_id = get_jwt_identity()
        produtor = Produtor.query.get(produtor_id)

        if not produtor:
            return jsonify({"erro": "Produtor não encontrado"}), 404

        # Passa o produtor como argumento para a rota
        return f(produtor, *args, **kwargs)
    
    return wrapper