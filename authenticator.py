import time
import jwt
import configparser
import os

from jwt import InvalidSignatureError


class Authenticator:
    def is_valid_token(self, token):
        try:
            config = configparser.ConfigParser()
            config.read(os.path.abspath(os.path.join(".ini")))
            prod_config = config["PROD"]
            secret = prod_config["JWT_SECRET"]
            jwt.decode(
                token,
                secret,
                algorithms=["HS256"]
            )
            return True
        except InvalidSignatureError:
            return False
        return False