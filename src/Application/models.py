from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db



class Produtor(db.Model):
    __tablename__ = "produtor"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(11))
    cpf_cnpj = db.Column(db.String(14), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    fazendas = db.relationship("Fazenda", backref="produtor", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "cpf_cnpj": self.cpf_cnpj,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Fazenda(db.Model):
    __tablename__ = "fazenda"

    id = db.Column(db.Integer, primary_key=True)
    produtor_id = db.Column(db.Integer, db.ForeignKey("produtor.id"), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    area_hectares = db.Column(db.Float)
    municipio = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # soft delete 
    ativo = db.Column(db.Integer, default=1)

    talhoes = db.relationship("Talhao", backref="fazenda", lazy=True, cascade="all, delete-orphan")
    estacoes = db.relationship("EstacaoMeteorologica", backref="fazenda", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "area_hectares": self.area_hectares,
            "municipio": self.municipio,
            "uf": self.uf,
            "produtor_id": self.produtor_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Talhao(db.Model):
    __tablename__ = "talhao"

    id = db.Column(db.Integer, primary_key=True)
    fazenda_id = db.Column(db.Integer, db.ForeignKey("fazenda.id"), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    area_hectares = db.Column(db.Float)
    ativo = db.Column(db.Integer, default=1)
    geometry = db.Column(Geometry("POLYGON", srid=4674))  

    def to_dict(self, include_geometry=False):
        data = {
            "id": self.id,
            "nome": self.nome,
            "area_hectares": self.area_hectares,
            "fazenda_id": self.fazenda_id,
        }
        if include_geometry and self.geometry:
            from geoalchemy2.shape import to_shape
            shape = to_shape(self.geometry)
            data["geometry"] = shape.__geo_interface__
        return data


class EstacaoMeteorologica(db.Model):
    __tablename__ = "estacao_meteorologica"

    id = db.Column(db.Integer, primary_key=True)
    
    fazenda_id = db.Column(db.Integer, db.ForeignKey("fazenda.id"), nullable=False)
    
    nome = db.Column(db.String(100), nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False)  # UUID físico da estação
    geometry = db.Column(Geometry("POINT", srid=4674))  # latitude/longitude
    ativo = db.Column(db.Integer, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento
    dados_chuva = db.relationship("DadoChuva", backref="estacao", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_geometry=False):
        data = {
            "id": self.id,
            "nome": self.nome,
            "uuid": self.uuid,
            "ativo": self.ativo,
            "fazenda_id": self.fazenda_id,
        }
        if include_geometry and self.geometry:
            from geoalchemy2.shape import to_shape
            shape = to_shape(self.geometry)
            data["geometry"] = shape.__geo_interface__
        return data


class DadoChuva(db.Model):
    __tablename__ = "dado_chuva"

    id = db.Column(db.Integer, primary_key=True)
    estacao_id = db.Column(db.Integer, db.ForeignKey("estacao_meteorologica.id"), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, index=True)
    precipitacao_mm = db.Column(db.Float, nullable=False)
    fonte = db.Column(db.String(20), default="estacao_propria")  # estacao_propria | inmet | satelite
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "estacao_id": self.estacao_id,
            "data_hora": self.data_hora.isoformat(),
            "precipitacao_mm": self.precipitacao_mm,
            "fonte": self.fonte,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }