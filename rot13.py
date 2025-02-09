def rot13(text):
    # Create the translation table
    input_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    output_chars = "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"
    trans_table = str.maketrans(input_chars, output_chars)

    # Apply the translation
    return text.translate(trans_table)
