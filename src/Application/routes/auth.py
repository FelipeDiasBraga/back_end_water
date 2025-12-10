from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from Application.models import Produtor, db
from Application.schemas.auth import RegisterSchema, LoginSchema, TokenResponse
from datetime import timedelta


auth_bp = Blueprint('auth', __name__, url_prefix='/v.0/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = RegisterSchema(**request.get_json())
    except Exception as e:
        return jsonify({"erro": [error["msg"] for error in e.errors()]}), 400

    if Produtor.query.filter_by(email=data.email).first():
        return jsonify({"erro": "E-mail já cadastrado"}), 409

    produtor = Produtor(
        nome=data.nome,
        email=data.email,
        telefone=data.telefone,
        cpf_cnpj=data.cpf_cnpj
    )
    produtor.set_password(data.password)

    db.session.add(produtor)
    db.session.commit()

    token = create_access_token(identity=produtor.id, expires_delta=timedelta(days=7))

    return jsonify(TokenResponse(
        access_token=token,
        produtor=produtor.to_dict()
    ).model_dump()), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = LoginSchema(**request.get_json())
    except Exception as e:
        return jsonify({"erro": [error["msg"] for error in e.errors()]}), 400

    produtor = Produtor.query.filter_by(email=data.email).first()

    if not produtor or not produtor.check_password(data.password):
        return jsonify({"erro": "Credenciais inválidas"}), 401

    token = create_access_token(identity=produtor.id, expires_delta=timedelta(days=7))

    return jsonify(TokenResponse(
        access_token=token,
        produtor=produtor.to_dict()
    ).model_dump())