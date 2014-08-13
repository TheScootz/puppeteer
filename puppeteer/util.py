import random

def convert_qmarks(raw):
    converted = raw
    while converted.count("?"):
        converted = converted.replace("?", str(random.randint(0,9)), 1)
    return converted

