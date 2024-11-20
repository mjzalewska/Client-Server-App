from prettytable import PrettyTable


class Display:
    @staticmethod
    def display_message(message):
        print(message)
        if message["event_type"] in ["exit_to_main_menu"]:
            pass
        else:
            print(message["message"])
            if message["data"]:
                for key, value in message["data"].items(): # różnicowaanie "data" na tables in nie tables przez eventy?
                    print(f"{key}: {value}")


        #         if isinstance(value, dict):
        #             for subkey, subvalue in value.items():
        #                 print(f"{subkey}: {subvalue}")
        #         elif isinstance(value, list):
        #             Display.display_tables(message)
        #         else:
        #             print(f"{value}")
        #     print()

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
