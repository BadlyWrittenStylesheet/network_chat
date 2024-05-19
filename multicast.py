import socket

# MULTICAST_ADDR = '224.0.0.1'
# PORT = 50007

# message = "H-Hii!1!!"

def multicast(MULTICAST_ADDR, PORT, message):

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        sock.sendto(message.encode(), (MULTICAST_ADDR, PORT))
        print("Message sent successfully")


