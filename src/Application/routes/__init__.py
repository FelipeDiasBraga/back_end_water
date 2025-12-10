from .auth import auth_bp
from .fazendas import fazendas_bp
from .talhoes import talhoes_bp
from .estacoes import estacoes_bp
from .chuva import chuva_bp

__all__ = ["auth_bp", "fazendas_bp", "talhoes_bp", "estacoes_bp", "chuva_bp"]