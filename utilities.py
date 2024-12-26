from datetime import datetime, timedelta
from os import system, name
import json


def clr_screen():
    """clears terminal screen"""
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


def get_user_input(comm_handler, fields):
    """Generic function to get user input for specified fields"""
    user_data = {}
    for field in fields:
        comm_handler.send(f"Enter {field}: ")
        user_data[field] = comm_handler.receive()["message"]
    return user_data


def load_menu_config(menu_type, state, user_type, filepath="menu_config.json"):
    """Load menu configuration from a json config file"""
    with open(filepath, "r") as config_file:
        menu = json.load(config_file)[menu_type][state][user_type]
        return menu


def calculate_uptime(start_time):
    """Calculate and return server uptime from start time"""
    request_time = datetime.now()
    time_diff = (request_time - start_time).seconds
    uptime_val = str(timedelta(seconds=time_diff))
    return uptime_val


def format_server_info(version, build_date):
    """Format server information string"""
    return f"version: {version}, build: {build_date}"
