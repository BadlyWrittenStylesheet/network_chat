import asyncio
from sympy import randprime
from dh import mod_exp, get_shared_key, get_public_key

ALL_USERS = {}
sys_msg = {
    "welcome": "Welcome! Write QUIT to leave. ( please don't )\n"
}

async def send_message(writer: asyncio.StreamWriter, msg_bytes: bytes):
    writer.write(msg_bytes)
    await writer.drain()

async def broadcast_message(message: str | list[str], code: str, blacklist=[], newline: bool=True):
    if isinstance(message, list):
        await broadcast_lines(message)
    else:

        print(f"Broadcast: '{code};{message.strip()}' to all except: {blacklist}")
        global ALL_USERS

        if newline:
            message = message + "\n"
        msg_bytes = (f"{code};{message}").encode()
        #for name, (reader, writer) in ALL_USERS.items():
        #    writer.write(message.encode())
        #    await writer.drain()

        people = {}
        for n, (r, w) in ALL_USERS.items():
            if n not in blacklist:
                people[n] = (r, w)

        if people:
            tasks = [asyncio.create_task(send_message(w, msg_bytes)) for _, (_, w) in people.items()]
            await asyncio.wait(tasks)


async def connect_user(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    writer.write("INPUT;Enter nickname:\n".encode())
    name_bytes = await reader.readline()
    res = name_bytes.decode().strip()
    code, _, name = res.partition(';') 
    #p, g = randprime(2137, 50007), randprime(2137, 50007)
    #print(p, g)
    # writer.write(f"INFO DH BASE;{p}:{g}".encode())


    global ALL_USERS

    ALL_USERS[name] = (reader, writer)
    await broadcast_message(f"{name} joined the chat!", 'SEND', blacklist=[name])


    await send_message(writer, sys_msg['welcome'].encode())
    #await send_message(writer, sys_msg['welcome'].encode())
    return name

async def disconnect_user(name, writer):
    writer.close()
    await writer.wait_closed()

    global ALL_USERS
    del ALL_USERS[name]

    await broadcast_message(f"{name} disconnected", "SEND")

async def send_lines(w, lines_bytes):
    w.writelines(lines_bytes)
    await w.drain()

async def broadcast_lines(lines: list[str], code: str, newline: bool=True):
    e = "\n" if newline else ''
    lines[0] = f"{code};{lines[0]}"
    lines_bytes = list(map(lambda x: (x + e).encode(), lines))

    tasks = [asyncio.create_task(send_lines(w, lines_bytes)) for _, (_, w) in ALL_USERS.items()]
    await asyncio.wait(tasks)

async def handle_chat_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    print("Client connecting...")
    print(writer.can_write_eof())
    name = await connect_user(reader, writer)
    try:
        while True:
            line_bytes = await reader.readline()
            code, _, line = line_bytes.decode().partition(";")
            if not line.strip() and code == 'SEND':
                continue
            match code.strip():
                case 'QUIT':
                    break
                case 'LIST':
                    # await broadcast_message("\n".join(list(map(lambda n, (w, r): f"{n} ({w.get_extra_info()})", ALL_USERS.items()))))
                    # await broadcast_message(f"{name}: {line}", "SEND", blacklist=[name], newline=False)
                    #print(f"LIST by {name}:\n" + "\n".join([f"{n} ({r.get_extra_info('peername')})"
                    #                                          for n, (_, r) in ALL_USERS.items()]))
                    # await broadcast_message2(['a\n', 'b', 'c\n', 'd', 'abcba'])
                            #[f"{name}: LIST"] + [f"{n} ({r.get_extra_info('peername')})" for n, (_, r) in ALL_USERS.items()], "SEND")
                    peer_list = [f"{n:<16} | {w.get_extra_info('peername')[0]}:{w.get_extra_info('peername')[1]}"
                                 for n, (_, w) in ALL_USERS.items()]

                    peer_list = [f"{name}: LIST"] + peer_list
                    await broadcast_lines(peer_list, "SEND")
                    continue
                # case 'RESPONSE':
                case "SEND":
                    # await broadcast_message(line, 'SEND', blacklist=[name])
                    await broadcast_message(f"{name}: {line}", "SEND", blacklist=[name], newline=False)
                case "INFO DH PUB":
                    ...


    finally:
        
        await disconnect_user(name, writer)


async def main():

    host_addr, host_port = '', 50007

    server = await asyncio.start_server(handle_chat_client, host_addr, host_port)

    async with server:
        print("Running server forever")
        await server.serve_forever()

asyncio.run(main())
