import configparser
import re
from concurrent import futures
import time
import grpc
import sqlalchemy
from sqlalchemy import Table, Column, String, create_engine, MetaData
import gateway_comm_pb2_grpc
from authenticator import is_valid_token, is_valid_password, generate_token
from gateway_comm_pb2 import Reply, UploadResponse, DownloadResponse, ValidateTokenResponse
from gateway_comm_pb2_grpc import AuthenticateServicer
from master_comm_pb2 import GetNodeForDownloadRequest, GetNodeForUploadRequest
from master_comm_pb2_grpc import ReplicationServicer


def validate_ip_address(address):
    match = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", address)
    if bool(match) is False:
        return False
    for part in address.split("."):
        if int(part) < 0 or int(part) > 255:
            return False
    return True


def register(request, meta, engine, secret):
    prefix = "node"
    if request.type == "CLIENT":
        prefix = "client"
    table = Table(
        prefix + '_details', meta,
        Column('ip', String, primary_key=True),
        Column('password', String),
    )
    query = table.select().where(table.c.ip == request.ip)
    conn = engine.connect()
    result = conn.execute(query)
    if result.first() is not None:
        return Reply(masterip=None, message="Client/Node already registered", token=None)
    query = sqlalchemy.insert(table).values(ip=request.ip, password=request.password)
    result = conn.execute(query)
    if result is not None:
        token = generate_token({
                "ip": request.ip,
                "requester": request.type,
                "time": time.time()
            })
        return Reply(masterip=config["MASTER_NODE_IP"], message="Client/Node successfully registered", token=token)
    return Reply(masterip=None, message="Client/Node failed to register", token=None)


class GatewayService(AuthenticateServicer):

    def __init__(self):
        self.masterServicer = ReplicationServicer

    def Login(self, request, context):
        requester_type = request.type
        ip = request.ip
        password = request.password
        # print(request)
        if is_valid_password(ip, password, requester_type):
            token = generate_token({
                    "ip": ip,
                    "requester": requester_type,
                    "time": time.time()
                })
            return Reply(master_ip=config["MASTER_NODE_IP"], message="SUCCESS", token=token)
        else:
            return Reply(master_ip=None, message="ERROR", token="")

    def Register(self, request, context):
        if not validate_ip_address(request.ip):
            return Reply(master_ip=None, message="Invalid ip address. Please enter IPV4 address", token=None)
        if len(request.password) < 6 or len(request.password) > 20:
            return Reply(master_ip=None, message="Invalid password length. Length must be between 6 to 20", token=None)
        if request.type != "CLIENT" and request.type != "NODE":
            return Reply(master_ip=None, message="Type must be CLIENT/NODE", token=None)
        config = configparser.ConfigParser()
        config.read(".ini")
        prod_config = config["PROD"]
        engine = create_engine(prod_config["SQLALCHEMY_DATABASE_URI"], echo=False)
        meta = MetaData()
        return register(request, meta, engine, prod_config["JWT_SECRET"])

    def GetNodeForDownload(self, request, context):
        if is_valid_token(request.token, request.client_ip):  # token goes here
            if request.filename:
                print("getting Node IP where file is stored")
                request_ip = GetNodeForDownloadRequest(request.filename)
                node_ip = self.masterServicer.GetNodeForDownload(request_ip)
                if node_ip:
                    return DownloadResponse(nodeip=node_ip, message="SUCCESS")
                else:
                    return DownloadResponse(nodeip=None, message="ERROR")
            else:
                return DownloadResponse(nodeip=None, message="ERROR")
        pass

    def GetNodeForUpload(self, request, context):
        if is_valid_token(request.token, request.client_ip):  # token goes here
            if request.filename:
                print("calling Master Node to get Node IP")
                request_ip = GetNodeForUploadRequest(request.filename, request.filesize)
                node_ip = self.masterServicer.GetNodeForUpload(request_ip)
                if node_ip:
                    return UploadResponse(nodeip=node_ip, message="SUCCESS")
                else:
                    return UploadResponse(nodeip=None, message="ERROR")
            else:
                return UploadResponse(nodeip=None, message="ERROR")
        pass

    def ValidateToken(self, request, context):
        if is_valid_token(request.token, request.client_ip):
            return ValidateTokenResponse(message="VALID")
        else:
            return ValidateTokenResponse(message="INVALID")
        pass


if __name__ == "__main__":
    conf = configparser.ConfigParser()
    conf.read(".ini")
    config = conf["PROD"]
    server_port = config["GATEWAY_SERVER_PORT"]

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    gateway_comm_pb2_grpc.add_AuthenticateServicer_to_server(GatewayService(), server)
    server.add_insecure_port("[::]:" + server_port)
    print("Starting Gateway Server on port ", server_port, " ...")

    server.start()
    server.wait_for_termination()
