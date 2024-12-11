import logging
from prettytable import PrettyTable


class Display:
    @staticmethod
    def display_message(message):
        if message.get("message"):
            print(message["message"])
        if message.get("data"):
            try:
                data_content, display_type = message["data"]
                if display_type == "list" and data_content:
                    for key, value in data_content.items():
                        print(f"{key}: {value}")
                elif display_type == "tabular" and data_content:
                    Display.display_tables(message)
            except (ValueError, TypeError):
                logging.error(f"Error displaying message data")
                print(f"Error displaying message")

    @staticmethod
    def display_tables(message):
        if not message or not message.get("data"):
            print("No data to display")
            return
        data = message["data"][0]
        if not data:
            print("No records found.")
            return
        sample_record = next(iter(data.values()))
        columns = ["username"] + list(sample_record.keys())
        table = PrettyTable(field_names=columns)
        for username, user_data in data.items():
            record = [username] + list(user_data.values())
            table.add_row(record)
        table.max_width = 30
        table.hrules = True
        print(table)
