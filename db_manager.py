import json
import os


class DbManager:
    db_file = "users.json"

    @classmethod
    def save(cls, username, user_data):
        if os.path.exists(cls.db_file):
            with open(cls.db_file, 'r') as db:
                try:
                    existing_data = json.load(db)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        existing_data[username] = user_data

        with open(cls.db_file, 'w') as db:
            json.dump(existing_data, db, indent=4)

    @classmethod
    def delete(cls, username):
        try:
            if os.path.exists(cls.db_file):
                updated_data = {}
                with open(cls.db_file, "r", encoding="utf-8") as current_db:
                    try:
                        current_data = json.load(current_db)
                        removed_items = 0
                        for user, user_data in current_data.items():
                            if user != username:
                                updated_data[user] = user_data
                            else:
                                removed_items += 1
                    except json.JSONDecodeError:
                        updated_data = []
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            return FileNotFoundError
        except Exception as e:
            return e

        with open(cls.db_file, 'w') as new_db:
            json.dump(updated_data, new_db, indent=4)
            return {"message": f"Deleted {removed_items} record(s)"}

    @classmethod
    def get(cls, username=None):
        try:
            if os.path.exists(cls.db_file):
                with open(cls.db_file, "r", encoding="utf-8") as db:
                    try:
                        users = json.load(db)
                        if username is None:
                            return users
                        else:
                            return users[username]
                    except json.JSONDecodeError:
                        return []
                    except KeyError:
                        return KeyError
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            return FileNotFoundError
        except Exception as e:
            return e


print(DbManager.delete("user1"))
