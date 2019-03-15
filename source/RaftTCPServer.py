import random
import time
import socket
import random
import time
import threading
import json
import network_config

def obtain_data(connection, symbol="$$$"):
    all_data = ""
    while True:
        data = connection.recv(16)
        # print('received {!r}'.format(data))
        all_data += data.decode('utf-8')
        if all_data.find(symbol)!=-1:
            all_data = all_data.replace(symbol, "")
            break
        '''
        # echo test
        if all_data.find(self.end_symbol)!=-1:
            print('sending data back to the client')
        else:
            data = (all_data + self.end_symbol).encode('utf-8')
            connection.sendall(data)
            print('data end', client_address)
            break
        '''
    return all_data

def push_data(conn, data, symbol="$$$"):
    conn.sendall((data+" "+symbol).encode('utf-8'))

class RaftTCPServer():
    def __init__(self, config_name, configs):
        config = configs[config_name]
        self.config = configs[config_name]
        self.send_port = config["send_port"]
        self.recv_port = config["recv_port"]
        self.host = 'localhost'
        self.name = config["name"]
        self.end_symbol = network_config.end_symbol
        self.name2outports = {}
        for name in configs:
            if name == config_name:
                continue
            config = configs[name]
            name = config["name"]
            self.name2outports[name] = config["recv_port"]

    def start_tcp(self, rpc_queue):
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
            connection, client_address = sock.accept()
            data = obtain_data(connection)
            json_data = json.loads(data)
            # print("got data:", data)
            rpc_queue.put(json_data)
        
    def start_server(self, rpc_queue):
        '''
        None blocking
        '''
        t1 = threading.Thread(target=self.start_tcp, args=[rpc_queue], daemon=True)
        t1.start()
        
    def send(self, name, data):
        try:
            port = self.name2outports[name]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self.host, port)
            sock.connect(server_address)
            push_data(sock, data)
            sock.close()
        except Exception as e:
            print(e)
            print("NETWORK ISSUE (site failure?) => SEND FAILURE")
        
