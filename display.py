from prettytable import PrettyTable


class Display:
    @staticmethod
    def display_message(message):
        try:
            if message.get("message"):
                print(message["message"])
            if message.get("data") and isinstance(message["data"], tuple):
                data_content, display_type = message["data"]
                if display_type == "list" and data_content:
                    for key, value in data_content.values():
                        print(f"{key}: {value}")
                elif display_type == "tabular" and data_content:
                    Display.display_tables(message)
        except Exception as e:
            print(f"Error displaying message: {str(e)}")

    @staticmethod
    def display_tables(message):
        if not message:
            print("No data to display.")
            return
        data = message["data"][0]
        columns = ["username", "password_hash", "email", "role"]
        table = PrettyTable(field_names=columns)
        for username, user_data in data.items():
            record = [username]
            data = [value for value in user_data.values()]
            record.extend(data)
            table.add_row(record)
        print(table)
