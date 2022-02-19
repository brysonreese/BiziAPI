from flask import Flask, jsonify, request, Response, Blueprint
from ..models.UserModel import UserModel, UserSchema
from ..shared.Authentication import Auth
from ..config import os

user_api = Blueprint('users', __name__)

#returns list of all users
@user_api.route('/', methods=['GET'])
def get_all_users():
    users = UserModel.get_all()
    serializer = UserSchema(many=True)
    data = serializer.dump(users)
    return jsonify(data), 200

## add user in json format
@user_api.route('/', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = UserModel(data)
    new_user.save()

    authenticate = Auth()
    token = authenticate.encode(new_user.uid)

    return jsonify({'token': token, 'public key': os.getenv('BIZI_EC_PUBLIC_KEY')}), 201

## get user by uuid
@user_api.route('/<uuid:uid>', methods=['GET'])
def get_user(uid):
    authenticate = Auth()
    authenticate.validate(request.headers.get('Authorization'), uid)
    
    user = UserModel.get_by_uid(uid)
    serializer = UserSchema()
    data = serializer.dump(user)
    return jsonify(data), 200

## update user by passing uuid in URL and adding json for the rest
@user_api.route('/<uuid:uid>', methods=['PUT'])
def update_user(uid):
    user_to_update = UserModel.get_by_uid(uid)

    data = request.get_json()

    user_to_update.update(data)

    user_to_update.save()

    serializer = UserSchema()

    user_data = serializer.dump(user_to_update)

    return jsonify(user_data), 200

## delete user by supplying uuid
@user_api.route('/<uuid:uid>', methods=['DELETE'])
def delete_user(uid):
    user_to_delete = UserModel.get_by_uid(uid)
    user_to_delete.delete()
    return jsonify({"message": "user deleted"}), 204

##debugging method to delete all users in database
@user_api.route('/', methods=['DELETE'])
def delete_all():
    Users = UserModel.get_all()
    for u in Users:
        u.delete()
    return jsonify({"message": "All users deleted"}), 204

@user_api.route('/password/<uuid:uid>/<string:password>', methods=['GET'])
def check_password(uid, password):
    user = UserModel.get_by_uid(uid)
    if user.check_hash(password):
        return jsonify({"message": "verified"}) 
    return jsonify({"message": "nah"})

@user_api.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Resource not found"}), 404

@user_api.errorhandler(500)
def internal_server(error):
    return jsonify({"message": "There is a problem"}), 500