import json


class DbManager:

    @classmethod
    def add(cls, record):
        with open("db_file.txt", "a+") as db:
            json.dump(record + "\n", db)
            print("New record added")

    @classmethod
    def remove(cls, username):
        new_db_file = {}
        with open("db_file.txt", "r+") as db:
            db_file = json.load(db)
            for key in db_file.keys():
                if key != username:
                    new_db_file[key] = db_file[key]
                else:
                    print(f"Removed user: {username}")
        with open("db_file.txt", "w+") as db:
            json.dump(new_db_file, db)

    @classmethod
    def fetch(cls, username):
        with open("db_file.txt", "r+") as db:
            db_file = json.load(db)
            for key in db_file.keys():
                if key == username:
                    return db_file[key]
                else:
                    return None
