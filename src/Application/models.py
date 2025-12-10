from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db 


class BaseModel(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def save(self):
        """Salva o objeto no banco de dados"""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        """Remove o objeto do banco de dados"""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def get_by_id(cls, id):
        """Busca um objeto pelo ID"""
        return cls.query.get(id)


class Grupo(BaseModel):
    __tablename__ = "grupos"
    
    nome = db.Column(db.String(50), nullable=False, unique=True)
    descricao = db.Column(db.String(200))
    ativo = db.Column(db.Integer, default=1)
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class User(BaseModel):
    __tablename__ = "users"
    
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(11))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos.id'))
    ativo = db.Column(db.Integer, default=1)
    
    # Relacionamentos
    grupo = db.relationship("Grupo", backref="users")
    # produtor = db.relationship("Produtor", backref="user", uselist=False, cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        """Define a senha do usuário"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "email": self.email,
            "grupo_id": self.grupo_id,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def find_by_email(cls, email):
        """Busca usuário por email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_active_by_email(cls, email):
        """Busca usuário ativo por email"""
        return cls.query.filter_by(email=email, ativo=1).first()


class Produtor(BaseModel):
    __tablename__ = "produtores"
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(11))
    cpf_cnpj = db.Column(db.String(14), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    ativo = db.Column(db.Integer, default=1)
    
    # Relacionamentos
    fazendas = db.relationship("Fazenda", backref="produtor", lazy=True,
                              cascade="all, delete-orphan",
                              order_by="desc(Fazenda.created_at)")
    
    user = db.relationship("User", backref=db.backref("produtor", uselist=False))
                           
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "nome": self.nome,
            "telefone": self.telefone,
            "cpf_cnpj": self.cpf_cnpj,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def find_by_cpf_cnpj(cls, cpf_cnpj):
        """Busca produtor por CPF/CNPJ"""
        return cls.query.filter_by(cpf_cnpj=cpf_cnpj).first()


class Fazenda(BaseModel):
    __tablename__ = "fazendas"
    
    produtor_id = db.Column(db.Integer, db.ForeignKey('produtores.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    area_hectares = db.Column(db.Float)
    municipio = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2))
    ativo = db.Column(db.Integer, default=1)
    geometry = db.Column(Geometry("POLYGON", srid=4674))
    
    # Relacionamentos
    talhoes = db.relationship("Talhao", backref="fazenda", lazy=True,
                             cascade="all, delete-orphan",
                             order_by="desc(Talhao.created_at)")
    estacoes = db.relationship("EstacaoMeteorologica", backref="fazenda", lazy=True,
                              cascade="all, delete-orphan",
                              order_by="desc(EstacaoMeteorologica.created_at)")
    
    # Índices
    __table_args__ = (
        db.Index('idx_fazenda_produtor_ativo', 'produtor_id', 'ativo'),
        db.Index('idx_fazenda_municipio_uf', 'municipio', 'uf'),
    )
    
    def to_dict(self, include_geometry=False):
        """Converte para dicionário"""
        data = {
            "id": self.id,
            "produtor_id": self.produtor_id,
            "nome": self.nome,
            "area_hectares": self.area_hectares,
            "municipio": self.municipio,
            "uf": self.uf,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_geometry and self.geometry:
            try:
                from geoalchemy2.shape import to_shape
                shape = to_shape(self.geometry)
                data["geometry"] = shape.__geo_interface__
            except:
                data["geometry"] = None
        
        return data
    
    @classmethod
    def get_by_produtor(cls, produtor_id, ativo=1):
        """Busca fazendas de um produtor"""
        return cls.query.filter_by(produtor_id=produtor_id, ativo=ativo).all()


class Talhao(BaseModel):
    __tablename__ = "talhoes"
    
    fazenda_id = db.Column(db.Integer, db.ForeignKey('fazendas.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    area_hectares = db.Column(db.Float)
    geometry = db.Column(Geometry("POLYGON", srid=4674))
    ativo = db.Column(db.Integer, default=1)
    
    # Índices
    __table_args__ = (
        db.Index('idx_talhao_fazenda_ativo', 'fazenda_id', 'ativo'),
    )
    
    def to_dict(self, include_geometry=False):
        """Converte para dicionário"""
        data = {
            "id": self.id,
            "fazenda_id": self.fazenda_id,
            "nome": self.nome,
            "area_hectares": self.area_hectares,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_geometry and self.geometry:
            try:
                from geoalchemy2.shape import to_shape
                shape = to_shape(self.geometry)
                data["geometry"] = shape.__geo_interface__
            except:
                data["geometry"] = None
        
        return data
    
    @classmethod
    def get_by_fazenda(cls, fazenda_id, ativo=1):
        """Busca talhões de uma fazenda"""
        return cls.query.filter_by(fazenda_id=fazenda_id, ativo=ativo).all()


class EstacaoMeteorologica(BaseModel):
    __tablename__ = "estacoes_meteorologicas"
    
    fazenda_id = db.Column(db.Integer, db.ForeignKey('fazendas.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    geometry = db.Column(Geometry("POINT", srid=4674))
    ativo = db.Column(db.Integer, default=1)
    
    # Relacionamentos
    dados_chuva = db.relationship("DadoChuva", backref="estacao", lazy=True,
                                 cascade="all, delete-orphan",
                                 order_by="desc(DadoChuva.data_hora)")
    
    # Índices
    __table_args__ = (
        db.Index('idx_estacao_fazenda_ativo', 'fazenda_id', 'ativo'),
        db.Index('idx_estacao_uuid', 'uuid'),
    )
    
    def to_dict(self, include_geometry=False):
        """Converte para dicionário"""
        data = {
            "id": self.id,
            "fazenda_id": self.fazenda_id,
            "nome": self.nome,
            "uuid": self.uuid,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_geometry and self.geometry:
            try:
                from geoalchemy2.shape import to_shape
                shape = to_shape(self.geometry)
                data["geometry"] = shape.__geo_interface__
            except:
                data["geometry"] = None
        
        return data
    
    @classmethod
    def get_by_fazenda(cls, fazenda_id, ativo=1):
        """Busca estações de uma fazenda"""
        return cls.query.filter_by(fazenda_id=fazenda_id, ativo=ativo).all()
    
    @classmethod
    def find_by_uuid(cls, uuid):
        """Busca estação por UUID"""
        return cls.query.filter_by(uuid=uuid).first()


class DadoChuva(BaseModel):
    __tablename__ = "dados_chuva"
    
    estacao_id = db.Column(db.Integer, db.ForeignKey('estacoes_meteorologicas.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, index=True)
    precipitacao_mm = db.Column(db.Float, nullable=False)
    temperatura = db.Column(db.Float)           # ºC
    umidade = db.Column(db.Float)               # %
    pressao = db.Column(db.Float)               # hPa
    velocidade_vento = db.Column(db.Float)      # m/s
    direcao_vento = db.Column(db.Float)         # graus (0-360)
    fonte = db.Column(db.String(20), default="estacao_propria")  # estacao_propria | inmet | satelite
    
    # Índices compostos para performance
    __table_args__ = (
        db.Index('idx_dado_chuva_estacao_data_desc', 'estacao_id', db.desc('data_hora')),
        db.Index('idx_dado_chuva_estacao_data', 'estacao_id', 'data_hora'),
        db.Index('idx_dado_chuva_data_hora', 'data_hora'),
    )
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            "id": self.id,
            "estacao_id": self.estacao_id,
            "data_hora": self.data_hora.isoformat(),
            "precipitacao_mm": self.precipitacao_mm,
            "temperatura": self.temperatura,
            "umidade": self.umidade,
            "pressao": self.pressao,
            "velocidade_vento": self.velocidade_vento,
            "direcao_vento": self.direcao_vento,
            "fonte": self.fonte,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def get_by_estacao(cls, estacao_id, start_date=None, end_date=None):
        """Busca dados de chuva de uma estação com filtro de data"""
        query = cls.query.filter_by(estacao_id=estacao_id)
        
        if start_date:
            query = query.filter(cls.data_hora >= start_date)
        
        if end_date:
            query = query.filter(cls.data_hora <= end_date)
        
        return query.order_by(cls.data_hora).all()
    
    @classmethod
    def get_by_periodo(cls, start_date, end_date, estacao_ids=None):
        """Busca dados de chuva por período e estações específicas"""
        query = cls.query.filter(cls.data_hora.between(start_date, end_date))
        
        if estacao_ids:
            query = query.filter(cls.estacao_id.in_(estacao_ids))
        
        return query.order_by(cls.estacao_id, cls.data_hora).all()