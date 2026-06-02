import re
import string
import random


def generate_symbols(length: int = 7, use_numbers: bool = True):
    characters = (
        string.ascii_letters + string.digits if use_numbers else string.ascii_letters
    )
    return "".join(random.choice(characters) for _ in range(length))


def has_cyrillic(text):
    return bool(re.search("[а-яА-Я]", text))
