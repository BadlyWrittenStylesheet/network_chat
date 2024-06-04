import asyncio
import sys
from typing import Literal
from sympy import randprime
from rsa_ed import generate_key_pair, encrypt, decrypt

from dh import mod_exp, get_shared_key, get_public_key


data = {}
user_dh: dict[Literal['base', 'modulus', 'a_public', 'b_public', 'private', 'shared'], int] = {}
user_rsa: dict[Literal['s_public', 'u_public', 'u_private'], tuple[int, int]] = {}

sys_msg = {
    'help': "H-Help?\n'QUIT' to exit chat\n'LIST' list all users with ip\n'HELP' to show this wonderful message"
}

async def send_message(writer: asyncio.StreamWriter, message: str, newline=True):
    message += "\n" if newline else ''
    msg_bytes = message.encode()
    writer.write(msg_bytes)
    await writer.drain()

async def send_encrypted(writer, message, public_key, newline=True):
    message = " ".join(map(str, encrypt(public_key, message + str(user_dh['shared']))))
    print(message)
    await send_message(writer, message, newline)

async def read_message(writer):
    while True:
        message = await asyncio.to_thread(sys.stdin.readline)
        
        # if not user_rsa: continue
        if 'name' not in data.keys():
            data['name'] = message.strip()
            await send_message(writer, f"SEND;{message.strip()}")
            continue
        match message.strip():
            case "QUIT":
                await send_encrypted(writer, "QUIT", user_rsa['s_public'])
                break
            case "LIST":
                await send_encrypted(writer, "LIST", user_rsa['s_public'])
            case "HELP":
                print(sys_msg['help'])
            case 'DH':
                print(user_dh)
            case _:
                if user_rsa:
                    await send_encrypted(writer, f"SEND;{message.strip()}", user_rsa['s_public'])
                else:
                    await send_message(writer, f"SEND;{message.strip()}")

    print("Exiting...")

async def receive_messages(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while True:
        result: bytes = await reader.read(2137)

        code, _, content = result.decode().partition(";")
        if not content: continue

        #print(code, content, "bruh")
        try:
            code = decrypt(user_rsa['u_private'], list(map(int, code.split(" "))))
            content = decrypt(user_rsa['u_private'], list(map(int, code.split(" "))))
            print(1, code, content)
        except Exception as e:
            print("Sth wrnt wrong when decrypting oopsies!", str(e))
        print("code and content: ", code, content)
        match code:
            case 'SEND':
                print(content.strip())
            case 'INPUT':
                print(content.strip())
            case "INFO DH BASE":
                print("Initializing Key Exchange Protocol...")
                # print('info dh base c')
                p, g = map(int, content.split(':'))
                user_dh['modulus'], user_dh['base'] = p, g

                user_dh['private']: int = randprime(2137, 50007)

                user_dh['b_public'] = get_public_key(g, user_dh['private'], p)

                await send_message(writer, f"INFO DH U_PUB;{user_dh['b_public']}")
            case "INFO DH S_PUB":
                user_dh['a_public'] = int(content)
                user_dh['shared'] = get_shared_key(user_dh['a_public'], user_dh['private'], user_dh['modulus'])

                p, q = randprime(2137, 50007), randprime(2137, 50007)

                
                # Here works.
                print("Exchanging public keys")
                public_key, private_key = generate_key_pair(p, q)
                user_rsa['u_public'], user_rsa['u_private'] = public_key, private_key

                await send_message(writer, f"INFO RSA U_PUB;{user_rsa['u_public'][0]}:{user_rsa['u_public'][1]}")

            case "INFO RSA S_PUB":
                a, b = map(int, content.split(":"))
                user_rsa['s_public'] = (a, b)

                print("Up and running securely ;)")

                
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

        read_task = asyncio.create_task(receive_messages(reader, writer))

        await read_message(writer)

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

