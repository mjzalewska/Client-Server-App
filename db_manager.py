import json


class DbManager:

    @classmethod
    def add(cls, data):
        with open("users.txt", "a+", encoding="utf-8") as db:
            record = json.dumps(data)
            db.write(record)
            db.write(",\n")
            print("New record added")

    @classmethod
    def update(cls, user_name, new_data):
        pass

    @classmethod
    def remove(cls, username):
        new_db_file = []
        with open("users.txt", "r+") as db:
            for line in db.readlines():
                record = json.loads(line.replace(",\n", ""))
                if record["username"] != username:
                    new_db_file.append(record)
                else:
                    pass

        with open("users.txt", "w+") as db:
            for item in new_db_file:
                record = json.dumps(item)
                db.write(record)
                db.write(",\n")
            print(f"Removed user: {username}")

    @classmethod
    def fetch(cls, username):
        with open("users.txt", "r+") as db:
            for line in db.readlines():
                record = json.loads(line.replace(",\n", ""))
                if record["username"] == username:
                    return line
                else:
                    return None


# DbManager.add({"username": "johnny_boy", "password": "strongpass123", "inbox": {}})
# DbManager.add({"username": "johnny_gal", "password": "strongpass456", "inbox": {}})
# DbManager.add({"username": "vito_bambino", "password": "strongpass456", "inbox": {}})
# DbManager.remove("johnny_boy")
