from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from Application.models import Fazenda, db

fazendas_bp = Blueprint('fazendas', __name__, url_prefix='/api/fazendas')

@fazendas_bp.route('', methods=['POST'])
@jwt_required()
def criar():
    data = request.get_json()
    fazenda = Fazenda(
        produtor_id=get_jwt_identity(),
        nome=data['nome'],
        area_hectares=data.get('area_hectares'),
        municipio=data.get('municipio'),
        uf=data.get('uf')
    )
    db.session.add(fazenda)
    db.session.commit()
    return jsonify(fazenda.to_dict()), 201

@fazendas_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    fazendas = Fazenda.query.filter_by(produtor_id=get_jwt_identity()).all()
    return jsonify([f.to_dict() for f in fazendas])

@fazendas_bp.route('/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def operacao(id):
    fazenda = Fazenda.query.filter_by(id=id, produtor_id=get_jwt_identity()).first_or_404()
    
    if request.method == 'GET':
        return jsonify(fazenda.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(fazenda)
        db.session.commit()
        return jsonify({"mensagem": "Fazenda excluída"})
    
    else:  
        data = request.get_json()
        fazenda.nome = data.get('nome', fazenda.nome)
        fazenda.area_hectares = data.get('area_hectares', fazenda.area_hectares)
        fazenda.municipio = data.get('municipio', fazenda.municipio)
        fazenda.uf = data.get('uf', fazenda.uf)
        db.session.commit()
        return jsonify(fazenda.to_dict())