from flask import Flask, jsonify, request, Response, Blueprint, render_template
from itsdangerous import Serializer
from ..models.UserModel import UserModel, UserSchema
from ..shared.Authentication import Auth, jwt
from ..config import os

user_api = Blueprint('users', __name__)

#returns list of all users
@user_api.route('/', methods=['GET'])
def get_all_users():
    users = UserModel.get_all()
    serializer = UserSchema(many=True)
    data = serializer.dump(users)
    return jsonify(data), 200

## get user by uuid
@user_api.route('/byuid', methods=['GET'])
def get_user():
    req = request.get_json()
    uid = req.get("uid")
    authenticate = Auth()
    authenticate.validate(request.headers, uid)
    
    user = UserModel.get_by_uid(uid)
    serializer = UserSchema()
    data = serializer.dump(user)
    return jsonify(data), 200

## add user in json format
@user_api.route('/', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = UserModel(data)
    new_user.save()
    serializer = UserSchema()
    user = serializer.dump(new_user)

    authenticate = Auth()
    token = authenticate.encode(user["uid"])

    return jsonify({'token': token, 'public key': os.getenv('BIZI_EC_PUBLIC_KEY')}), 201

## update user by passing uuid in URL and adding json for the rest
@user_api.route('/', methods=['PUT'])
def update_user():
    req = request.get_json()
    uid = req.get("uid_to_update")
    authenticate = Auth()
    authenticate.validate(request.headers, uid)

    user_to_update = UserModel.get_by_uid(uid)

    data = request.get_json()

    user_to_update.update(data)

    user_to_update.save()

    serializer = UserSchema()

    user_data = serializer.dump(user_to_update)

    return jsonify(user_data), 200

## delete user by supplying uuid
@user_api.route('/', methods=['DELETE'])
def delete_user(uid):
    req = request.get_json()
    uid = req.get("uid")
    authenticate = Auth()
    authenticate.validate(request.headers, uid)

    user_to_delete = UserModel.get_by_uid(uid)
    user_to_delete.delete()
    return jsonify({"message": "user deleted"}), 204

## debugging method to delete all users in database
@user_api.route('/deleteallusers', methods=['DELETE'])
def delete_all():
    Users = UserModel.get_all()
    for u in Users:
        u.delete()
    return jsonify({"message": "All users deleted"}), 204

## verifies user login info
@user_api.route('/authenticate', methods=['POST'])
def check_password():
    credentials = request.get_json()
    email = credentials.get("email")
    user = UserModel.get_by_email(email)
    if isinstance(user, type(None)):
        return jsonify({"message": "noemailfound"}), 403
    serializer = UserSchema()
    data = serializer.dump(user)
    if user.check_hash(credentials["password"]):
        authenticate = Auth()
        token = authenticate.encode(user.uid)
        return jsonify({'token': token, 'public key': os.getenv('BIZI_EC_PUBLIC_KEY')}), 201 
    return jsonify({"message": "nah"}), 403

@user_api.errorhandler(jwt.exceptions.PyJWTError)
def jwt_error(e):
    return jsonify({"message": "Not Authorized"}), 401
