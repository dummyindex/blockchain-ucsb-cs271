import random
import time
import socket
import random
import time
import threading
from network_config import *
import network_config

class RaftTCPServer():
    def __init__(self, delay, config_name, configs):
        config = configs[config_name]
        self.config = configs[config_name]
        self.send_port = config["send_port"]
        self.recv_port = config["recv_port"]
        self.host = 'localhost'
        change_balance(config["balance"])
        self.name = config["name"]
        self.end_symbol = network_config.end_symbol
        self.delay = delay
        self.out_channels = {}
        for i in range(len(configs)):
            if i == config_name:
                continue
            config = configs[i]
            in_channels[config["name"]] = create_channel(config["send_port"], config)
            self.out_channels[config["name"]] = create_channel(config["recv_port"], config)
        self.client_total = len(self.out_channels) + 1

    def init(self):
        pass
    
    def start_tcp(self):
        '''
        start a tcp server
        '''
        global client_state
        print(self.name + " starting backend tcp server")
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = (self.host, self.recv_port)
        print('starting up on {} port {}'.format(*server_address))
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(20)
        while True:
            # Wait for a connection
            # print('waiting for a connection')
            connection, client_address = sock.accept()
            data = obtain_data(connection)
    
    def start_server(self):
        '''
        todo: move it to server node
        '''
        print("sleep for 5s. please start all 3 clints within 5s")
        t1 = threading.Thread(target=self.start_tcp, args=())
        t1.daemon = True
        t1.start()
        t2 = threading.Thread(target=self.try_transfer_loop, args=())
        t2.daemon = True
        t2.start()

        while 1:
            cmd = input("give command, ")
            if cmd == "snap":
                self.start_snap()
                # self.collect_report()
            else:
                amount, name = cmd.split()
                amount = float(amount)
                self.add_transfer(amount, name)

    
