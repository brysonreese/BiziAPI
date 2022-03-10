from flask import Flask, jsonify, request, Response, Blueprint, json
from ..models.HouseholdModel import HouseholdModel, HouseholdSchema
from ..models.UserModel import UserModel, UserSchema
from ..shared.Authentication import Auth
from ..config import os

household_api = Blueprint('household', __name__)

@household_api.route('/', methods=['GET'])
def get_all_households():
    households = HouseholdModel.get_all()
    serializer = HouseholdSchema(many=True)
    data = serializer.dump(households)
    return jsonify(data), 200

@household_api.route('/', methods=["GET"])
def get_household():
    req = request.get_json()
    hid = req.get("hid")
    household = HouseholdModel.get_by_hid(hid)
    serializer = HouseholdSchema()
    data = serializer.dump(household)
    return jsonify(data), 200

@household_api.route('/', methods=["POST"])
def add_household():
    data = request.get_json()
    new_household = HouseholdModel(data)
    new_household.save()
    if (len(data["members"])):
        for u in data["members"]: 
            user = UserModel.get_by_email(u)
            serializer = UserSchema()
            uid = serializer.dump(user)['uid']
            print(uid)
            new_household.add_user([str(uid), new_household.hid])

    serializer = HouseholdSchema()
    data_serialized = serializer.dump(new_household)
    new_household.save()

    return jsonify(data_serialized), 201

@household_api.route('/test', methods=["POST"])
def test_post():
    data = request.get_json
    HouseholdModel(data)

@household_api.route('/', methods=["PUT"])
def update_household():
    req = request.get_json()
    hid = req.get("hid")
    household_to_update = HouseholdModel.get_by_hid(hid)
    data = request.get_json()
    household_to_update.update_household(data)
    household_to_update.save()
    serializer = HouseholdSchema()
    household_data = serializer.dump(data)
    return jsonify(household_data), 200

@household_api.route('/', methods=["DELETE"])
def delete_household():
    req = request.get_json()
    hid = req.get("hid")
    household_to_delete = HouseholdModel.get_by_hid(hid)
    household_to_delete.delete()

    return jsonify({"message": "household deleted"})

##debugging method to delete all households in database
@household_api.route('/', methods=['DELETE'])
def delete_all():
    households = HouseholdModel.get_all()
    for h in households:
        h.delete()
    return jsonify({"message": "All households deleted"}), 204

@household_api.route('/<uuid:hid>/<uuid:uid>', methods=["PUT"])
def add_user_to_household(hid, uid):
    household_to_add_to = HouseholdModel.get_by_hid(hid)
    user_list= [str(uid), hid]
    household_to_add_to.add_user(user_list)

    return jsonify({"message": "user added"})

@household_api.route('/delete_households/<uuid:hid>/<uuid:uid>', methods=["DELETE"])
def delete_user_from_household(hid, uid):
    household_to_delete_from = HouseholdModel.get_by_hid(hid)
    user_list = [str(uid), hid]
    household_to_delete_from.delete_user(user_list)

    return jsonify({"message": "user deleted"})

@household_api.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Resource not found"}), 404

@household_api.errorhandler(500)
def internal_server(error):
    return jsonify({"message": "There is a problem"}), 500