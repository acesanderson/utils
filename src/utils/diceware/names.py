from xdg_base_dirs import xdg_config_home
from random import choice

DICE_TEXT_PATH = xdg_config_home() / "diceware" / "names.txt"
DICE_TEXT = DICE_TEXT_PATH.read_text().splitlines()
FIRST_NAMES = [line.split("\t")[0] for line in DICE_TEXT]
SURNAMES = [line.split("\t")[1] for line in DICE_TEXT]


def generate_name(num_words: int = 2, separator: str = " ") -> str:
    """Generate a username by rolling dice to select words from the Diceware list."""
    first_name = choice(FIRST_NAMES)
    surname = choice(SURNAMES)
    return separator.join([first_name, surname])


def main():
    print(generate_name())


if __name__ == "__main__":
    main()
