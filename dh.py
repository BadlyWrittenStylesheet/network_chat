def mod_exp(base: int, exponent: int, modulus: int) -> int:
    result = 1
    while exponent > 0:
        if exponent & 1 == 1:
            result = (result * base) % modulus
        base = (base**2) % modulus
        exponent //= 2
    return result

def get_shared_key(A: int, b: int, p: int) -> int:
    return mod_exp(A, b, p)

def get_public_key(g: int, a: int, p: int) -> int:
    return mod_exp(g, a, p)

# p, g = 23, 5

# a = random.randint(1, p-2)
# b = random.randint(1, p-2)
# A = mod_exp(g, a, p)
# B = mod_exp(g, b, p)

# shared_a = get_shared_key(A, b, p)
# shared_b = get_shared_key(B, a, p)
# print(a, b)
# print(A, B)
# print(shared_a, shared_b)
