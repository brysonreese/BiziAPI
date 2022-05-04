from flask import Flask, jsonify, request, Response, Blueprint, json
from sqlalchemy import null
import sqlalchemy
from ..models.HouseholdModel import HouseholdModel, HouseholdSchema
from ..models.UserModel import UserModel, UserSchema
from ..shared.Authentication import Auth
from ..config import os
import uuid


household_api = Blueprint('household', __name__)

@household_api.route('/', methods=['GET'])
def get_all_households():
    households = HouseholdModel.get_all()
    serializer = HouseholdSchema(many=True)
    data = serializer.dump(households)
    return jsonify(data)

@household_api.route('/<uuid:hid>', methods=["GET"])
def get_household(hid):
    household = HouseholdModel.get_by_hid(hid)
    serializer = HouseholdSchema()
    data = serializer.dump(household)
    return jsonify(data)

@household_api.route('/names/<uuid:hid>', methods=["GET"])
def get_names(hid):
    household = HouseholdModel.get_by_hid(hid)
    members = household.members
    members_names = []
    for m in members:
        mem = UserModel.get_by_uid(m)
        members_names.append(mem.name)
    return jsonify(members_names)

@household_api.route('/notes/<uuid:hid>', methods=["GET"])
def get_notes(hid):
    household = HouseholdModel.get_by_hid(hid)
    return jsonify(household.notes), 200

@household_api.route('/notes/<uuid:hid>', methods=["POST"])
def post_notes(hid): 
    data = request.get_json()
    household = HouseholdModel.get_by_hid(hid)
    notes = data["notes"]
    for n in notes:
        n["id"] = str(uuid.uuid4())
        household.add_notes(n)
    
    household.save()
    return {"message": "Notes added"}

@household_api.route('/notes/edit/<uuid:hid>', methods=["PUT"])
def update_note(hid):
    data = request.get_json()
    household = HouseholdModel.get_by_hid(hid)
    notes = household.notes
    success = False
    print(data)
    for note in notes:
        if note["id"] == data["id"]:
            temp_id = note["id"]
            temp_title = note["title"]
            household.delete_note(note)
            new_note = {}
            new_note_content = {"id": "{}".format(temp_id), "title": "{}".format(temp_title), "content": "{}".format(data["content"])}
            new_note["notes"] = new_note_content
            household.add_notes(new_note_content)
            household.save()
            success = True
            break
    
    if success:
        return {"message": "note updated"}

    return {"message": "something went wrong when updating that note"}

@household_api.route('/notes/<uuid:hid>', methods=["PUT"])
def delete_note(hid):
    data = request.get_json()
    household = HouseholdModel.get_by_hid(hid)
    notes = household.notes
    note_to_delete = ""
    for note in notes:
        if note["id"] == data["id"]:
            note_to_delete = note
            break
    if note_to_delete:
        household.delete_note(note_to_delete)
        household.save()
        return {"message": "note deleted"}, 200
    
    return {"message": "note not found"}, 404

@household_api.route('/tasks/<uuid:hid>', methods=["GET"])
def get_tasks(hid):
    household = HouseholdModel.get_by_hid(hid)
    if not household.tasks:
        household.tasks = []
    print(household.tasks)
    return jsonify(household.tasks), 200

@household_api.route('/tasks/<uuid:hid>', methods=["POST"])
def add_tasks(hid): 
    data = request.get_json()
    print(data)
    household = HouseholdModel.get_by_hid(hid)
    for n in data["tasks"]:
        n["id"] = str(uuid.uuid4())
        household.add_task(n)
    
    household.save()
    return {"message": "Task added"}

@household_api.route('/tasks/<uuid:hid>', methods=["PUT"])
def delete_task(hid):
    data = request.get_json()
    household = HouseholdModel.get_by_hid(hid)
    tasks = household.tasks
    task_to_delete = ""
    for task in tasks:
        if task["id"] == data["id"]:
            task_to_delete = task
            break
    if task_to_delete:
        household.delete_task(task_to_delete)
        household.save()
        return {"message": "task deleted"}, 200
    
    return {"message": "task not found"}, 404

@household_api.route('/bills/<uuid:hid>', methods=["GET"])
def get_bills(hid):
    household = HouseholdModel.get_by_hid(hid)
    if not household.bills:
        household.bills = []
    print(household.bills)
    return jsonify(household.bills), 200

@household_api.route('/bills/<uuid:hid>', methods=["POST"])
def add_bills(hid): 
    data = request.get_json()
    print(data)
    household = HouseholdModel.get_by_hid(hid)
    for b in data["bills"]:
        b["id"] = str(uuid.uuid4())
        household.add_bill(b)
    
    household.save()
    return {"message": "Bills added"}

@household_api.route('/bills/<uuid:hid>', methods=["PUT"])
def delete_bill(hid):
    data = request.get_json()
    household = HouseholdModel.get_by_hid(hid)
    bills = household.bills
    bill_to_delete = ""
    for bill in bills:
        if bill["id"] == data["id"]:
            bill_to_delete = bill
            break
    if bill_to_delete:
        household.delete_bill(bill_to_delete)
        household.save()
        return {"message": "bill deleted"}, 200
    
    return {"message": "bill not found"}, 404

@household_api.route('/', methods=["POST"])
def add_household():
    data = request.get_json()
    new_household = HouseholdModel(data)
    new_household.save()
    hid = new_household.hid
    if (len(data["members"])):
        serializer = UserSchema()
        for u in data["members"]: 
            user = UserModel.get_by_email(u)
            if user and user.is_verified:
                uid = serializer.dump(user)['uid']
                new_household.add_user(uid)
                user.set_user_hid(hid)

    serializer = HouseholdSchema()
    data_serialized = serializer.dump(new_household)
    new_household.save()

    return jsonify(data_serialized), 201

@household_api.route('/<uuid:hid>', methods=["PUT"])
def update_household(hid):
    household_to_update = HouseholdModel.get_by_hid(hid)
    data = request.get_json()
    household_to_update.update_household(data)
    household_to_update.save()
    serializer = HouseholdSchema()
    household_data = serializer.dump(data)
    return jsonify(household_data)

@household_api.route('/<uuid:hid>/<uuid:uid>', methods=["PUT"])
def add_user_to_household(hid, uid):
    household_to_add_to = HouseholdModel.get_by_hid(hid)
    household_to_add_to.add_user(uid)
    household_to_add_to.save()
    return {"hid": hid}

@household_api.route('/<uuid:uid>', methods=["DELETE"])
def delete_household(hid):
    household_to_delete = HouseholdModel.get_by_hid(hid)
    household_to_delete.delete()

    return {"message": "household deleted"}

##debugging method to delete all households in database
@household_api.route('/deleteallhouseholds', methods=['DELETE'])
def delete_all():
    households = HouseholdModel.get_all()
    for h in households:
        h.delete()
    return {"message": "All households deleted"}, 204

@household_api.route('/<uuid:hid>/<uuid:uid>', methods=["DELETE"])
def delete_user_from_household(hid, uid):
    household_to_delete_from = HouseholdModel.get_by_hid(hid)
    user_to_delete = UserModel.get_by_uid(uid)
    ##try:
    household_to_delete_from.delete_user(str(uid))
    household_to_delete_from.save()
    user_to_delete.hid = sqlalchemy.null()
    user_to_delete.save()
    ##except:
        ##return {"message": "resource not found"}, 400

    return {"message": "user deleted"}

@household_api.errorhandler(404)
def not_found(error):
    return {"message": "Resource not found"}, 404

@household_api.errorhandler(500)
def internal_server(error):
    return {"message": "There is a problem"}, 500