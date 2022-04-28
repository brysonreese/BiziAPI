from marshmallow import Schema, fields
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from sqlalchemy.orm.attributes import flag_modified
from . import db
import uuid

class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()
    
    def remove(self, value):
        list.remove(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value

class HouseholdModel(db.Model):
    __tablename__ = 'households'

    hid = db.Column(UUID(as_uuid=True), primary_key = True, server_default = db.text("gen_random_uuid()"),)
    name = db.Column(db.String(255), nullable = False)
    members = db.Column(MutableList.as_mutable(ARRAY(UUID)))
    notes = db.Column(MutableList.as_mutable(ARRAY(JSON)))
    tasks = db.Column(MutableList.as_mutable(ARRAY(JSON)))
    bills = db.Column(MutableList.as_mutable(ARRAY(JSON)))

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
        if not self.members:
            self.members = []
        HouseholdModel.query.filter_by(hid=self.hid).one().members.append(data)
        db.session.commit()

    def delete_note(self, data):
        if not self.notes:
            self.notes = []
        HouseholdModel.query.filter_by(hid=self.hid).one().notes.remove(data)
    
    def add_notes(self, data):
        if not self.notes:
            self.notes = []
        HouseholdModel.query.filter_by(hid=self.hid).one().notes.append(data)

    def add_task(self, data):
        if not self.tasks:
            self.tasks = []
        HouseholdModel.query.filter_by(hid=self.hid).one().tasks.append(data)

    def delete_task(self, data):
        if not self.tasks:
            self.tasks = []
        HouseholdModel.query.filter_by(hid=self.hid).one().tasks.remove(data)

    def add_bill(self, data):
        if not self.bills:
            self.bills = []
        HouseholdModel.query.filter_by(hid=self.hid).one().bills.append(data)

    def delete_bill(self, data):
        if not self.bills:
            self.bills = []
        HouseholdModel.query.filter_by(hid=self.hid).one().bills.remove(data)

    def delete_user(self, data):
        HouseholdModel.query.filter_by(hid=self.hid).one().members.remove(data)
        db.session.commit()

class HouseholdSchema(Schema):
    hid = fields.UUID()
    name = fields.String()
    members = fields.UUID()