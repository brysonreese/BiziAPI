from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://bizi:bizidevelopment@localhost/bizi'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    uid = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(255), nullable = False)
    password = db.Column(db.String(255), nullable = False)
    hid = db.Column(db.Integer())

    def __repr__(self):
        return "{}".format(self.name)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_uid(cls, uid_to_find):
        return cls.query.get_or_404(uid_to_find)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class UserSchema(Schema):
    uid = fields.Integer()
    name = fields.String()
    email = fields.Email()
    password = fields.String()
    hid = fields.Integer()

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.get_all()
    serializer = UserSchema(many=True)
    data = serializer.dump(users)
    return jsonify(data)


@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(
        name = data.get('name'),
        email = data.get('email'),
        password = data.get('password')
    )
    new_user.save()

    serializer = UserSchema()

    data = serializer.dump(new_user)

    return jsonify(data), 201

@app.route('/user/<int:uid>', methods=['GET'])
def get_user(uid):
    user = User.get_by_uid(uid)

    serializer = UserSchema()

    data = serializer.dump(user)

    return jsonify(data), 200

@app.route('/user/<int:uid>', methods=['PUT'])
def update_user(uid):
    user_to_update = User.get_by_uid(uid)

    data = request.get_json()

    user_to_update.name = data.get('name'),
    user_to_update.email = data.get('email'),
    user_to_update.password = data.get('password')

    user_to_update.save()

    serializer = UserSchema()

    user_data = serializer.dump(user_to_update)

    return jsonify(user_data), 200


@app.route('/user/<int:uid>', methods=['DELETE'])
def delete_user(uid):
    user_to_delete = User.get_by_uid(uid)
    user_to_delete.delete()

    return jsonify({"message": "user deleted"}), 204

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
