import json
import os


class DbManager:

    @classmethod
    def add(cls, db_name, data):
        if os.path.exists(db_name):
            with open(db_name, 'r') as db:
                try:
                    existing_data = json.load(db)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        existing_data.append(data)

        with open(db_name, 'w') as db:
            json.dump(existing_data, db, indent=4)


    @classmethod
    def update(cls, db_name, user_name, key, new_key_val):
        try:
            if os.path.exists(db_name):
                with open(db_name, "r", encoding="utf-8") as old_db_file:
                    try:
                        existing_data = json.load(old_db_file)
                        updated_recs = 0
                        for record in existing_data:
                            if record["username"] == user_name:
                                record[key] = new_key_val
                                updated_recs +=1
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

        with open(db_name, 'w') as new_db_file:
            json.dump(existing_data, new_db_file, indent=4)
            return {"message": f"updated {updated_recs} record(s)"}


    @classmethod
    def remove(cls, db_name, user_name):
        try:
            if os.path.exists(db_name):
                updated_data = []
                with open(db_name, "r", encoding="utf-8") as old_db_file:
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

        with open(db_name, 'w') as new_db_file:
            json.dump(updated_data, new_db_file, indent=4)
            return {"message": f"updated {removed_recs} record(s)"}

    @classmethod
    def fetch(cls, db_name, user_name):
        try:
            if os.path.exists(db_name):
                with open(db_name, "r", encoding="utf-8") as old_db_file:
                    try:
                        existing_data = json.load(old_db_file)
                        return [record for record in existing_data if record["username"] == user_name]
                    except json.JSONDecodeError:
                        return []
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            return {"message": "database not found"}
        except Exception as e:
            return {"message": e}




