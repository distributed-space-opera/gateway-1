import configparser
import os
import time

import jwt
from jwt import InvalidSignatureError
from sqlalchemy import create_engine, MetaData, Table, Column, String

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))
prod_config = config["PROD"]
private_key = prod_config["PRIVATE_KEY"]
public_key = prod_config["PUBLIC_KEY"]
secret = prod_config["JWT_SECRET"]


def is_valid_token(token, client_ip):
    try:
        data = {
            "ip": client_ip,
            "requester": "NODE",
            "time": time.time()
        }
        jwt.decode(
            token,
            public_key,
            algorithms=["HS256"]
        )
        return True
    except InvalidSignatureError:
        return False


def generate_token(data):
    encoded = jwt.encode(data, private_key, algorithm="HS256")
    return encoded


def is_valid_password(ip, password, requester):
    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join(".ini")))
    db_uri = config["PROD"]["SQLALCHEMY_DATABASE_URI"]
    print(db_uri)

    engine = create_engine(config[db_uri], echo=False)
    meta = MetaData()
    print(engine)
    node_details = Table(
        'node_details', meta,
        Column('node_ip', String, primary_key=True),
        Column('password', String),
    )
    client_details = Table(
        'client_details', meta,
        Column('client_ip', String, primary_key=True),
        Column('password', String),
    )

    query = None
    if requester == "NODE":
        query = node_details.select().where(node_details.c.node_ip == ip)
    else:
        query = node_details.select().where(client_details.c.client_ip == ip)
    conn = engine.connect()
    result = conn.execute(query)

    return False


# TO DO
def encrypt(message, salt):
    pass


# TO DO
def decrypt(password, ciphertext, salt):
    pass
