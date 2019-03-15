start_port = 5000
clientA = {
    "send_port": start_port+1,
    "recv_port": start_port+2,
    "name": "A",
    "initial_amount": 100
}
clientB = {
    "send_port": start_port+3,
    "recv_port": start_port+4,
    "name": "B",
    "initial_amount": 100
}
clientC = {
    "send_port": start_port+5,
    "recv_port": start_port+6,
    "name": "C",
    "initial_amount": 100
}


clients = [clientA, clientB, clientC]
# clients = {
#     "A": clientA,
#     "B": clientB,
#     "C": clientC
# }


with open('input_file.txt', 'r') as myfile:
    content = myfile.readlines()
transaction_list = [x.strip() for x in content]
