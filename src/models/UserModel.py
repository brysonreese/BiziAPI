from pickle import FALSE, TRUE
from marshmallow import Schema, fields
from sqlalchemy.dialects.postgresql import UUID
from . import db
from ..app import bcrypt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os

## model for users, contains all basic user info
class UserModel(db.Model):
    __tablename__ = 'users'

    uid = db.Column(UUID(as_uuid=True), primary_key = True, server_default = db.text("gen_random_uuid()"),)
    name = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(255), nullable = False)
    password = db.Column(db.String(255), nullable = False)
    hid = db.Column(UUID(as_uuid=True))
    is_verified = db.Column(db.Boolean())
    venmo_link = db.Column(db.String(255))

    def __init__(self, data):
        self.name = data.get('name')
        self.email = data.get('email')
        self.password = self.__generate_hash(data.get('password'))
        self.is_verified = False

    def __repr__(self):
        return "<uid {}>".format(self.uid)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_uid(cls, uid_to_find):
        return cls.query.get_or_404(uid_to_find)

    @classmethod
    def get_by_email(cls, email_to_find):
        return cls.query.filter_by(email = email_to_find).first()

    @classmethod
    def send_email(cls, email, subject, html):

        sender_address = 'biziapplication@gmail.com'
        sender_pass = 'v92zqTeGkNiXM5J'
        message = MIMEMultipart('alternative')
        message['From'] = sender_address
        message['To'] = email
        message['Subject'] = subject
        message.attach(MIMEText(html, 'html'))
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls() 
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, email, text)
        session.quit()

    def set_user_hid(self, hid):
        self.hid = hid
        db.session.add(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def verify_registration(self):
        self.is_verified= True
        db.session.commit()

    def update(self, data):
        for t in data.items():
            if t[0] == 'password':
                self.password = self.__generate_hash(t[1])
            else:
                setattr(self, t[0], t[1])
        db.session.commit()

    def __generate_hash(self, password):
        return bcrypt.generate_password_hash(password, rounds=10).decode('utf-8')

    def check_hash(self, password):
        return bcrypt.check_password_hash(self.password, password)

## serializes all of the different pieces of our UserModel nicely
class UserSchema(Schema):
    uid = fields.UUID()
    name = fields.String()
    email = fields.Email()
    password = fields.String()
    hid = fields.UUID()