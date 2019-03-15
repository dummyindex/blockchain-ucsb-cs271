import queue
import sys
import os
import threading
import socket
import json

from network_config import *
from ServerNode import *
from utils import *
from utils import *

class Client():
    def __init__(self, client_name, server_configs, client_configs):
        config = client_configs[client_name]
        self.name = config["name"]
        self.config = config
        self.initial_unit = config["initial_amount"]
        self.current_txn = None
        self.server_names = list(server_configs.keys())
        all_configs = dict(server_configs)
        all_configs.update(client_configs)
        self .tcpServer = RaftTCPServer(self.name, all_configs)
        self.rpc_queue = queue.Queue()
        self.txn_queue = queue.Queue()
        self.txn_id = 0
        self.estimate_leader = None
        self.id2amount = {}
        self.balance = config["initial_amount"]
        self.cmd_thread = threading.Thread(
            target=self.handle_cmds, daemon=True)

    def start(self):
        self.tcpServer.start_server(self.rpc_queue)
        self.cmd_thread.start()
        self.handle_userInput()

    def add_transaction(self):
        '''
        prompt user for standard input of transactions
        '''
        pass

    def handle_complete_txn(self, req):
        print("---complete")
        txn_id = req['txn_id']
        self.balance -= self.id2amount[txn_id]
        if txn_id in self.txns:
            self.txns.pop(txn_id)
        print("updated balance:", self.balance)

    def handle_cmds(self):
        self.txns = {}
        last_upload_time = time.time()
        interval = 0.3
        while True:
            # response
            while not self.rpc_queue.empty():
                req = self.rpc_queue.get()
                req_type = req['type']
                if req_type == txnCommitType:
                    self.handle_complete_txn(req)

            # transaction
            if time.time() - last_upload_time > interval:
                while not self.txn_queue.empty():
                    ta, tb, amount, txn_id = self.txn_queue.get()
                    assert not (txn_id in self.txns)
                    self.txns[txn_id] = (ta, tb, amount)
                last_upload_time = time.time()

                for txn_id in self.txns:
                    ta, tb, amount = self.txns[txn_id]
                    self.send_clientCommand(ta, tb, amount, txn_id)

            # print balance and block chain command

    def send_clientCommand(self, ta, tb, amount, txn_id):
        data = {
            'type': clientCommandType,
            'send_client': ta,
            'recv_client': tb,
            'amount': amount,
            'txn_id' : txn_id,
            'source' : self.name
        }
        
        leader = self.estimate_leader
        if self.estimate_leader == None:
            leader = random.choice(self.server_names)
        print("sending txn to esitmated leader", leader)
        data = json.dumps(data)
        # print(data)
        self.tcpServer.send(leader, data)

    def update_client(self):
        pass

    def handle_userInput(self):
        while True:
            #print('Please add transaction in format: Client1 Client2 Amount')
            input_txn = input('Input transactionFormat(ta tb amount)/printBalance/printBlockChain\n')
            self.upload_transaction(input_txn)
            
    def upload_transaction(self, input_txn):
        parsed_txn = input_txn.split()
        if len(parsed_txn) != 3:
            print("wrong format. enter ta, tb, tc")
            return
        ta = parsed_txn[0]
        tb = parsed_txn[1]
        amount = None
        try:
            amount = float(parsed_txn[2])
        except:
            print("enter numeric value for amount")
            return

        if parsed_txn[0] != self.name:
            print('The first client should be %s' % (self.name))
            return

        self.txn_queue.put((ta, tb, amount, self.txn_id))
        self.id2amount[self.txn_id] = amount
        self.txn_id += 1


def client_main():
    client_name = sys.argv[1]
    client = Client(client_name, server_configs, client_configs)
    client.start()

if __name__ == "__main__":
    client_main()
