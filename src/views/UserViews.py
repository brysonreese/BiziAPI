from os import getenv
from flask import Flask, jsonify, request, Response, Blueprint, redirect, render_template, url_for
from ..models.UserModel import UserModel, UserSchema
from ..models import socketio, emit
from ..shared.Authentication import Auth, jwt
from itsdangerous import URLSafeTimedSerializer

user_api = Blueprint('users', __name__)

ts = URLSafeTimedSerializer('BD6A57DB5B9C6F7CFB214E0189CB2972')

#returns list of all users
@user_api.route('/', methods=['GET'])
def get_all_users():
    users = UserModel.get_all()
    serializer = UserSchema(many=True)
    data = serializer.dump(users)
    return jsonify(data)

## get user by uuid
@user_api.route('/<uuid:uid>', methods=['GET'])
def get_user(uid):
    authenticate = Auth()
    authenticate.validate(request.headers, uid)
    
    user = UserModel.get_by_uid(uid)
    serializer = UserSchema()
    data = serializer.dump(user)
    return jsonify(data)

## Sends user an email with a unique route identifier to verify they have an email and it belongs to them
@user_api.route('/', methods=['POST'])
def add_user():
    data = request.get_json()
    email = data.get("email")
    user = UserModel.get_by_email(email)
    if user:
        return {'message': 'Account already exists'}, 400

    new_user = UserModel(data)
    new_user.save()
    
    ##To do: create a better salt key
    token = ts.dumps(email.lower(), salt='email-confirm-key')
    confirm_url = url_for(
        'users.confirm_email',
        token=token,
        _external=True)
    html = render_template(
        'activate.html',
        confirm_url=confirm_url)
    UserModel.send_email(email, "Confirm your email", html)

    return {"message": "Email sent"}

## add user in json format
@user_api.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    try:
        email = ts.loads(token, salt='email-confirm-key', max_age=86400)
    except:
        return {'message': 'Expired'}, 404

    new_user = UserModel.get_by_email(email)
    new_user.verify_registration()
    return "You are now authenticated. Please login with your email and password from the Bizi homescreen.", 201

## verifies user login info
@user_api.route('/authenticate', methods=['POST'])
def check_password():
    credentials = request.get_json()
    email = credentials.get("email")
    user = UserModel.get_by_email(email)
    if not user:
        return {"message": "wrong credentials"}, 403
    if not user.is_verified:
        return {"message": "wrong credentials"}, 403
    if user.check_hash(credentials["password"]):
        authenticate = Auth()
        token = authenticate.encode(user.uid)
        return {'token': token}, 201 
    return {"message": "wrong credentials"}, 403

## update user by passing uuid in URL and adding json for the rest
@user_api.route('/', methods=['PUT'])
def update_user():
    data = request.get_json()
    uid = data["uid"]
    ##authenticate = Auth()
    ##authenticate.validate(request.headers, uid)

    user_to_update = UserModel.get_by_uid(uid)
    
    user_to_update.update(data)
    user_to_update.save()
    serializer = UserSchema()
    user_data = serializer.dump(user_to_update)
    return jsonify(user_data), 200

@user_api.route('/hid/<uuid:uid>', methods=['GET'])
def get_user_hid(uid):

    user = UserModel.get_by_uid(uid)
    return {"hid": user.hid}

## delete user by supplying uuid
@user_api.route('/<uuid:uid>', methods=['DELETE'])
def delete_user(uid):
    authenticate = Auth()
    authenticate.validate(request.headers, uid)

    user_to_delete = UserModel.get_by_uid(uid)
    user_to_delete.delete()
    return {"message": "user deleted"}, 204

## debugging method to delete all users in database
@user_api.route('/deleteallusers', methods=['DELETE'])
def delete_all():
    Users = UserModel.get_all()
    for u in Users:
        u.delete()
    return {"message": "All users deleted"}, 204

@socketio.event('/echo')
def echo(message):
    emit(message)

@user_api.errorhandler(jwt.exceptions.PyJWTError)
def jwt_error(e):
    return {"message": "Not Authorized"}, 401
