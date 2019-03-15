delay = 5
end_symbol = "$$$"
start_port = 8960
config0 = {
    "send_port": start_port+1,
    "recv_port": start_port+2,
    "name": "A",
    "init_term": 0
}
config1 = {
    "send_port": start_port+3,
    "recv_port": start_port+4,
    "name": "B",
    "init_term": 0
}
config2 = {
    "send_port": start_port+5,
    "recv_port": start_port+6,
    "name": "C",
    "init_term": 0
}

configs = {
    "A": config0,
    "B": config1,
    "C": config2
}
clientA = {
    "send_port": start_port+7,
    "recv_port": start_port+8,
    "name": "clientA",
    "initial_amount": 100
}
clientB = {
    "send_port": start_port+9,
    "recv_port": start_port+10,
    "name": "clientB",
    "initial_amount": 100
}
clientC = {
    "send_port": start_port+11,
    "recv_port": start_port+12,
    "name": "clientC",
    "initial_amount": 100
}


client_configs = {
    "clientA": clientA,
    "clientB": clientB,
    "clientC": clientC
}

server_configs = configs
all_configs = dict(configs)
all_configs.update(client_configs)

with open('input_file.txt', 'r') as myfile:
    content = myfile.readlines()
transaction_list = [x.strip() for x in content]
