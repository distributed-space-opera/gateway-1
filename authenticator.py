import time
import jwt
import configparser
import os
from sqlalchemy import create_engine, MetaData, Table, Column, String
from jwt import InvalidSignatureError


def is_valid_token(token):
    try:
        data = {
            "ip": "10.0.0.1",
            "requester": "NODE",
            "time": time.time()
        }
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


def is_valid_password(requestor_type="CLIENT"):
    return False

