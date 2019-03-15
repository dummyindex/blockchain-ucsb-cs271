import queue
import sys
import os
import threading
import socket
import json

from client_config import *
from ServerNode import *
from utils import *
from utils import *

INITIAL_UNIT = 100


class Client():
    def __init__(self, client_id):
        config = clients[client_id]
        self.id = client_id
        self.name = config["name"]
        self.config = config
        self.current_unit = 100
        self.initial_unit = config["initial_amount"]
        self.send_port = None
        self.recv_port = config["recv_port"]
        self.current_txn = None
        self.host = 'localhost'

        self.recv_thread = threading.Thread(
            target=self.start_clientTCP)
        self.wait_userInput_thread = threading.Thread(
            target=self.handle_userInput)

        self.start_client()

    def start_client(self):
        self.recv_thread.start()
        self.wait_userInput_thread.start()

    def add_transaction(self):
        '''
        prompt user for standard input of transactions
        '''
        pass

    def estimate_leader(self):
        '''
        Todo: estimate current leader
        set server1 recv_port
        '''
        self.send_port = 8932

    def send_clientCommand(self, parsed_txn):
        data = {
            'type': clientCommandType,
            'send_client': parsed_txn[0],
            'recv_client': parsed_txn[1],
            'amount': parsed_txn[2]
        }

        self.estimate_leader()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.host, self.send_port)
        sock.connect(server_address)
        push_data(sock, data)
        sock.close()

    def start_clientTCP(self):
        print(f'Client {self.name} starting: ')
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
            connection, server_address = sock.accept()
            data = obtain_data(connection)
            json_data = json.loads(data)
            print("got data:", data)
            self.update_client(json_data)

    def update_client(self, json_data):
        pass

    def handle_userInput(self):
        '''
        1. The blocks are initialized by input file, txt
        2. After finishing initialization, user input transactions
        3. If the sender in txn not current client, decline
        '''
        input_txn = None

        while True:
            #print('Please add transaction in format: Client1 Client2 Amount')
            if len(transaction_list) != 0:
                parsed = transaction_list[0].split()
                print(f'parsed {parsed}')

                if self.name == parsed[0]:
                    input_txn = transaction_list.pop(0)
                    #print(f'pop: {input_txn}')
                    self.parse_input_transaction(input_txn)

            else:
                input_txn = input()
                print(f'User input transaction: {input_txn}')
                self.parse_input_transaction(input_txn)

    def parse_input_transaction(self, input_txn):
        parsed_txn = input_txn.split()

        if parsed_txn[0] != self.name:
            print(f'The first client should be {self.name}')
        else:
            self.send_clientCommand(parsed_txn)

    def printCurrentBalance(self):
        print(f'Client {self.name}: current amount = {self.current_unit}')


def main():
    client_id = int(sys.argv[1])
    client = Client(client_id)


if __name__ == "__main__":
    main()
