import socket
import struct

# MULTICAST_ADDR = '224.0.0.1'
# PORT = 50007

def multicast_listen(MULTICAST_ADDR, PORT, debug=False):
    # UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(('', PORT))

    # Add socket to multicast group
    group = socket.inet_aton(MULTICAST_ADDR)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    if debug:
        print(f"Listening on: {MULTICAST_ADDR}, {PORT}")
    while True:
        data, addr = sock.recvfrom(1024)
        print(f"Received message:\n{data.decode()}\nfrom {addr}")
        return data, addr
        
