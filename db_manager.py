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
        return data if key is None else {key: data.get(key)}
