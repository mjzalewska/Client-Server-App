import json
import os


class DbManager:
    db_file = "users.json"

    @classmethod
    def add(cls, data):
        if os.path.exists(cls.db_file):
            with open(cls.db_file, 'r') as db:
                try:
                    existing_data = json.load(db)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        existing_data.append(data)

        with open(cls.db_file, 'w') as db:
            json.dump(existing_data, db, indent=4)

    @classmethod
    def update(cls, user_name, key, new_key_val):
        try:
            if os.path.exists(cls.db_file):
                with open(cls.db_file, "r", encoding="utf-8") as old_db_file:
                    try:
                        existing_data = json.load(old_db_file)
                        updated_recs = 0
                        for record in existing_data:
                            if record["username"] == user_name:
                                record[key] = new_key_val
                                updated_recs += 1
                            else:
                                pass
                    except json.JSONDecodeError:
                        existing_data = []
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            return {"message": "database not found"}
        except Exception as e:
            return {"message": e}

        with open(cls.db_file, 'w') as new_db_file:
            json.dump(existing_data, new_db_file, indent=4)
            return {"message": f"updated {updated_recs} record(s)"}

    @classmethod
    def remove(cls, user_name):
        try:
            if os.path.exists(cls.db_file):
                updated_data = []
                with open(cls.db_file, "r", encoding="utf-8") as old_db_file:
                    try:
                        existing_data = json.load(old_db_file)
                        removed_recs = 0
                        for record in existing_data:
                            if record["username"] != user_name:
                                updated_data.append(record)
                            else:
                                removed_recs += 1
                    except json.JSONDecodeError:
                        updated_data = []
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            return {"message": "database not found"}
        except Exception as e:
            return {"message": e}

        with open(cls.db_file, 'w') as new_db_file:
            json.dump(updated_data, new_db_file, indent=4)
            return {"message": f"updated {removed_recs} record(s)"}

    @classmethod
    def fetch(cls, username=None):
        try:
            if os.path.exists(cls.db_file):
                with open(cls.db_file, "r", encoding="utf-8") as old_db_file:
                    try:
                        existing_data = json.load(old_db_file)
                        if username is None:
                            return [record for record in existing_data]
                        return [record for record in existing_data if record.get("username") == username]
                    except json.JSONDecodeError:
                        return []
                    except KeyError:
                        return []
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            return [{"message": "database not found"}]
        except Exception as e:
            return [{"message": e}]
