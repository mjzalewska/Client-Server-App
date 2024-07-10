import json


class DbManager:

    @classmethod
    def add(cls, db_name, data, flag):
        with open(db_name, flag, encoding="utf-8") as db:
            db.write(json.dumps(data))
            db.write("\n")

    @classmethod
    def update(cls, db_name, user_name, key, new_key_val):
        with open(db_name, "r+", encoding="utf-8") as db:
            cache = [eval(line) for line in db.read().splitlines()]
            for record in cache:
                if record["username"] == user_name:
                    record[key] = new_key_val
                else:
                    pass
            db.truncate(0)
            for new_record in cache:
                cls.add(db_name, new_record, "a+")
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


# DbManager.add("users.json", {"username": "johnny_boy", "password": "strongpass123", "inbox": []}, "a+")
# DbManager.add("users.json", {"username": "johnny_gal", "password": "strongpass456", "inbox": []}, "a+")
# DbManager.add("users.json", {"username": "vito_bambino", "password": "strongpass456", "inbox": []}, "a+")
# DbManager.remove("johnny_boy")
# DbManager.create_db()
DbManager.update("users.json", "johnny_gal", "username", "bunny_man")
