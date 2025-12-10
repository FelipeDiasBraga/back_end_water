# src/Application/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from decouple import config
import os

# Força o carregamento do .env na raiz do projeto
from pathlib import Path
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
if env_path.exists():
    from decouple import Config as DecoupleConfig, RepositoryEnv
    config = DecoupleConfig(RepositoryEnv(str(env_path)))

# Extensions (criadas fora da função para evitar recriação)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # === CONFIGURAÇÕES OBRIGATÓRIAS ===
    app.config['SECRET_KEY'] = config('SECRET_KEY', default='dev-secret-key-change-me')
    app.config['JWT_SECRET_KEY'] = config('JWT_SECRET_KEY', default='jwt-secret-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = config(
        'DATABASE_URL',
        default='sqlite:///instance/rain_app.db'  # fallback seguro
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa as extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Registra blueprints (crie as pastas routes/ se ainda não existirem)
    with app.app_context():
        from .routes.auth import auth_bp
        # from .routes.fazendas import fazendas_bp  # descomente quando criar
        app.register_blueprint(auth_bp)

    return app