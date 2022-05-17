import time
import jwt
import configparser
import os
from sqlalchemy import create_engine, MetaData, Table, Column, String

from jwt import InvalidSignatureError


def is_valid_token(token, client_ip):
    try:
        data = {
            "ip": client_ip,
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


def generate_token(data):
    pass


def is_valid_password(requestor_type="CLIENT"):
    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join(".ini")))
    db_uri = config["PROD"]

    engine = create_engine(config[db_uri], echo=True)
    meta = MetaData()

    node_details = Table(
        'node_details', meta,
        Column('node_ip', String, primary_key=True),
        Column('password', String),
    )
    query = node_details.select().where(node_details.c.node_ip == "")
    conn = engine.connect()
    result = conn.execute(query)

    return False
