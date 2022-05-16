import time
from concurrent import futures

import grpc
import os
import configparser

import gateway_comm_pb2_grpc
from gateway_comm_pb2 import Reply, Request
from gateway_comm_pb2_grpc import AuthenticateServicer
from authenticator import Authenticator

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))


class GatewayService(AuthenticateServicer):
    def Login(self, request, context):
        ip = request.ip
        password = request.password
        print(ip)
        return Reply(message="m", token="")

    def Register(self, request, context):
        pass

    def GetNodeForDownload(self, request, context):
        authenticator = Authenticator()
        is_valid_token("")  # token goes here
        pass

    def GetNodeForUpload(self, request, context):
        pass

    def ValidateToken(self, request, context):
        pass


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(".ini")
    prod_config = config["PROD"]
    server_port = prod_config["GATEWAY_SERVER_PORT"]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    gateway_comm_pb2_grpc.add_AuthenticateServicer_to_server(GatewayService(), server)
    server.add_insecure_port("[::]:" + server_port)
    print("Starting Gateway Server on port ", server_port, " ...")
    server.start()
    server.wait_for_termination()