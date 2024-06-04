import asyncio
import sys
from sympy import randprime
import random
import hashlib
from ast import literal_eval
from typing import Literal
from dh import get_shared_key, get_public_key
from rsa_ed import generate_key_pair, encrypt, decrypt

from tools import decrypt_message, format_to_send, send, encrypt_message, parse_message, send, await_message, MUT, User

min_prime, max_prime = 1000, 9999
# from tools import serialize, deserialize









async def exchange_keys(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> dict:
    # DODAC TYP!!!
    storage = {}
    message = await await_message(reader)
    method, data = parse_message(message.decode())
    
    if method != 'KEY_EXCHANGE':
        print("Wrong method?", method)
        return

    # Diffie Helman Diffie Helman Diffie Helman Diffie Helman Diffie Helman
    # Diffie Helman Diffie Helman Diffie Helman Diffie Helman Diffie Helman

    private_key = randprime(min_prime, max_prime)

    base = int(data['DH_BASE'])
    modulus = int(data['DH_MOD'])
    s_public_dh = int(data['DH_KEY'])
    s_public_rsa = literal_eval(data['RSA_KEY'])

    storage['base'] = base
    storage['modulus'] = modulus
    storage['private_dh'] = private_key
    storage['s_public_dh'] = s_public_dh

    u_public_dh = get_public_key(base, private_key, modulus)
    storage['u_public_dh'] = u_public_dh

    shared = get_shared_key(s_public_dh, private_key, modulus)
    storage['shared'] = shared

    # RSA stuff
    
    # Servers
    storage['s_public_rsa'] = s_public_rsa
    # print("uuuu", s_public_rsa, type(s_public_rsa))

    # User
    p, q = randprime(min_prime, max_prime), randprime(min_prime, max_prime)
    u_public_rsa, u_private_rsa = generate_key_pair(p, q)

    storage['u_public_rsa'] = u_public_rsa
    storage['u_private_rsa'] = u_private_rsa
    
    

    message = f"""KEY_EXCHANGE
DH_KEY:{u_public_dh}
RSA_KEY:{u_public_rsa}"""

    await send(writer, message.encode())
    return storage
    



    
    

async def receive_messages(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, storage):
    while True:
        result = await await_message(reader)
        if not result: continue
        # print("RESULT", repr(result))

        message = decrypt_message(storage['u_private_rsa'], storage['shared'], result.decode())
        if not message:
            print("bad message")
            continue
        method, data = parse_message(message)

        match method:
            case 'ACTION':
                match data['event']:
                    case 'user_join':
                        print(f"Welcome to chat {data['name']}!!!")
                    case 'send_public_message':
                        print(f"{data['name']}: {data['value']}")
                    case 'user_leave':
                        print(f"{data['name']} left the chat unfortunately.")
            case 'DATA':
                match data['request']:
                    case 'list':
                        print("\n".join(literal_eval(data['value'])))
                        # print(literal_eval(data['value']))


        # print("received", result)

        
        # print(method, data)

async def read_messages(reader, writer, storage):
    mut = MUT(storage['u_private_rsa'], storage['shared'], storage['s_public_rsa'])
    while True:
        message = await asyncio.to_thread(input)
        pairs = {}
        if not message: continue
        match message:
            case '/quit':
                method = 'ACTION'
                pairs['event'] = 'user_leave'
                pairs['value'] = message
            case '/list':
                method = 'DATA'
                pairs['request'] = "list"

            case _:
                method = 'ACTION'
                pairs['event'] = 'send_public_message'
                pairs['value'] = message
        # msg = encrypt_message(storage['s_public_rsa'], storage['shared'], format_to_send('ACTION', event='send_public_message', value=message))
        msg = mut.encrypt(mut.format(method, **pairs))
        await send(writer, msg)
        if message == '/quit': break



async def connect_to_server(server_host, server_port):# -> tuple[asyncio.StreamReader, asyncio.StreamWriter, dict]:
    reader, writer = await asyncio.open_connection(server_host, server_port)
    # print("Exchanging keys")
    storage = await exchange_keys(reader, writer)
    # print("Keys exchanged")
    name = "Anonymous#" + hashlib.md5(str(random.choice(list(storage.values()))).encode()).hexdigest()[::2]
    input(f"Your name is {name}, can't change it <3... *psst* click <enter> to proceed!")
    await send(writer, encrypt_message(storage['s_public_rsa'], str(storage['shared']), format_to_send('ACTION', event='set_username', value=name)))

    return name, reader, writer, storage

async def main():
    try:
        server_host, server_port = '127.0.0.1', 50007
        # reader, writer = await asyncio.open_connection()
        
        name, reader, writer, storage = await connect_to_server(server_host, server_port)
        storage = {k: storage[k] for k in sorted(storage)}
        # print("\n".join([f"{k} : {v} ~ {type(v)}" for k, v in storage.items()]))
        print("Connection established")

        receive_task = asyncio.create_task(receive_messages(reader, writer, storage))
        await read_messages(reader, writer, storage)

        receive_task.cancel()
        print("HATE RAISING ERRORS")

        await asyncio.sleep(3)

        
        writer.close()
        await writer.wait_closed()

            # from_stdin = sys.stdin.readline()
            # if from_stdin.strip() == 'q':
            #     break
        print("Quittin'")
    except ConnectionRefusedError:
        print("Failed to establish connection, check if the host is online and try again.")


if __name__ == '__main__':
    asyncio.run(main())
