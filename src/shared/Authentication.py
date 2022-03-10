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
                          "exp": datetime.utcnow() + timedelta(days=7),
                          "jti": uuid.uuid4().hex}, private_key, algorithm="ES256")
    return encoded
  def validate(self, headers, uid):
    try:
      token = headers.get('Authorization').split()[1]
    except:
      raise jwt.exceptions.PyJWTError
    decoded = jwt.decode(token, os.getenv('BIZI_EC_PUBLIC_KEY'), algorithms=["ES256"])
    duid = uuid.UUID(decoded['sub']) #converts uid in token from hex back to its original form
    if (duid == uid):
      return decoded