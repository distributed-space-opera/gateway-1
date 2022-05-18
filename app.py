import configparser
import re
from concurrent import futures
from datetime import datetime
import grpc
import sqlalchemy
from sqlalchemy import Table, Column, String, create_engine, MetaData
import gateway_comm_pb2_grpc
from authenticator import is_valid_token, is_valid_password, generate_token, encrypt, decrypt
from gateway_comm_pb2 import Reply, UploadResponse, DownloadResponse, ValidateTokenResponse
from gateway_comm_pb2_grpc import AuthenticateServicer
from master_comm_pb2 import GetNodeForDownloadRequest, GetNodeForUploadRequest, NewNodeUpdateRequest
from master_comm_pb2_grpc import ReplicationServicer, ReplicationStub


class Master:
    def __init__(self, master_ip):
        self.channel = grpc.insecure_channel(master_ip)
        self.master_stub = ReplicationStub(self.channel)

# This function block will validate IP address format of node requesting to connect
def validate_ip_address(address):
    match = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", address)
    if bool(match) is False:
        return False
    for part in address.split("."):
        if int(part) < 0 or int(part) > 255:
            return False
    return True


# register function will add user details to database and notify master node if new node is added to network
def register(request, meta, engine, master):
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
        return Reply(masterip=None, message="ERROR", token=None)
    query = sqlalchemy.insert(table).values(ip=request.ip, password=encrypt(request.password))
    result = conn.execute(query)
    print(result)
    if result is not None:
        # Call master node and register new node
        if prefix == "node":
            request_ip = NewNodeUpdateRequest(newnodeip=request.ip)
            response = master.master_stub.NewNodeUpdate(request_ip)
            if response.status == "FAILURE":
                return Reply(masterip=None, message="ERROR", token=None)
            token = generate_token({
                    "ip": request.ip,
                    "requester": request.type,
                    "time": datetime.now().isoformat()
                })
            return Reply(masterip=config["MASTER_NODE_IP"], message="SUCCESS", token=token)
        else:
            token = generate_token({
                "ip": request.ip,
                "requester": request.type,
                "time": datetime.now().isoformat()
            })
            return Reply(masterip=None, message="SUCCESS", token=token)
    return Reply(masterip=None, message="ERROR", token=None)


# A GatewayService Class which will provide a platform to communicate with internal network
class GatewayService(AuthenticateServicer):

    def __init__(self):
        self.master = Master(config["MASTER_NODE_IP"])

    # Login function will authenticate and authorize user trying to access network
    def Login(self, request, context):
        """
        Entry check to internal network
        Endpoint for Client node
        """
        # client_ip = context.peer() # get client IP
        requester_type = request.type
        ip = request.ip
        password = request.password
        if is_valid_password(ip, password, requester_type):
            token = generate_token({
                "ip": ip,
                "requester": requester_type,
                "time": datetime.now().isoformat()
            })
            return Reply(masterip=config["MASTER_NODE_IP"], message="SUCCESS", token=token)
        else:
            return Reply(masterip=None, message="ERROR", token="")

    def Register(self, request, context):
        """
        Registering to access the network to take responsibilities or access features
        Endpoint for Client and node
        """
        # client_ip = context.peer()   # get client IP
        print(request, context.peer())
        # if not validate_ip_address(request.ip):
        #     print("ip not validated!")
        #     return Reply(master_ip=None, message="Invalid ip address. Please enter IPV4 address", token=None)
        # if len(request.password) < 6 or len(request.password) > 20:
        #     return Reply(master_ip=None, message="Invalid password length. Length must be between 6 to 20", token=None)
        if request.type != "CLIENT" and request.type != "NODE":
            return Reply(master_ip=None, message="Type must be CLIENT/NODE", token=None)
        config = configparser.ConfigParser()
        config.read(".ini")
        prod_config = config["PROD"]
        engine = create_engine(prod_config["SQLALCHEMY_DATABASE_URI"], echo=False)
        meta = MetaData()
        print("register")
        return register(request, meta, engine, self.master)

    def GetNodeForDownload(self, request, context):
        """
        A middle layer to authenticate client and restrict client to access whole network to download file
        Endpoint for Client
        """
        if is_valid_token(request.token, request.client_ip):
            if request.filename:
                print("getting Node IP where file is stored")
                master = Master(config["MASTER_NODE_IP"])
                request_ip = GetNodeForDownloadRequest(filename=request.filename)
                response = self.master.masterStub.GetNodeForDownload(request_ip)
                if response:
                    return DownloadResponse(nodeip=response.nodeip, message="SUCCESS")
                else:
                    return DownloadResponse(nodeip=None, message="ERROR")
            else:
                return DownloadResponse(nodeip=None, message="ERROR")
        pass

    def GetNodeForUpload(self, request, context):
        """
        A middle layer to authenticate client and restrict client to access whole network to upload a file
        Endpoint for Client
        """
        if is_valid_token(request.token, request.client_ip):  # token goes here
            if request.filename:
                print("calling Master Node to get Node IP")
                request_ip = GetNodeForUploadRequest(filename=request.filename, filesize=request.filesize)
                response = self.master.master_stub.GetNodeForUpload(request_ip)
                print("response ", response)
                if response:
                    print("called response ", response)
                    return UploadResponse(nodeip=response.nodeip, message="SUCCESS")
                else:
                    return UploadResponse(nodeip=None, message="ERROR")
            else:
                return UploadResponse(nodeip=None, message="ERROR")
        pass

    def ValidateToken(self, request, context):
        """
        Endpoint to validate the token which is proof of authenticity of the client
        """
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
