from prettytable import PrettyTable


class Display:
    @staticmethod
    def display_message(message):
        if message["event"] in ["exit_to_main_menu"]:
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
        data = message["data"]
        columns = list(data.keys())[:4]
        table = PrettyTable(field_names=columns)
        for item in data:
            table.add_row(item.values())
        print(table)
