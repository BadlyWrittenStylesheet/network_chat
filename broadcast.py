import socket

message = b'Hello there!1!!'
broadcast_address = '<broadcast>'
port = 50007

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    udp_socket.sendto(message, (broadcast_address, port))
    print(f"Message {message} to {broadcast_address}, {port}")
