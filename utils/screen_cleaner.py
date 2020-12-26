import os


def screen_cleaner():
    os.system('cls' if os.name == 'nt' else 'clear')
