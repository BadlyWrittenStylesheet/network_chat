from ast import literal_eval
import asyncio
from typing import Literal, Any
from sympy import randprime
from dh import get_shared_key, get_public_key
from rsa_ed import generate_key_pair
from tools import await_message, encrypt_message, decrypt_message, format_to_send, parse_message, send, MUT, User

# USERS: dict[User, tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}
USERS = []

rsa_keys: dict[str, dict[Literal['user_public', 'server_public', 'server_private'], Any]] = {}
dh_keys: dict[str, dict[Literal['base', 'modulus', 'server_public', 'user_public', 'private', 'shared_key'], Any]] = {} 

min_prime, max_prime = 1000, 9999


async def exchange_keys(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> dict:
    storage: dict[Literal['base', 'modulus', 's_public_dh', 'u_public_dh', 'private_dh', 'shared', 'u_public_rsa', 's_public_rsa', 's_private_rsa'], Any] = {}

    # Define base and modulus for the DHKE
    base, modulus = randprime(min_prime, max_prime),  randprime(min_prime, max_prime)
    private_key = randprime(min_prime, max_prime)
    s_public_dh = get_public_key(base, private_key, modulus)

    storage['base'] = base
    storage['modulus'] = modulus
    storage['private_dh'] = private_key
    storage['s_public_dh'] = s_public_dh
    
    # RSA Server's public key
    p, q = randprime(min_prime, max_prime), randprime(min_prime, max_prime)
    s_public_rsa, s_private_rsa = generate_key_pair(p, q)

    storage['s_public_rsa'] = s_public_rsa
    storage['s_private_rsa'] = s_private_rsa
    

    message = f"""KEY_EXCHANGE
DH_BASE:{base}
DH_MOD:{modulus}
DH_KEY:{s_public_dh}
RSA_KEY:{s_public_rsa}
"""
    


    # print('storage', repr(storage))

    await send(writer, message.encode())

    message = await await_message(reader)
    method, data = parse_message(message.decode())
 
    if method != 'KEY_EXCHANGE':
        print("Wrong method?", method)
        return

    storage['u_public_dh'] = int(data['DH_KEY'])
    storage['u_public_rsa'] = literal_eval(data['RSA_KEY'])

    shared = get_shared_key(int(data['DH_KEY']), private_key, modulus)
    storage['shared'] = shared

    return storage
    
    



# Encrypt messaga with users public key and sign with a DH shared key
# def encrypt_message(public_key: tuple[int, int], signature: str, message: str):
#     encrypted_message = " ".join(map(
#         str, encrypt(
#             public_key, message + signature
#             )))
#     print("Encrypting:", message)

#     return encrypted_message


async def broadcast_message(message: str, blacklist=[]):
    print(f"Broadcasting")
    receivers = [(u.writer, mut) for u, mut in USERS if u.username not in blacklist]

    if receivers:
        tasks = [asyncio.create_task(send(w, mut.encrypt(message))) for w, mut in receivers]
        await asyncio.wait(tasks)

async def connect_user(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = f"{writer.get_extra_info('peername')[0]}:{writer.get_extra_info('peername')[1]}"
    print(f"Connected with: {addr}")
    storage = await exchange_keys(reader, writer)
    return storage





async def handle_chat_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    storage = await connect_user(reader, writer)
    # storage = {k: storage[k] for k in sorted(storage)}
    # print("\n".join([f"{k} : {v} ~ {type(v)}" for k, v in storage.items()]))
    print("User connected.")

    mut = MUT(storage['s_private_rsa'], storage['shared'], storage['u_public_rsa'])

    while True:
        message = await await_message(reader)
        # print("Received:", message)
        # message = decrypt_message(storage['s_private_rsa'], storage['shared'], message.decode())
        message = mut.decrypt(message.decode())
        if not message:
            continue
        method, data = parse_message(message)

        match method:
            case 'ACTION':
                match data['event']:
                    case 'set_username':
                        u = User(username=data['value'], ip=writer.get_extra_info('peername')[0], port=writer.get_extra_info('peername')[1], reader=reader, writer=writer, keys=storage)
                        USERS.append((u, mut))
                        msg = format_to_send('ACTION', event='user_join', name=u.username)
                        print(repr(msg))
                        await broadcast_message(msg, [u.username])
                    case 'send_public_message':
                        msg = format_to_send('ACTION', event='send_public_message', name=u.username, value=data['value'])
                        await broadcast_message(msg, [u.username])


            

async def main():
    addr, port = '', 50007
    server = await asyncio.start_server(handle_chat_client, addr, port)

    async with server:
        print("Server is running forever... forever... anyways copy the terminal to stop <3")
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
