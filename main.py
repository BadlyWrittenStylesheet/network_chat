import asyncio

ALL_USERS = {}
sys_msg = {
    "welcome": "Welcome! Write QUIT to leave. ( please don't )\n"
}

async def write_message(writer: asyncio.StreamWriter, msg_bytes: bytes):
    writer.write(msg_bytes)
    await writer.drain()

async def broadcast_message(message: str, blacklist=[], newline: bool=True):
    print(f"Broadcast: {message.strip()} to all except: {', '.join(blacklist)}")
    global ALL_USERS
    if newline:
        message = message + "\n"
    msg_bytes = message.encode()
    #for name, (reader, writer) in ALL_USERS.items():
    #    writer.write(message.encode())
    #    await writer.drain()

    people = {}
    for n, (r, w) in ALL_USERS.items():
        if n not in blacklist:
            people[n] = (r, w)

    tasks = [asyncio.create_task(write_message(w, msg_bytes)) for _, (_, w) in people.items()]
    await asyncio.wait(tasks)


async def connect_user(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    writer.write("Enter nickname:\n".encode())
    name_bytes = await reader.readline()
    name = name_bytes.decode().strip()
    global ALL_USERS
    ALL_USERS[name] = (reader, writer)
    await broadcast_message(f"{name} joined the chat!", blacklist=[name])
    # writer.write(sys_msg['welcome'].encode())
    await write_message(writer, sys_msg['welcome'].encode())
    return name

async def disconnect_user(name, writer):
    writer.close()
    await writer.wait_closed()

    global ALL_USERS
    del ALL_USERS[name]

    await broadcast_message(f"{name} disconnected")


async def handle_chat_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    print("Client connecting...")
    name = await connect_user(reader, writer)
    try:
        while True:
            line_bytes = await reader.readline()
            line = line_bytes.decode()

            if line.strip() == 'QUIT': # ahh ten strip, prawie sie poplakalem jak to znalazlem
                break
            await broadcast_message(f"{name}: {line}", blacklist=[name], newline=False)
    finally:
        
        await disconnect_user(name, writer)


async def main():

    host_addr, host_port = '127.0.0.1', 50007

    server = await asyncio.start_server(handle_chat_client, host_addr, host_port)

    async with server:
        print("Running server forever")
        await server.serve_forever()

asyncio.run(main())
