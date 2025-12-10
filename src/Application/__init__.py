from flask import Flask
from commons.configs import Config
from extensions import db, migrate, jwt

from routes.auth import auth_bp
from routes.fazendas import fazendas_bp
from routes.talhoes import talhoes_bp
from routes.chuva import chuva_bp
from routes.estacoes import estacoes_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  


    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/v.0/auth")
    app.register_blueprint(chuva_bp, url_prefix="/api/chuva_bp")
    app.register_blueprint(estacoes_bp, url_prefix="/v.0/estacoes_bp")
    app.register_blueprint(fazendas_bp, url_prefix="/v.0/fazendas_bp")
    app.register_blueprint(talhoes_bp, url_prefix="/v.0/talhoes_bp")

    @app.get("/")
    def health():
        return {"status": "ok", "message": "API Pingo Agro rodando!"}, 200

    return app