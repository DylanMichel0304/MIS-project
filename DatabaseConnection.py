import sqlite3
import logging
from tkinter import messagebox


class DatabaseConnection:
    def __init__(self, db_file='HospitalDB2.db'):
        self.db_file = db_file

    def connect(self):
        try:
            print(f"Connecting to database: {self.db_file}")
            conn = sqlite3.connect(self.db_file)
            print("Connected to database successfully.")
            return conn
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            messagebox.showerror("Database Error", f"Unable to connect to database: {e}")
            return None


    def create_table(self):
        create_table_sql = '''
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            );
        '''
        conn = None
        cursor = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
        except mysql.connector.Error as e:
            logging.error(f"Error creating tables: {e}")
            if conn:
                conn.rollback()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def insert_person(self, name, age):
        insert_sql = "INSERT INTO people (name, age) VALUES (?, ?)"
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(insert_sql, (name, age))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error inserting person: {e}")

    def search_by_name(self, name):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM people WHERE name LIKE ?", ('%' + name + '%',))
                return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error searching by name: {e}")

    def update_person(self, id, name, age):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE people SET name = ?, age = ? WHERE id = ?", (name, age, id))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error updating person: {e}")

    def delete_person(self, id):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM people WHERE id = ?", (id,))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error deleting person: {e}")

    def show_all_people(self):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM people")
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
        except sqlite3.Error as e:
            logging.error(f"Error showing all people: {e}")
    
    def add_person(self):
        name = input("Enter the person's name: ")
        while True:
            try:
                age = int(input("Enter the person's age: "))
                break
            except ValueError:
                print("Please enter a valid integer for the age.")
        
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO people (name, age) VALUES (?, ?)", (name, age))
            conn.commit()
            print(f"{name} has been added to the database.")
            cur.close()
        
    def reinitialize_database(self):
        try:
            self.drop_tables()
            self.create_table()
        except sqlite3.Error as e:
            logging.error(f"Error reinitializing the database: {e}")

    def drop_tables(self):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS people")
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error dropping tables: {e}")
            
    def execute_query(self, query, params=None):
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                conn.commit()
                return cur.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Failed to execute query {query}: {e}")
            messagebox.showerror("Database Error", "Failed to execute operation")
            return None

    def close(self):
        """Close the database connection."""
        if self.conn:
            try:
                self.conn.close()
                print("The database is closed")
            except sqlite3.Error as e:
                logging.error(f"Error closing the database: {e}")
                
    