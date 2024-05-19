import asyncio
from multicast import multicast
from multicast_listen import multicast_listen

MULTICAST_ADDR = "224.0.0.1"
PORT = 50007

message = "tymon"

async def main():

    print("start multicast")
    multicast(MULTICAST_ADDR, PORT, message)
    print("start listening for response")
    data, addr = await multicast_listen(MULTICAST_ADDR, PORT)
    print(f"Response received from: {addr} with: {data.decode()}")

    msg = input("> ")
    while msg != '':
        data, addr = await multicast_listen(MULTICAST_ADDR, PORT, debug=True)
        
        msg = input("> ")
        multicast(MULTICAST_ADDR, PORT, msg)

asyncio.run(main())
