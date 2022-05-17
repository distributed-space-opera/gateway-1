import time
from concurrent import futures

import grpc
import configparser

import gateway_comm_pb2_grpc
from gateway_comm_pb2 import Reply, Request
from gateway_comm_pb2_grpc import AuthenticateServicer
from authenticator import is_valid_token, is_valid_password


class GatewayService(AuthenticateServicer):
    def Login(self, request, context):
        requester_type = request.type
        ip = request.ip
        password = request.password
        print(request)
        if is_valid_password(ip, password, requester_type):
            # generate token
            pass
        else:
            pass
        return Reply(message="m", token="")

    def Register(self, request, context):
        pass

    def GetNodeForDownload(self, request, context):
        is_valid_token("")  # token goes here
        pass

    def GetNodeForUpload(self, request, context):
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