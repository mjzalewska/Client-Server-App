import json
import os


class DbManager:
    db_file = "users.json"

    @classmethod
    def _read_data(cls):
        """Helper method to read data from the database."""
        if os.path.exists(cls.db_file):
            with open(cls.db_file, "r", encoding="utf-8") as db:
                try:
                    return json.load(db)
                except json.JSONDecodeError:
                    return {}
        return {}

    @classmethod
    def _write_data(cls, data):
        """Helper method to write data to the database."""
        with open(cls.db_file, "w", encoding="utf-8") as db:
            json.dump(data, db, indent=4)

    @classmethod
    def save(cls, key, value):
        """Save or update a record in the database"""
        data = cls._read_data()
        data[key] = value
        cls._write_data(data)

    @classmethod
    def delete(cls, key):
        """Delete a record."""
        data = cls._read_data()
        if key in data:
            del data[key]
            cls._write_data(data)
            return {"message": f"Deleted record for {key}"}
        else:
            return {"error": f"No record found for {key}"}

    @classmethod
    def get(cls, key=None):
        """Retrieve all data or a specific record by key."""
        data = cls._read_data()
        return data if key is None else data.get(key)

#     @classmethod
#     def save(cls, username, user_data):
#         if os.path.exists(cls.db_file):
#             with open(cls.db_file, 'r') as db:
#                 try:
#                     existing_data = json.load(db)
#                 except json.JSONDecodeError:
#                     existing_data = []
#         else:
#             existing_data = []
#
#         existing_data[username] = user_data
#
#         with open(cls.db_file, 'w') as db:
#             json.dump(existing_data, db, indent=4)
#
#     @classmethod
#     def delete(cls, username):
#         try:
#             if os.path.exists(cls.db_file):
#                 updated_data = {}
#                 with open(cls.db_file, "r", encoding="utf-8") as current_db:
#                     try:
#                         current_data = json.load(current_db)
#                         removed_items = 0
#                         for user, user_data in current_data.items():
#                             if user != username:
#                                 updated_data[user] = user_data
#                             else:
#                                 removed_items += 1
#                     except json.JSONDecodeError:
#                         updated_data = []
#             else:
#                 raise FileNotFoundError
#         except FileNotFoundError:
#             return FileNotFoundError
#         except Exception as e:
#             return e
#
#         with open(cls.db_file, 'w') as new_db:
#             json.dump(updated_data, new_db, indent=4)
#             return {"message": f"Deleted {removed_items} record(s)"}
#
#     @classmethod
#     def get(cls, username=None):
#         try:
#             if os.path.exists(cls.db_file):
#                 with open(cls.db_file, "r", encoding="utf-8") as db:
#                     try:
#                         users = json.load(db)
#                         if username is None:
#                             return users
#                         else:
#                             return users[username]
#                     except json.JSONDecodeError:
#                         return []
#                     except KeyError:
#                         return []
#             else:
#                 raise FileNotFoundError
#         except FileNotFoundError:
#             return FileNotFoundError
#         except Exception as e:
#             return e
#
#
# print(DbManager.delete("user1"))
