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
            cache = [eval(line.rstrip(",")) for line in db.read().splitlines()]
            for record in cache:
                if record["username"] == user_name:
                    record[key] = new_key_val
                else:
                    pass
            db.truncate(0)
            for new_record in cache:
                cls.add(db_name, new_record, "a+")
    @classmethod
    def remove(cls, db_name, user_name):
        updated_records = []
        with open(db_name, "r+", encoding="utf-8") as db:
            cache = [eval(line.rstrip(",")) for line in db.read().splitlines()]
            for record in cache:
                if record["username"] != user_name:
                    updated_records.append(record)
                else:
                    pass
            db.truncate(0)
            for record in updated_records:
                cls.add(db_name, record, "a+")

    @classmethod
    def fetch(cls, db_name, user_name):
        with open(db_name, "r+") as db:
            cache = [eval(line.rstrip(",")) for line in db.read().splitlines()]
            return [record for record in cache if record["username"] == user_name]



# DbManager.add("users.json", {"username": "johnny_boy", "password": "strongpass123", "inbox": []}, "a+")
# DbManager.add("users.json", {"username": "johnny_gal", "password": "strongpass456", "inbox": []}, "a+")
# DbManager.add("users.json", {"username": "vito_bambino", "password": "strongpass456", "inbox": []}, "a+")
# DbManager.remove("users.json", "bunny_man")
# DbManager.create_db()
# DbManager.update("users.json", "johnny_gal", "username", "bunny_man")
# print(DbManager.fetch("users.json", "johnny_gal"))