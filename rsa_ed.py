from secrets import choice


def gcd(a: int, b: int):
    while b != 0:
        a, b = b, a % b
    return a


def multiplicative_inverse(e: int, phi: int):
    d, x1, x2, y1 = 0, 0, 1, 1
    tmp_phi = phi

    while e > 0:
        tmp1 = tmp_phi // e
        tmp2 = tmp_phi - tmp1 * e

        tmp_phi = e
        e = tmp2

        x = x2 - tmp1 * x1
        y = d - tmp1 * y1

        x2 = x1
        x1 = x
        d = y1
        y1 = y
    if tmp_phi == 1:
        return d + phi
    return -1  # Typing ehhh


def is_prime(n: int):
    if n == 2:
        return True
    if n < 2 or n % 2 == 0:
        return False
    for i in range(3, int(n ** .5) + 2, 2):
        if n % i == 0:
            return False
    return True


def generate_key_pair(p: int, q: int) -> tuple[tuple[int, int], tuple[int, int]]:
    # they wont ok?
    if not is_prime(p) or not is_prime(q):
        raise ValueError("p and q must be prime")
    elif p == q:
        raise ValueError("p and q cant be equal")

    n = p * q

    phi = (p - 1) * (q - 1)

    e = choice(range(1, phi))

    g = gcd(e, phi)
    while g != 1:
        e = choice(range(1, phi))
        g = gcd(e, phi)

    d = multiplicative_inverse(e, phi)

    return ((e, n), (d, n))


def encrypt(public_key: tuple[int, int], plain: str) -> list[int]:
    key, n = public_key

    cipher = [pow(ord(char), key, n) for char in plain]

    return cipher


def decrypt(private_key: tuple[int, int], cipher: list[int]) -> str:
    key, n = private_key

    aux = [str(pow(char, key, n)) for char in cipher]

    plain = [chr(int(char)) for char in aux]

    return ''.join(plain)

# p, q = sympy.randprime(1, 100), sympy.randprime(1, 100)

# pub, pri = generate_key_pair(p, q)

# message = input("msg?: ")
# encrypted = encrypt(pub, message)

# print(encrypted)

# decrypted = decrypt(pri, encrypted)
# print(decrypted)
