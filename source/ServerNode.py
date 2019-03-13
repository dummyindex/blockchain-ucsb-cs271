import time
from utils import *
import queue
import threading
from Block import *
from RaftTCPServer import *
follower_role = 0
candidate_role = 1
leader_role = 2
requestVoteType = "requestVote"
appendEntryType = "appendEntry"

class ServerNode():
    def __init__(self, config_name, configs):
        config = configs[config_name]
        self.name = config_name
        self.config = config
        self.role = follower_role
        self.election_timeout = gen_timeout()
        self.block_chain = BlockChain()
        self.term = config["init_term"]
        self.other_names = [config["name"] for config in configs]
        self.other_names.remove(self.name)
        self.last_refresh_time = time.time()
        #  RPC queue
        self.rpc_queue = queue.Queue()
        self.tcpServer = RaftTCPServer(config, configs)
        self.handler_thread = threading.Thread(target=self.handle_rpc_queue, args=(self.rpc_queue), daemon=True)
        
        self.timeout_thread = threading.Thread(target=self.check_time_out, args=(self.rpc_queue), daemon=True)
        

    def start(self):
        self.last_refresh_time = time.time()
        self.tcpServer.start_server(self.rpc_queue)
        self.handler_thread.start()

    def trans_candidate(self):
        self.last_refresh_time = time.time()
        self.role = candidate_role
        self.term += 1
        self.send_requestVotes()

    def check_time_out(self):
        while True:
            if self.role == leader_role:
                continue
            
            is_timeout = time.time() - self.last_refresh_time > self.election_timeout
            if is_timeout:
                self.trans_candidate()
        
    def handle_rpc_queue(self):
        '''
        todo: dispatch all reqs here
        '''
        return

    def send_requestVote(self, name):
        data = {
            "type" : requestVoteType,
            "term" : self.term,
            "lastLogIndex": len(self.block_chain) - 1,
            "lastLogTerm": self.block_chain.get(-1).term
        }
        data = json.dumps(data)
        self.tcpServer.send(name, data)

    def send_requestVotes(self):
        for name in self.other_names:
            self.send_requestVote(name)

