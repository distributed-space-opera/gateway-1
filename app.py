from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

import os
import configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))


@app.route('/')
def hello_world():  # put application's code here
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///' + os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return 'Hello World!'


if __name__ == '__main__':

    app.run()

