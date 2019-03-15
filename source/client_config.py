start_port = 5000
clientA = {
    "send_port": start_port+1,
    "recv_port": start_port+2,
    "name": "A",
    "init_term": 0
}
clientB = {
    "send_port": start_port+3,
    "recv_port": start_port+4,
    "name": "B",
    "init_term": 0
}
clientC = {
    "send_port": start_port+5,
    "recv_port": start_port+6,
    "name": "C",
    "init_term": 0
}

clients = {
    "A": clientA,
    "B": clientB,
    "C": clientC
}

with open('input_file.txt', 'r') as myfile:
    content = myfile.readlines()
transaction_list = [x.strip() for x in content]
