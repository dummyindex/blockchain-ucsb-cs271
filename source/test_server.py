from ServerNode import *
from RaftTCPServer import *


def manual_test():
    servers = start_all_servers()
    for server in servers:
        print(server.name)


manual_test()
