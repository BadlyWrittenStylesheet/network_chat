import asyncio
import sys


data = {}

async def send_messages(writer):
    while True:
        message = await asyncio.to_thread(sys.stdin.readline)

        match message.strip():
            case "QUIT":
                writer.write(b"QUIT")
                break
            case "LIST":
                writer.write("LIST\n".encode())
                await writer.drain()
            case _:
                writer.write((f"SEND;{message.strip()}\n").encode())
                await writer.drain()

    print("Exiting...")

async def receive_messages(reader: asyncio.StreamReader):
    while True:
        result: bytes = await reader.read(2137)

        code, _, content = result.decode().partition(";")

        #print(code, content, "bruh")
        match code:
            case 'SEND':
                print(content.strip())
            case 'INPUT':
                print("Respond to:", content.strip())
                #user_in = input(content)
                #writer.write(f"RESPONSE;{user_in}\n".encode())
                #await writer.drain()


            #case 'INFO DH BASE':
            #    data['p'], data['g'] = content.split(":")
            #    print(data)




async def main():
    try:
        server_host, server_port = '127.0.0.1', 50007
        print(f"Establishing connection to: {server_host}:{server_port}...")
        reader, writer = await asyncio.open_connection(server_host, server_port)
        print("Connection established.")

        read_task = asyncio.create_task(receive_messages(reader))

        await send_messages(writer)

        read_task.cancel()
        print("Disconnecting...")
        # Awful solution but had nothing else in mind :/
        await asyncio.sleep(3)

        print("Closing")
        writer.close()
        await writer.wait_closed()

        print("Bye!")
    except ConnectionRefusedError:
        print("Failed to establish connection, check if the host is online and try again.")
    
asyncio.run(main())

