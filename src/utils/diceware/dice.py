from xdg_base_dirs import xdg_config_home
from random import choice

DICE_TEXT_PATH = xdg_config_home() / "diceware" / "diceware.txt"
DICE_TEXT = DICE_TEXT_PATH.read_text().splitlines()
WORDS = [line.split("\t")[1] for line in DICE_TEXT]


def roll_dice() -> str:
    """Simulate rolling five six-sided dice and return the result as a string."""
    return choice(WORDS)


def generate_username(num_words: int = 2, separator: str = "") -> str:
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
    return separator.join(words)


def main():
    print(generate_username())


if __name__ == "__main__":
    main()
