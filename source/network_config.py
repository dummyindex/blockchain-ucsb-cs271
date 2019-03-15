delay = 5
end_symbol = "$$$"
start_port = 8940
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
