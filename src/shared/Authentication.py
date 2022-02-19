from lib2to3.pgen2.tokenize import TokenError
import jwt
from datetime import datetime
from datetime import timedelta
import uuid
from ..config import os


class Auth:
  def encode(self, uid):
    private_key = os.getenv('BIZI_EC_PRIVATE_KEY')
    encoded = jwt.encode({"iss": "Bizi",
                          "sub": uid.hex,
                          "iat": datetime.utcnow(),
                          "exp": datetime.utcnow() + timedelta(days=1),
                          "jti": uuid.uuid4().hex}, private_key, algorithm="ES256")
    return encoded
  def validate(self, token, uid):
    try:
      decoded = jwt.decode(token, os.getenv('BIZI_EC_PUBLIC_KEY'), algorithms=["ES256"])
      if (decoded['exp'] > datetime.utcnow() and decoded['sub'] == uid):
        return decoded
    except jwt.InvalidTokenError as exc:
      raise TokenError(str(exc))
