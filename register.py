import configparser
import os
from concurrent import futures

import grpc
from sqlalchemy import create_engine, MetaData, Table, Column, String

from gateway_comm_pb2 import Reply
from gateway_comm_pb2_grpc import AuthenticateServicer, add_AuthenticateServicer_to_server


class Listener(AuthenticateServicer):

    def Register(self, request, context):
        config = configparser.ConfigParser()
        config.read(os.path.abspath(os.path.join(".ini")))
        db_client = create_engine.connect(config['SQLALCHEMY_DATABASE_URI'])
        meta = MetaData()
        node_details = Table(
            'node_details   ', meta,
            Column('username', String, primary_key=True),
            Column('password', String),
        )
        node_ins_query = node_details.insert().values(username=request.username, password=request.password)
        result = db_client.execute(node_ins_query)
        if result is not None:
            return Reply("Success")
        return Reply("Failure")


def serve():
    # create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    add_AuthenticateServicer_to_server(Listener(), server)
    print('Starting server. Listening on port 50051.')
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
