import time
from utils import *
import queue
import threading
from Block import *
from RaftTCPServer import *
from network_config import *
follower_role = 0
candidate_role = 1
leader_role = 2
requestVoteType = "requestVote"
appendEntryType = "appendEntry"
voteResponseType = "voteResponse"
startElectionType = "startElection"
clientCommandType = "clientCommand"
transRoleType = "transRole"


def start_all_servers():
    servers = []
    for name in configs:
        servers.append(ServerNode(name, configs))
        servers[-1].start()
    return servers

class ServerNode():
    def __init__(self, config_name, configs):
        config = configs[config_name]
        self.name = config_name
        self.config = config
        self.role = follower_role
        self.election_timeout = gen_timeout()
        self.is_timeout_thread = threading.Event()
        self.vote_for = None
        self.received_vote = 0
        self.block_chain = BlockChain()
        self.term = config["init_term"]
        self.other_names = [name for name in configs]
        self.other_names.remove(self.name)
        self.last_refresh_time = time.time()
        #  RPC queue
        self.rpc_queue = queue.Queue()
        self.tcpServer = RaftTCPServer(self.name, configs)
        self.handler_thread = threading.Thread(
            target=self.handle_rpc_queue, daemon=True)

        self.timeout_thread = threading.Thread(
            target=self.check_time_out, daemon=True)
        self.notify_timeout_event = threading.Event()
        self.notify_timeout_event.clear()

    def start(self):
        self.last_refresh_time = time.time()
        self.tcpServer.start_server(self.rpc_queue)
        self.handler_thread.start()
        self.timeout_thread.start()

    def add_election_req(self, role):
        req = {
            "type": startElectionType,
            "role": role
        }
        self.rpc_queue.put(req)

    def update_refresh_time(self):
        self.last_refresh_time = time.time()
        self.notify_timeout_event.set()

    def trans_candidate(self):
        self.update_refresh_time()
        self.role = candidate_role
        self.term += 1
        # candidate vote for itself
        self.vote_for = self.name
        self.send_requestVotes()

    def trans_follower(self):
        self.role = follower_role
        self.vote_for = None

    def trans_leader(self):
        print("========================")
        print(self.name, "become leader, term=", self.term)
        print("========================")
        self.role = leader_role
        '''
        Todo: if leader has been elected
        1. send heartbeat (empty AppendEntries)
        2. receive client commd
        3. logIndex >= nextIndex for a follower, send AppendEntries with log entries
        4. N > commitIndex ?
        '''

    def check_time_out(self):
        self.last_refresh_time = time.time()
        while True:
            if self.notify_timeout_event.is_set():
                self.last_refresh_time = time.time()
                self.notify_timeout_event.clear()

            is_timeout = (
                time.time() - self.last_refresh_time) > self.election_timeout
            if is_timeout:
                print("timeout")
                self.add_election_req(candidate_role)
                self.last_refresh_time = time.time()

    def handle_startElection_req(self, req):
        if self.role == leader_role:
            return
        self.trans_candidate()

    def response_vote(self, candidate, granted):
        data = {
            'type': voteResponseType,
            'term': self.term,
            'voteGranted': granted
        }
        data = json.dumps(data)
        self.tcpServer.send(candidate, data)

    def is_completer_log(self, other_log):
        '''
        todo
        '''
        return True

    def handle_requestVote_req(self, req):
        candidate_term = req['term']
        candidate = req['source']
        other_log = None
        if candidate_term > self.term:
            self.term = candidate_term
            if self.role == leader_role or self.role == candidate_role:
                self.trans_follower()
        if candidate_term == self.term and\
           (self.vote_for != None or self.vote_for == candidate) and\
           self.is_completer_log(other_log):
            self.vote_for = req['source']
            self.response_vote(candidate, True)
            self.election_timeout = gen_timeout()
        else:
            self.response_vote(candidate, False)

    def handle_voteResponse_req(self, req):
        '''
        only candidate cares about it
        data = {
            'type': voteResponseType,
            'term': self.term,
            'voteGranted': granted
        }

        if not vote granted:
            => 'follower'
        if vote granted:
            add voted number, compare to majority
        '''
        if self.role != candidate_role:
            return

        majority = len(configs) / 2 + 1
        if req['voteGranted']:
            assert req['term'] <= self.term
            self.received_vote += 1
            if self.received_vote >= majority:
                self.is_timeout_thread.clear()
                self.trans_leader()

        if req['term'] > self.term:
            self.term = req['term']
            self.is_timeout_thread.clear()
            self.trans_follower()

    def handle_clientCommand(self, req):
        '''
        data = {
            type: clientCommandType
            transaction detail:
                send_client
                recv_client
                amount
        }
        '''
        pass

    def handle_req(self, req):
        req_type = req["type"]
        if req_type == startElectionType:
            self.update_refresh_time()
            self.handle_startElection_req(req)
        elif req_type == requestVoteType:
            self.update_refresh_time()
            self.handle_requestVote_req(req)
        elif req_type == voteResponseType:
            # self.update_refresh_time()
            self.handle_voteResponse_req(req)
        if req_type == clientCommandType:
            if self.role == follower_role:
                pass
                # redirect to current leader
            if self.role == leader_role:
                self.handle_clientCommand(req)
            if self.role == candidate_role:
                pass
        else:
            print("not implemented:", req)

    def handle_rpc_queue(self):
        '''
        todo: dispatch all reqs here
        '''
        while True:
            if self.rpc_queue.empty():
                continue
            req = self.rpc_queue.get()
            print(req)
            self.handle_req(req)
        return

    def send_requestVote(self, name):
        # print("sending vote request to", name)
        data = {
            "type": requestVoteType,
            "term": self.term,
            "lastLogIndex": len(self.block_chain) - 1,
            "lastLogTerm": self.block_chain.get(-1).term,
            "source": self.name
        }
        data = json.dumps(data)
        self.tcpServer.send(name, data)

    def send_requestVotes(self):
        for name in self.other_names:
            self.send_requestVote(name)
