from multicast import multicast
from multicast_listen import multicast_listen

MULTICAST_ADDR = "224.0.0.1"
PORT = 50007

message = "tymon"

print("start multicast")
multicast(MULTICAST_ADDR, PORT, message)
print("start listening for response")
data, addr = multicast_listen(MULTICAST_ADDR, PORT, debug=True)

print(data, addr)


