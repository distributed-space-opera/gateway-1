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


def generate_token(data):
    pass


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
