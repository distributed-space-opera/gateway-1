import configparser
import os
from datetime import datetime

import jwt
from jwt import InvalidSignatureError
from sqlalchemy import create_engine, MetaData, Table, Column, String, text

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))
prod_config = config["PROD"]
secret = prod_config["JWT_SECRET"]


def is_valid_token(token, client_ip):
    try:
        data = {
            "ip": client_ip,
            "requester": "NODE",
            "time": datetime.now()
        }
        decoded = jwt.decode(
                token,
                "secret",
                algorithms=["HS256"]
            )
        seconds = (datetime.now()-datetime.fromisoformat(decoded['time'])).seconds
        if client_ip == decoded['ip'] and seconds<3600:
            return True

        return False
    except InvalidSignatureError:
        return False


def generate_token(data):
    print("called here!")
    encoded = jwt.encode(data, "secret", algorithm="HS256")
    print("encoded token ",encoded)
    return encoded


def is_valid_password(ip, password, requester):
    config = configparser.ConfigParser()
    config.read(".ini")
    prod_config = config["PROD"]
    engine = create_engine(prod_config["SQLALCHEMY_DATABASE_URI"], echo=False)
    meta = MetaData()
    node_details = Table(
        'node_details', meta,
        Column('ip', String, primary_key=True),
        Column('password', String),
    )
    client_details = Table(
        'client_details', meta,
        Column('ip', String, primary_key=True),
        Column('password', String),
    )

    # query = None
    if requester == "NODE":
        query = text("SELECT * FROM node_details WHERE ip = :ip")
    else:
        query = text("SELECT * FROM client_details WHERE ip = :ip")
    conn = engine.connect()
    result = conn.execute(query, ip=ip)
    value = result.first()
    try:
        print(len(value))
        return value[0] == password

    except:
        return False


# TO DO
def encrypt(message, salt):
    pass


# TO DO
def decrypt(password, ciphertext, salt):
    pass
