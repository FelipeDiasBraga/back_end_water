from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from Application.models import Talhao, Fazenda, db


talhoes_bp = Blueprint('talhoes', __name__, url_prefix='/v.0/talhoes')


@talhoes_bp.route('/fazenda/<int:fazenda_id>', methods=['POST'])
@jwt_required()
def criar(fazenda_id):

    Fazenda.query.filter_by(id=fazenda_id, produtor_id=get_jwt_identity()).first_or_404()
    
    data = request.get_json()
    talhao = Talhao(
        fazenda_id=fazenda_id,
        nome=data['nome'],
        area_hectares=data.get('area_hectares'),
        geometry_wkt=data.get('geometry_wkt') 
    )
    db.session.add(talhao)
    db.session.add(talhao)
    db.session.commit()
    return jsonify(talhao.to_dict()), 201

@talhoes_bp.route('/fazenda/<int:fazenda_id>', methods=['GET'])
@jwt_required()
def listar_por_fazenda(fazenda_id):
    Fazenda.query.filter_by(id=fazenda_id, produtor_id=get_jwt_identity()).first_or_404()
    talhoes = Talhao.query.filter_by(fazenda_id=fazenda_id).all()
    return jsonify([t.to_dict() for t in talhoes])