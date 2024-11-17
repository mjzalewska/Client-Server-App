from os import system, name
import json


def clr_screen():
    """
    clears terminal screen
    :return: None
    """
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


def load_menu_config(menu_type, state, user_type, filepath="menu_config.json"):
    with open(filepath, "r") as config_file:
        menu = json.load(config_file)[menu_type][state][user_type]
        return menu
