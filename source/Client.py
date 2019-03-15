import queue

from client_config import *
from utils import *


class Client():
    def __init__(self, client_name, clients):
        config = clients[client_name]
        self.name = client_name
        self.config = config
        self.send_port = config["send_port"]
        self.recv_port = config["recv_port"]
        self.host = 'localhost'
        self.clientRPC_queue = queue.Queue()

        self.recv_thread = threading.Thread(
            target=self.handle_clientRPC_queue, daemon=True)

    def start_client(self):
        self.recv_thread.start()

    def add_transaction(self):
        '''
        prompt user for standard input of transactions
        '''
        pass

    def estimate_leader(self):
        pass

    def send_clientCommand(self, receiver, amount):
        data = {
            'type': clientCommandType,
            'send_client': self.name,
            'recv_client': receiver,
            'amount': amount
        }
        pass

    def handle_clientRPC_queue(self):
        print(self.name + " starting client")
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
            clientRPC_queue.put(json_data)
