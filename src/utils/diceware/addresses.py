from xdg_base_dirs import xdg_config_home
from random import choice
import random

DICE_TEXT_PATH = xdg_config_home() / "diceware" / "diceware.txt"
DICE_TEXT = DICE_TEXT_PATH.read_text().splitlines()
WORDS = [line.split("\t")[1] for line in DICE_TEXT]


FIRST_NAMES = [
    "Alex",
    "Jordan",
    "Taylor",
    "Morgan",
    "Casey",
    "Riley",
    "Avery",
]

LAST_NAMES = [
    "Rowan",
    "Parker",
    "Hayes",
    "Blake",
    "Quinn",
    "Reed",
]

STREET_NAMES = [
    "Oakfield",
    "Maplecrest",
    "Silverrun",
    "Pinehaven",
    "Clearbrook",
]

STREET_TYPES = ["St", "Ave", "Rd", "Ln", "Dr"]

CITIES = [
    ("Springfield", "IL"),
    ("Riverton", "UT"),
    ("Fairview", "TX"),
    ("Madison", "WI"),
    ("Franklin", "TN"),
]


STREET_TYPES = [
    "Boulevard",
    "Avenue",
    "Street",
    "Drive",
    "Court",
    "Place",
    "Lane",
    "Road",
    "Parkway",
]


def roll_dice() -> str:
    """Simulate rolling five six-sided dice and return the result as a string."""
    return choice(WORDS)


def generate_street_name(num_words: int = 2, separator: str = " ") -> str:
    """Generate a username by rolling dice to select words from the Diceware list.

    Args:
        num_words (int): Number of words to include in the username.
        separator (str): Separator to use between words.

    Returns:
        str: Generated username.
    """
    words = []
    while True:
        word = roll_dice()
        if word not in words:
            words.append(word)
        if len(words) == num_words:
            break

    # Capitalize the words, and add a random street type, a la "Willow Jump Lane"
    words = [word.capitalize() for word in words]
    street_type = choice(STREET_TYPES)
    words.append(street_type)
    return separator.join(words)


def fake_zip() -> str:
    # 00000 and 99999 are invalid/unassigned ZIP codes
    return choice(["00000", "99999"])


def generate_address() -> dict[str, str]:
    first = choice(FIRST_NAMES)
    last = choice(LAST_NAMES)
    street_number = str(random.randint(100, 9999)).strip()
    street = generate_street_name(num_words=2, separator=" ")
    city, state = choice(CITIES)

    return {
        "name": f"{first} {last}",
        "street": f"{street_number} {street}",
        "city": city,
        "state": state,
        "zip": fake_zip(),
        "country": "USA",
    }


def main():
    address = generate_address()
    print(f"{address['name']}")
    print(f"{address['street']}")
    print(f"{address['city']}, {address['state']} {address['zip']}")
    print(f"{address['country']}")


if __name__ == "__main__":
    main()
