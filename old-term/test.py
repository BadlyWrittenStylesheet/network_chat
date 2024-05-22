from multicast import multicast
from multicast_listen import multicast_listen
from defaults import MULTICAST_ADDR, PORT
import asyncio

message = input("> ")

multicast(MULTICAST_ADDR, PORT, message)

asyncio.run(multicast_listen(MULTICAST_ADDR, PORT))

