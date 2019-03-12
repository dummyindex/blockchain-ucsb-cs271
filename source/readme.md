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
