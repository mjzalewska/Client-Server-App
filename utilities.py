from os import system, name


def clr_screen():
    """
    clears terminal screen
    :return: None
    """
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

