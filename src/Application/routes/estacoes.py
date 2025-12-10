import uuid

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from Application.models import EstacaoMeteorologica, Fazenda, db

estacoes_bp = Blueprint('estacoes', __name__, url_prefix='/v.0/estacoes')

@estacoes_bp.route('/fazenda/<int:fazenda_id>', methods=['POST'])
@jwt_required()
def criar(fazenda_id):
    Fazenda.query.filter_by(id=fazenda_id, produtor_id=get_jwt_identity()).first_or_404()
    
    data = request.get_json()
    estacao = EstacaoMeteorologica(
        fazenda_id=fazenda_id,
        nome=data['nome'],
        uuid=str(uuid.uuid4()),  
        lat=data.get('lat'),
        lng=data.get('lng'),
        ativo=True
    )

    db.session.add(estacao)
    db.session.commit()

    return jsonify(estacao.__dict__), 201  


@estacoes_bp.route('/fazenda/<int:fazenda_id>', methods=['GET'])
@jwt_required()
def listar(fazenda_id):
    
    Fazenda.query.filter_by(id=fazenda_id, produtor_id=get_jwt_identity()).first_or_404()

    estacoes = EstacaoMeteorologica.query.filter_by(fazenda_id=fazenda_id).all()
    return jsonify([{
        "id": e.id,
        "nome": e.nome,
        "uuid": e.uuid,
        "lat": e.lat,
        "lng": e.lng,
        "ativo": e.ativo
    } for e in estacoes])