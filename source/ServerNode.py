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
appendEntriesType = "appendEntriesType"
voteResponseType = "voteResponse"
appendEntriesResponseType = "appendEntriesResponseType"
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
    def __init__(self, config_name, configs, avg_election_timeout=0.5):
        config = configs[config_name]
        self.name = config_name
        self.config = config
        self.role = follower_role
        self.avg_election_timeout = avg_election_timeout
        self.election_timeout = gen_timeout(self.avg_election_timeout)
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
        self.notify_timeout_thread_refresh_time_event = threading.Event()
        self.notify_timeout_thread_refresh_time_event.clear()

        # heart beat for leader
        self.heartbeat_thread = None
        self.heartbeat_end_event = threading.Event()
        self.heartbeat_end_event.clear()
        self.leader = None

        # for store client txn
        self.txn_buffer = []

        # log commit info
        self.name2loggedIndex = None
        
    def start(self):
        self.last_refresh_time = time.time()
        self.tcpServer.start_server(self.rpc_queue)
        self.handler_thread.start()
        self.timeout_thread.start()

    def heartbeat_leader_thread(self):
        last_time = time.time()
        interval = self.election_timeout/3.0
        while True:
            if self.heartbeat_end_event.is_set():
                self.heartbeat_end_event.clear() # no need to clear, but harmless
                return

            if time.time() - last_time > interval:
                self.send_heartbeats()
                last_time = time.time()


    def add_election_req(self, role):
        req = {
            "type": startElectionType,
            "role": role
        }
        self.rpc_queue.put(req)

    def update_refresh_time(self):
        self.last_refresh_time = time.time()
        self.notify_timeout_thread_refresh_time_event.set()

    def check_time_out(self):
        self.last_refresh_time = time.time()
        while True:
            if self.notify_timeout_thread_refresh_time_event.is_set():
                print("timeout thread refreshing....")
                self.last_refresh_time = time.time()
                self.notify_timeout_thread_refresh_time_event.clear()

            is_timeout = (
                time.time() - self.last_refresh_time) > self.election_timeout
            if is_timeout:
                # print(self.name, "timeout")
                self.add_election_req(candidate_role)
                self.last_refresh_time = time.time()

    def trans_candidate(self):
        self.update_refresh_time()
        self.role = candidate_role
        self.term += 1
        # candidate vote for itself
        self.vote_for = self.name
        self.received_vote = 1
        self.send_requestVotes()

    def trans_follower(self):
        # step down
        assert self.role != follower_role
        if self.role == leader_role:
            self.heartbeat_end_event.set()
            # self.heartbeat_thread.join()
            # print("heartbeat ends")
            self.heartbeat_thread = None
        assert self.heartbeat_thread == None
        self.role = follower_role
        self.vote_for = None
        self.leader = None
        
    def trans_leader(self):
        print("========================")
        print(self.name, "become leader, term", self.term, "votes", self.received_vote)
        print("========================")
        self.role = leader_role
        self.name2nextIndex = {}
        self.name2lastContactTime = {}
        self.name2loggedIndex = {}
        self.txn_buffer = []
        for name in self.other_names:
            self.name2nextIndex[name] = self.block_chain.lastLogIndex() + 1
            self.name2lastContactTime[name] = time.time()
            self.name2loggedIndex[name] = set()
        self.send_heartbeats() # send heartbeats immediately
        self.heartbeat_end_event.clear()
        # self.heartbeat_thread = threading.Thread(
        #     target=self.heartbeat_leader_thread, daemon=True)
        # self.heartbeat_thread.start()        
        '''
        Todo: if leader has been elected
        1. send heartbeat (empty AppendEntries)
        2. receive client commd
        3. logIndex >= nextIndex for a follower, send AppendEntries with log entries
        4. N > commitIndex ?
        '''

    def response_vote(self, candidate, granted):
        data = {
            'type': voteResponseType,
            'term': self.term,
            'voteGranted': granted
        }
        data = json.dumps(data)
        self.tcpServer.send(candidate, data)

    def is_completer_log(self, lastLogIndex, lastLogTerm):
        '''
        todo
        '''
        not_completer = self.block_chain.lastLogTerm() > lastLogTerm or\
                        (self.block_chain.lastLogTerm() == lastLogTerm and\
                         self.block_chain.lastLogIndex() > lastLogIndex)
        return not not_completer

    def handle_startElection_req(self, req):
        if self.role == leader_role:
            return
        print(self.name, "start election at term", self.term + 1)
        self.trans_candidate()

    def has_matched_block(self, index, term):
        if index <0 or index >= len(self.block_chain):
            return False
        block = self.block_chain.get(index)
        return block.term == term

    def handle_appendEntries_req(self, req):
        '''
        '''
        self.update_refresh_time()
        is_heartbeat = req['is_heartbeat']
        term = req['term']
        leader = req['leaderId']
        prevLogIndex = req['prevLogIndex']
        prevLogTerm = req['prevLogTerm']
        commitIndex = req['commitIndex']
        block_list = req['entries']
        block_list = [Block.from_dict(d) for d in block_list]
        next_id = prevLogIndex + len(block_list) + 1
        # not valid leader term case
        if self.term > term:
            self.response_appendEntries(leader, False, prevLogIndex, next_id)
            return

        if term > self.term:
            self.term = term

        self.leader = leader
        # stepdown
        if self.role == candidate_role or self.role == leader_role:
            self.trans_follower()
        
        # is heartbeat
        if is_heartbeat:
            self.response_appendEntries(leader, True, prevLogIndex, next_id, is_heartbeat=True)
            return
        
        assert prevLogIndex >= 0
        if not self.has_matched_block(prevLogIndex, prevLogTerm):
            self.response_appendEntries(leader, False, prevLogIndex, next_id)
            return
        
        # append new entries
        self.block_chain.update_chain_at(prevLogIndex+1, block_list)
        # advance state machine - balance

        # respond
        self.response_appendEntries(leader, True, prevLogIndex, next_id)
        
    def handle_requestVote_req(self, req):
        candidate_term = req['term']
        candidate = req['source']
        lastLogIndex = req['lastLogIndex']
        lastLogTerm = req['lastLogTerm']
        if candidate_term > self.term:
            self.term = candidate_term
            # stepdown
            if self.role == leader_role or self.role == candidate_role:
                self.trans_follower()

        if candidate_term == self.term and\
           (self.vote_for == None or self.vote_for == candidate) and\
           self.is_completer_log(lastLogIndex, lastLogTerm):
            print("%s grant vote to %s at term %d" % (self.name, candidate, self.term))
            self.vote_for = req['source']
            self.response_vote(candidate, True)
            self.election_timeout = gen_timeout(self.avg_election_timeout)
            self.update_refresh_time()
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

        majority = int(len(configs) / 2) + 1
        if req['voteGranted']:
            assert req['term'] <= self.term
            if req['term'] == self.term:
                self.received_vote += 1
                if self.received_vote >= majority:
                    self.trans_leader()

        if req['term'] > self.term:
            self.term = req['term']
            self.trans_follower()


    def update_success_follower_log(self, name, next_index):
        self.name2loggedIndex[name].add(next_index-1)
        self.name2nextIndex[name] = next_index
        
    def majority(self):
        return int(len(configs)/2)+1

    def count_logged_follower_num(self, i):
        count = 0
        for name in self.name2loggedIndex:
            for index in self.name2loggedIndex[name]:
                if i <= index:
                    count += 1
                    break
                
    def check_update_commit(self):
        start = self.block_chain.get_commitIndex() + 1
        end = len(self.block_chain)
        for i in range(start, end):
            if self.count_logged_follower_num(i) >= self.majority():
                self.block_chain.commit_next()
            else:
                break
            
    def handle_appendEntriesResponse_req(self, req):
        '''
        only leader considers this message
        when in other state (role), slow network may deliver previous
        sent response, so need to check role
        data = {
            "type" : appendEntriesResponseType,
            "term" : self.term,
            "success" : success,
            "source" : self.name,
            "prevLogIndex" : prevLogIndex,
            "is_heartbeat": is_heartbeat
        }
        '''
        if self.role != leader_role:
            return

        term = req['term']
        success = req['success']
        name = req['source']
        prevLogIndex = req['prevLogIndex']
        is_heartbeat = req['is_heartbeat']
        next_index = req['next_index']
        # stepdown
        if term > self.term:
            assert not req['success']
            self.trans_follower()
            return

        # corner case: append sent in previous terms
        # just returned, meaningless
        if term < self.term:
            assert not req['success']
            return
        
        if is_heartbeat:
            return
        
        if success:
            self.update_success_follower_log(name, next_index)
            self.check_update_commit()
        else:
            self.name2nextIndex[name] -= 1
            assert self.name2nextIndex[name] >= 0

    def handle_clientCommand_req(self, req):
        '''
        data = {
            type: clientCommandType
            send_client:
            recv_client:
            amount:
        }
        '''
        if self.role == candidate_role:
            # discard, let client reissue
            return
        elif self.role == follower_role:
            # redirect
            name = self.leader
            if self.leader == None:
                if len(self.other_names) == 0:
                    return
                name = self.other_names[0]
            self.redirect_clientCommand(name, req)
        elif self.role == leader_role:
            send_client = req['send_client']
            recv_client = req['recv_client']
            amount = req['amount']
            temp = send_client + " " + recv_client + " " + str(amount)
            self.txn_buffer.append(temp)
            if len(self.txn_buffer) == 2:
                new_block = Block(self.txn_buffer[0], self.txn_buffer[1], self.term, self.block_chain.get(-1).hash())
                self.block_chain.append(new_block)
                txn_buffer = []

    def handle_req(self, req):
        req_type = req["type"]
        if req_type == startElectionType:
            self.update_refresh_time()
            self.handle_startElection_req(req)
        elif req_type == requestVoteType:
            self.handle_requestVote_req(req)
        elif req_type == voteResponseType:
            self.handle_voteResponse_req(req)
        elif req_type == appendEntriesType:
            self.handle_appendEntries_req(req)
        elif req_type == appendEntriesResponseType:
            self.handle_appendEntriesResponse_req(req)
        elif req_type == clientCommandType:
            self.handle_clientCommand_req(req)
        else:
            print("not implemented:", req)

    def handle_rpc_queue(self):
        '''
        todo: dispatch all reqs here
        '''
        while True:
            if self.role == leader_role:
                self.leader_update_followers()
            while not self.rpc_queue.empty():
                req = self.rpc_queue.get()
                print(self.name, self.term, ":", req)
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

    def send_appendEntries(self, name, is_heartbeat=False):
        next_index = self.name2nextIndex[name]
        prevLogIndex = next_index-1
        data = {
            "type": appendEntriesType,
            "term": self.term,
            "prevLogIndex": prevLogIndex,
            "prevLogTerm": self.block_chain.get(prevLogIndex).term,
            "source": self.name,
            "leaderId": self.name,
            "entries": self.block_chain.get_entries_start_at_list(next_index),
            "commitIndex": self.block_chain.get_commitIndex(),
            "is_heartbeat": is_heartbeat
        }
        data = json.dumps(data)
        self.tcpServer.send(name, data)

    def send_heartbeats(self):
        for name in self.name2nextIndex:
            self.send_appendEntries(name, is_heartbeat=True)

    def response_appendEntries(self, leader, success, prevLogIndex, next_index, is_heartbeat=False):
        data = {
            "type" : appendEntriesResponseType,
            "term" : self.term,
            "success" : success,
            "source" : self.name,
            "prevLogIndex" : prevLogIndex,
            "is_heartbeat": is_heartbeat,
            "next_index": next_index
        }
        data = json.dumps(data)
        self.tcpServer.send(leader, data)

    def redirect_clientCommand(self, name, req):
        data = json.dumps(req)
        self.tcpServer.send(name, data)

    def leader_update_followers(self):
        assert self.role == leader_role
        interval = self.avg_election_timeout/3
        for name in self.name2nextIndex:
            nextIndex = self.name2nextIndex[name]
            if self.block_chain.lastLogIndex() < nextIndex:
                # heartbeat
                if time.time() -  self.name2lastContactTime[name] > interval:
                    self.send_appendEntries(name, is_heartbeat=True)
                    self.name2lastContactTime[name] = time.time()
                continue
            
            if time.time() - self.name2lastContactTime[name] > interval:
                self.send_appendEntries(name, False)
                self.name2lastContactTime[name] = time.time()
        
