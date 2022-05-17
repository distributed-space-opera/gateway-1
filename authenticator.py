import configparser
import os
import time

import jwt
from jwt import InvalidSignatureError
from sqlalchemy import create_engine, MetaData, Table, Column, String, text

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))
prod_config = config["PROD"]
# private_key = prod_config["PRIVATE_KEY"]
# public_key = prod_config["PUBLIC_KEY"]
secret = prod_config["JWT_SECRET"]


def is_valid_token(token, client_ip):
    try:
        data = {
            "ip": client_ip,
            "requester": "NODE",
            "time": time.time()
        }
        decoded = jwt.decode(
                token,
                "secret",
                algorithms=["HS256"]
            )
        print("decoded: ", decoded)
        return True
    except InvalidSignatureError:
        return False


def generate_token(data):
    encoded = jwt.encode(data, "secret", algorithm="HS256")
    return encoded


def is_valid_password(ip, password, requester):
    # config = configparser.ConfigParser()
    # config.read(os.path.abspath(os.path.join(".ini")))
    # db_uri = config["PROD"]["SQLALCHEMY_DATABASE_URI"]
    # print(db_uri)

    config = configparser.ConfigParser()
    config.read(".ini")
    prod_config = config["PROD"]
    engine = create_engine(prod_config["SQLALCHEMY_DATABASE_URI"], echo=False)
    meta = MetaData()
    #
    # engine = create_engine(config[db_uri], echo=False)
    # meta = MetaData()
    # print(engine)
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
    #     query = node_details.select().where(node_details.c.node_ip == ip)
    else:
        query = text("SELECT * FROM client_details WHERE ip = :ip")
    #     query = node_details.select().where(client_details.c.client_ip == ip)
    conn = engine.connect()
    result = conn.execute(query, ip=ip)
    value = result.first()
    try:
        print(len(value))
        return value[0] == password
        # return False
    except:
        return False
        # print(result.first()[0], password)
        # return result.first()[0] == password


# TO DO
def encrypt(message, salt):
    pass


# TO DO
def decrypt(password, ciphertext, salt):
    pass
