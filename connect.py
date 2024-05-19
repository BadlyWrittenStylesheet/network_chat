from multicast_listen import multicast_listen
from defaults import MULTICAST_ADDR, PORT


print("Listening multicast")
data, addr = multicast_listen(MULTICAST_ADDR, PORT)
print("Received:", data, addr)

