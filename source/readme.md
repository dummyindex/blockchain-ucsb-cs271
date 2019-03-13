# Project source code

## python version
python3

## Raft

### type of requests
- requestVote
- appendEntries

### implementation details
- roles: follower, candidate, leader
- classes: log, block, networkServer(tcp), server, client
- election timeout : need to be random to ensure some liveness


### raft TCP server:
- send request
- recieve request from port and return to queue for raft server node later ops


### server node
- server node dont care about underlying ports, ip addr....
- server node send by name