from marshmallow import Schema, fields
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from sqlalchemy.orm.attributes import flag_modified
from . import db

class HouseholdModel(db.Model):
    __tablename__ = 'households'

    hid = db.Column(UUID(as_uuid=True), primary_key = True, server_default = db.text("gen_random_uuid()"),)
    name = db.Column(db.String(255), nullable = False)
    members = db.Column(ARRAY(UUID(as_uuid=True)))
    notes = db.Column(ARRAY(JSON))

    def __init__(self, data):
        self.name = data.get('name')
        
    def __repr__(self):
        return "<name {}>".format(self.hid)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_hid(cls, hid_to_find):
        return cls.query.get_or_404(hid_to_find)
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update_household(self, data):
        for t in data.items():
            setattr(self, t[0], t[1])
        db.session.commit()
    
    def add_user(self, data):
        db.session.execute("UPDATE households SET members = members || '{}' WHERE hid = '{}'".format('{' + data[0] + '}', data[1]))
        db.session.commit() 

    def delete_user(self, data):
        db.session.execute("UPDATE households SET members = array_remove(members, '{}') WHERE hid = '{}'".format('{' + data[0] + '}', data[1]))
        db.session.commit()

class HouseholdSchema(Schema):
    hid = fields.UUID()
    name = fields.String()
    members = fields.UUID()
