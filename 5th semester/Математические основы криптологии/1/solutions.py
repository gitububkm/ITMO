from math import gcd
from random import randint


def task1_mod():
    """Return remainder of task 1 expression modulo 47."""
    mod = 47
    term1 = (pow(6, 93, mod) * pow(8, 90, mod)) % mod
    term2 = (pow(50, 12, mod) * pow(90, 10, mod)) % mod
    return (term1 + term2) % mod


def base13_to_int(digits):
    """Convert a base-13 string to an integer."""
    table = {ch: i for i, ch in enumerate("0123456789ABC")}
    value = 0
    for ch in digits.upper():
        value = value * 13 + table[ch]
    return value


def task2_check():
    """Check divisibility of the given base-13 number by 18."""
    number_13 = "2131BB9BCA"
    value = base13_to_int(number_13)
    return value, value % 18 == 0


def task3_gcd(n):
    """Compute gcd of numerator and denominator for task 3."""
    num = 50 * n * n + 70 * n + 4
    den = 100 * n * n + 150 * n + 9
    return gcd(num, den)


def task3_scan(limit=200):
    """Search for n with gcd > 1 within [-limit, limit]."""
    for n in range(-limit, limit + 1):
        g = task3_gcd(n)
        if g != 1:
            return n, g
    return None, 1


def task4_random_check(samples=1000, span=10**4):
    """
    Empirically confirm the gcd identity for random odd triples.

    Returns True if every sampled triple satisfied the identity.
    """
    for _ in range(samples):
        a = 2 * randint(-span, span) + 1
        b = 2 * randint(-span, span) + 1
        c = 2 * randint(-span, span) + 1
        left = gcd(gcd((a + b) // 2, (a + c) // 2), (b + c) // 2)
        right = gcd(gcd(a, b), c)
        if left != right:
            return False
    return True


if __name__ == "__main__":
    print(f"Task 1 remainder mod 47: {task1_mod()}")

    value, divisible = task2_check()
    print(f"Task 2 value in decimal: {value}")
    print(f"Task 2 divisible by 18? {divisible}")

    witness, g = task3_scan()
    if witness is None:
        print("Task 3: gcd is 1 for all tested n in [-200, 200]")
    else:
        print(f"Task 3: n={witness} gives gcd={g} (>1)")

    print(f"Task 4 identity holds for random tests? {task4_random_check()}")

