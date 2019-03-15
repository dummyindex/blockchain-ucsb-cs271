from ServerNode import *
from RaftTCPServer import *


def manual_test():
    servers = start_all_servers()
    print("allow 1 secs for servers to start")
    for server in servers:
        print(server.name)
    while True:
        pass

manual_test()
