from multicast import multicast
from multicast_listen import multicast_listen


import asyncio 

MULTICAST_ADDR = "224.0.0.1"
PORT = 50007

message = "tymon"

def send_message():
    msg = input("> ")
    multicast(MULTICAST_ADDR, PORT, msg)

async def main():

    print("Start multicast")
    multicast(MULTICAST_ADDR, PORT, message)
    print("Start listening for response")
    data, addr = await multicast_listen(MULTICAST_ADDR, PORT)
    print(f"Response received from: {addr} with: {data.decode()}")

    while True:
        print('1')
        data, addr = asyncio.create_task(multicast_listen(MULTICAST_ADDR, PORT))
        print('2')
        asyncio.create_task(send_message)
        print(data.decode(), addr)
        print('3')


        
asyncio.run(main())