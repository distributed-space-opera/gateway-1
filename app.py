from flask import Flask
import os
import configparser
import master_comm_pb2 as master_request

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


@app.route('/upload')
def uploadFile(filename, payload):
    print("redirection to master's node to get nodeIP where data needs to be stored")
    nodeIP = master_request.GetNodeForUploadRequest(filename)
    return nodeIP


@app.route('/download')
def downloadFile(filename):
    nodeIP = master_request.GetNodeForDownloadRequest(filename)
    print("redirection to master's node to fetch IP address where filename is present")


if __name__ == '__main__':
    app.run()

