delay = 5
end_symbol = "$$$"
start_port = 8910
config0 = {
    "send_port": start_port+1,
    "recv_port": start_port+2,
    "name": "A",
}
config1 = {
    "send_port": start_port+3,
    "recv_port": start_port+4,
    "name": "B",
}
config2 = {
    "send_port": start_port+5,
    "recv_port": start_port+6,
    "name": "C",
}

configs = {
    "A": config0,
    "B": config1,
    "C": config2
}

def obtain_data(connection, symbol="$$$"):
    all_data = ""
    while True:
        data = connection.recv(16)
        # print('received {!r}'.format(data))
        all_data += data.decode('utf-8')
        if all_data.find(symbol)!=-1:
            break
        '''
        # echo test
        if all_data.find(self.end_symbol)!=-1:
            print('sending data back to the client')
        else:
            data = (all_data + self.end_symbol).encode('utf-8')
            connection.sendall(data)
            print('data end', client_address)
            break
        '''
    return all_data

def push_data(conn, data, symbol="$$$"):
    conn.sendall((data+" "+symbol).encode('utf-8'))
