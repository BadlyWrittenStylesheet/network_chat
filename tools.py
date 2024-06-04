import struct
from dataclasses import dataclass
import asyncio
from rsa_ed import encrypt, decrypt
from typing import Literal, Any

def serialize(key: int | tuple[tuple[int, int], tuple[int, int]]):
    serialized = b''
    if isinstance(key, int):
        return struct.pack('!I', key)
    return struct.pack('!IIII', key)
    # for t in key:
    #     for n in t:
    #         serialized += struct.pack('!I', n)
    # return serialized

def deserialize(serialized: bytes) -> tuple[int, ...]: # Beautiful

    try:
        key = struct.unpack('!IIII', serialized)


        return key

    except struct.error:
        return struct.unpack('!I', serialized)[0]
    except Exception as e:
        print(str(e))


async def send(writer, message: str | bytes):
    # print(f"Sending: {repr(message)}")
    if isinstance(message, str):
        message = message.encode()
    writer.write(message)
    await writer.drain()

def encrypt_message(public_key: tuple[int, int], signature: str | int, message: str):
    signature = str(signature)
    encrypted_message = " ".join(map(
        str, encrypt(
            public_key, message + signature
            )))
    # print("Encrypting:", encrypted_message)

    return encrypted_message

def decrypt_message(private_key: tuple[int, int], signature: str | int, cipher: str):
    if isinstance(signature, int): signature = str(signature)
    try:
        decrypted = decrypt(private_key, list(map(int, cipher.split(" "))))
        if not decrypted.endswith(signature):
            return False
        # print("Decrypted:", repr(decrypted))
        return decrypted.removesuffix(signature)
    except Exception as e:
        print(str(e))


async def await_message(reader: asyncio.StreamReader):
    result = await reader.read(2137)
    return result

                                                                                                                                                                                                                                                     
def parse_message(message: bytes | str):
    if isinstance(message, bytes):
        message = message.decode()
    d = message.strip()
    d = d.split("\n")

    # split_data = message.strip().split("\n")
    method, data = d[0], d[1:]
    # method, data = split_data[0], split_data[1:]

    arguments = list(map(lambda x: x.split(":"), data))
    arguments = {k: v for k, v in arguments}
    # print(f"Parsed: '{method=}' '{arguments=}'")

    return method, arguments


# Send message
async def send(writer, message: str | bytes):
    # print(f"Sending: {repr(message)}")
    if isinstance(message, str):
        message = message.encode()
    writer.write(message)
    await writer.drain()


@dataclass
class User:
    """ I do indeed love static typing """
    username: str
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    keys: dict[Literal['base', 'modulus', 's_public_dh', 'u_public_dh', 'private_dh', 'shared', 'u_public_rsa', 's_public_rsa', 's_private_rsa'], Any]
    ip: str | None = None
    port: int | None = None


class MUT:
    def __init__(self, my_private_rsa, signature, their_public_rsa):
        self.my_private_rsa = my_private_rsa
        self.signature = signature 
        self.their_public_rsa = their_public_rsa
    def encrypt(self, message):
        return encrypt_message(self.their_public_rsa, self.signature, message)

    def decrypt(self, message):
        return decrypt_message(self.my_private_rsa, self.signature, message)

    def format(self, method, **values):
        return format_to_send(method, **values)


def format_to_send(method: str, **values):
    # formatted = f"{method}{'\n'}{'\n'.join([f'{k}:{v}' for k, v in values])}"
    formatted = method + "\n" + "\n".join({f'{k}:{v}' for k, v in values.items()})
    # print("Formatted:", formatted)
    return formatted

