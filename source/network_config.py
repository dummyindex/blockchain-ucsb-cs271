delay = 5
end_symbol = "$$$"
start_port = 8990
config0 = {
    "send_port": start_port+1,
    "recv_port": start_port+2,
    "name": "server0",
    "init_term": 0
}
config1 = {
    "send_port": start_port+3,
    "recv_port": start_port+4,
    "name": "server1",
    "init_term": 0
    # "is_leader": 1

}
config2 = {
    "send_port": start_port+5,
    "recv_port": start_port+6,
    "name": "server2",
    "init_term": 0
}

configs = {
    "server0": config0,
    "server1": config1,
    "server2": config2
}
clientA = {
    "send_port": start_port+7,
    "recv_port": start_port+8,
    "name": "A",
    "initial_amount": 100
}
clientB = {
    "send_port": start_port+9,
    "recv_port": start_port+10,
    "name": "B",
    "initial_amount": 100
}
clientC = {
    "send_port": start_port+11,
    "recv_port": start_port+12,
    "name": "C",
    "initial_amount": 100
}


client_configs = {
    "A": clientA,
    "B": clientB,
    "C": clientC
}

server_configs = configs
all_configs = dict(configs)
all_configs.update(client_configs)

with open('input_file.txt', 'r') as myfile:
    content = myfile.readlines()
transaction_list = [x.strip()for x in content]
print(transaction_list)
