# src/models/__init__.py

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit

# initialize our db
db = SQLAlchemy()

## initialize password hashing utility
bcrypt = Bcrypt()

## initialize or socket utility
socketio = SocketIO()