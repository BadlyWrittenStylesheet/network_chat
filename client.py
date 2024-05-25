import asyncio
import sys


async def write_messages(writer):
    while True:
        message = await asyncio.to_thread(sys.stdin.readline)
        writer.write(message.encode())

        await writer.drain()

        if message.strip() == "QUIT":
            break

    print("Exiting...")

async def read_messages(reader: asyncio.StreamReader):
    while True:
        result: bytes = await reader.readline()

        respone = result.decode()

        print(respone.strip())


async def main():
    try:
        server_host, server_port = '127.0.0.1', 50007
        print(f"Establishing connection to: {server_host}:{server_port}...")
        reader, writer = await asyncio.open_connection(server_host, server_port)
        print("Connection established.")

        read_task = asyncio.create_task(read_messages(reader))

        await write_messages(writer)

        read_task.cancel()
        print("Disconnecting...")
        # Nie wymyslilem nic lepszego bruh ale jest pewnie cos
        await asyncio.sleep(3)

        print("closing")
        writer.close()
        await writer.wait_closed()

        print("Bye!")
    except ConnectionRefusedError:
        print("Failed to establish connection, check if the host is online and try again.")
    
asyncio.run(main())

