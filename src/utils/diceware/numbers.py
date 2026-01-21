def generate_number() -> str:
    """Generate a plausible phone number."""
    import random

    area_code = random.randint(100, 999)
    central_office_code = random.randint(100, 999)
    line_number = random.randint(1000, 9999)

    return f"({area_code}) {central_office_code}-{line_number}"


def main():
    print(generate_number())


if __name__ == "__main__":
    main()
