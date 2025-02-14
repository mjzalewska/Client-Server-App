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
                    Display.display_table(message)
                    print()
            except (ValueError, TypeError):
                logging.error(f"Error displaying message data")
                print(f"Error displaying message")

    @staticmethod
    def display_table(message):
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
        inbox_columns = ["#", "SENDER", "SUBJECT", "DATE"]
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

    @staticmethod
    def display_email(email_num, message):
        if not message or not message.get("data"):
            print("No data to display")
            return
        inbox = message["data"][0]
        if not inbox:
            print("No messages to display")
            return
        messages = list(inbox.values())[0]
        for field_name, field in messages[Display._map_email_id(email_num, messages)].items():
            print(f"{field_name.title()}: {field}")

    @staticmethod
    def _map_email_id(email_num, messages_dict):
        message_id_mapping = {num + 1: item for num, item in enumerate(list(messages_dict.keys()))}
        for key in message_id_mapping.keys():
            if key == email_num:
                return message_id_mapping[key]
