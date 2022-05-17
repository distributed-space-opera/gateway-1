import time
from concurrent import futures

import grpc
import configparser

import gateway_comm_pb2_grpc
from gateway_comm_pb2 import Reply, Request, UploadResponse, DownloadResponse
from gateway_comm_pb2_grpc import AuthenticateServicer
from authenticator import is_valid_token, is_valid_password
from master_comm_pb2_grpc import ReplicationServicer
from master_comm_pb2 import GetNodeForDownloadRequest, GetNodeForUploadRequest


class GatewayService(AuthenticateServicer):

    def __init__(self):
        self.masterServicer = ReplicationServicer

    def Login(self, request, context):
        requester_type = request.type
        ip = request.ip
        password = request.password
        # print(request)
        if is_valid_password(ip, password, requester_type):
            # generate token
            pass
        else:
            pass
        return Reply(message="m", token="")

    def Register(self, request, context):
        pass

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