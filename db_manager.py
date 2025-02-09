import json
import logging

class DbManager:
    def __init__(self, db_table):
        self.db = db_table

    def _read_data(self):
        """
        Helper method to read data from the database.

        Returns:
            dict: Database contents or empty dict if file doesn't exist

        Raises:
            PermissionError: If file exists but can't be accessed
            ValueError: If database file is corrupted
        """
        try:
            with open(self.db, "r", encoding="utf-8") as db:
                return json.load(db)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"Corrupted database file: {e}")
            raise ValueError(f"Database file is corrupted: {e}") from e
        except PermissionError as e:
            logging.error(f"Permission denied accessing database: {e}")
            raise
        except OSError as e:
            logging.error(f"OS error accessing database: {e}")
            raise

    def _write_data(self, data):
        """
        Helper method to write data to the database.

        Args:
            data (dict): Data to write to database

        Raises:
            PermissionError: If file can't be written to
            TypeError: If data is not JSON serializable
            OSError: If file system error occurs
        """
        try:
            with open(self.db, "w", encoding="utf-8") as db:
                json.dump(data, db, indent=4)
        except TypeError as e:
            logging.error(f"Invalid data format for JSON serialization: {e}")
            raise TypeError(f"Data is not JSON serializable: {e}") from e
        except PermissionError as e:
            logging.error(f"Permission denied writing to database: {e}")
            raise
        except OSError as e:
            logging.error(f"OS error writing to database: {e}")

    def save(self, key, value):
        """
        Save or update a record in the database.

        Args:
            key (str): Record key (username)
            value (dict): User data to save

        Raises:
            ValueError: If key or value is invalid
            TypeError: If value is not JSON serializable
        """
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Invalid key: must be a non-empty string")
        if not isinstance(value, dict):
            raise ValueError("Invalid value: must be a dictionary")
        try:
            data = self._read_data()
            data[key] = value
            self._write_data(data)
        except (ValueError, TypeError, OSError) as e:
            logging.error(f"Failed to save data for key {key}: {e}")
            raise

    def delete(self, key):
        """
        Delete a record from the database.

        Args:
            key (str): Key to delete

        Returns:
            dict: Status message

        Raises:
            KeyError: If key doesn't exist
            OSError: If file system error occurs
        """
        try:
            data = self._read_data()
            if key not in data:
                raise KeyError(f"No record found for {key}")
            del data[key]
            self._write_data(data)
        except KeyError as e:
            logging.error(f"Delete failed - key not found: {e}")
            raise
        except OSError as e:
            logging.error(f"Failed to delete record: {e}")
            raise

    def get(self, key=None):
        """
        Retrieve all data or a specific record by key.

        Args:
            key (str, optional): Specific key to retrieve

        Returns:
            dict: Requested data

        Raises:
            ValueError: If key is invalid
            KeyError: If the key doesn't exist
        """
        try:
            data = self._read_data()
            if key is None:
                return data
            if not isinstance(key, str):
                raise ValueError("Key must be a string")
            if key not in data:
                return {}
            return {key: data.get(key)}
        except ValueError as e:
            logging.error(f"Invalid key type: {e}")
            raise
        except OSError as e:
            logging.error(f"Failed to retrieve data: {e}")
            raise
