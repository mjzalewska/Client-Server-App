import logging
from prettytable import PrettyTable


class Display:
    @staticmethod
    def display_message(message):
        if message.get("message"):
            print()
            print(message["message"])
        if message.get("data"):
            try:
                data_content, display_type = message["data"]
                if display_type == "list" and data_content:
                    for key, value in data_content.items():
                        print(f"{key}: {value}")
                    print()
                elif display_type == "tabular" and data_content:
                    Display.display_tables(message)
                    print()
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

    @staticmethod
    def display_inbox(message):
        if not message or not message.get("data"):
            print("No data to display")
            return
        messages = message["data"][0]
        if not messages:
            print("No messages to display")
            return
        inbox_columns = [" ", "SENDER", "SUBJECT", "DATE"]
        table = PrettyTable(field_names=inbox_columns)
        message_number = 1
        for message in messages.values():
            for message_data in message.values():
                table.add_row([
                    message_number,
                    message_data["sender"],
                    message_data["subject"],
                    message_data["timestamp"]
                ])
                message_number += 1
        table.max_width = 30
        table.hrules = True
        print(table)
