import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST, PORT = '', 50007



with s:
    print(f"Listening on {HOST} {PORT}")
    s.bind((HOST, PORT))
    s.listen(1)
    # print("Connected by", addr)
    while True:
        conn, addr = s.accept()
        # print("Connected by", addr)
        data = conn.recv(1024)
        print("Received data:\n", data)
        print(f"From: {addr}")
        # if not data:
        #     print('no data :/')
        # break
        conn.sendall(data + b'RESPONSE')
