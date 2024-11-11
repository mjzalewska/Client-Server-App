from prettytable import PrettyTable


class Display:
    @staticmethod
    def display_message(message):
        for item in message:
            for key, value in item.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        print(f"{subkey}: {subvalue}")
                elif isinstance(value, list):
                    Display.display_tables(message)
                else:
                    print(f"{value}")
            print()

    @staticmethod
    def display_tables(message):
        if not message:
            print("No data to display.")
            return
        data = message[0]["message"]
        columns = list(data[0].keys())[:4]
        table = PrettyTable(field_names=columns)
        for item in data:
            table.add_row(item.values())
        print(table)
