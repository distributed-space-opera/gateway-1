import configparser
import os
from datetime import datetime
import bcrypt
import jwt
from jwt import InvalidSignatureError
from sqlalchemy import create_engine, MetaData, Table, Column, String, text
from passlib.hash import sha256_crypt

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))
prod_config = config["PROD"]
secret = prod_config["JWT_SECRET"]


# function to check if registered client is requesting using valid token
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
        if client_ip == decoded['ip'] and seconds < 3600:
            return True
        else:
            return False
    except InvalidSignatureError:
        return False


# Below logic will generate token for valid client using payload data
def generate_token(data):
    encoded = jwt.encode(data, "secret", algorithm="HS256")
    return encoded


# Below function will check if user trying to login is valid using password attribute
def is_valid_password(ip, password, requester):
    engine = create_engine(prod_config["SQLALCHEMY_DATABASE_URI"], echo=False)
    meta = MetaData()
    # Database details
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

    if requester == "NODE":
        query = text("SELECT * FROM node_details WHERE ip = :ip")
    else:
        query = text("SELECT * FROM client_details WHERE ip = :ip")

    conn = engine.connect()
    result = conn.execute(query, ip=ip)
    value = result.first()
    try:
        print("data found in database for node: ", ip, "having values: ", len(value))
        return decrypt(password, value[0])
    except:
        return False


# below code encrypt the password to avoid security attacks
def encrypt(password):
    encrypted_password = sha256_crypt.encrypt(password)
    return encrypted_password


# below code decrypts the encrypted password and check if there is match between user entered password and
# password stored in database.
def decrypt(password, ciphertext):
    matched = sha256_crypt.verify(password, ciphertext)
    return matched
