# app/routes/chuva.py
from flask import Blueprint, request, jsonify
from Application.models import EstacaoMeteorologica, DadoChuva, db
from datetime import datetime

chuva_bp = Blueprint('chuva', __name__, url_prefix='/v.0/chuva')

# Rota pública — a estação física chama com UUID no header
@chuva_bp.route('/ingest', methods=['POST'])
def ingest():
    auth_uuid = request.headers.get('X-Station-UUID')
    if not auth_uuid:
        return jsonify({"erro": "UUID da estação ausente"}), 401

    estacao = EstacaoMeteorologica.query.filter_by(uuid=auth_uuid, ativo=True).first()
    if not estacao:
        return jsonify({"erro": "Estação não autorizada"}), 401

    data = request.get_json()
    dado = DadoChuva(
        estacao_id=estacao.id,
        data_hora=datetime.fromisoformat(data['data_hora']),
        precipitacao_mm=data['precipitacao_mm'],
        fonte="estacao_propria"
    )
    db.session.add(dado)
    db.session.commit()
    return jsonify({"status": "ok"}), 201