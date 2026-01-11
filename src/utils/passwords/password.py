"""
Generates cryptographically secure random passwords with guaranteed character diversity. This script provides a simple utility for creating strong passwords that meet minimum complexity requirements (uppercase, lowercase, digits, and special characters) with cryptographic randomness to prevent predictability.

The `gen_password()` function assembles a password by first selecting one character from each required character class using the `secrets` module, then filling the remainder of the desired length with random selections from the combined character pool, and finally shuffling to eliminate any structural patterns. The script can be used as a library or invoked directly from the command line with an optional length argument.

Usage:
```python
from utils.passwords import gen_password

# Generate default 16-character password
password = gen_password()

# Generate custom-length password
password = gen_password(length=24)
```
"""

import secrets
import string
import random
import sys

LENGTH = 16
SPECIALS = "!@$%-_"

if LENGTH < 4:
    raise ValueError("Password length must be at least 4")


def gen_password(length: int = LENGTH) -> str:
    if length < 4:
        raise ValueError("length must be >= 4")

    # Required characters (guaranteed)
    chars = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice(SPECIALS),
    ]

    # Remaining characters
    all_chars = string.ascii_letters + string.digits + SPECIALS
    remaining = length - len(chars)

    chars.extend(secrets.choice(all_chars) for _ in range(remaining))

    # Shuffle to remove structure
    random.SystemRandom().shuffle(chars)

    return "".join(chars)


def main():
    length = LENGTH

    if len(sys.argv) == 2:
        try:
            length = int(sys.argv[1])
        except ValueError:
            print("Usage: gen_password.py [length]", file=sys.stderr)
            sys.exit(1)

    print(gen_password(length))


if __name__ == "__main__":
    main()
