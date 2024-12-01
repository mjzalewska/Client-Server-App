from prettytable import PrettyTable


class Display:
    @staticmethod
    def display_message(message):
        if message["event"] == "return":
            pass
        else:
            print(message["message"])
            if message["data"]:
                if message["data"][1] == "list":
                    for key, value in message["data"][0].items():
                        print(f"{key}: {value}")
                elif message["data"][1] == "tabular":
                    Display.display_tables(message)
        print()

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
