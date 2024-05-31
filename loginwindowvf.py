import tkinter as tk
from tkinter import messagebox
import sys
import DatabaseConnection
import LoginPortal
from LoginPortal import InitialWindow
from DBmanager import DatabaseManager

class MainApplication:
    def __init__(self, root):
        try:
            print("Initializing database manager...")
            db_manager = DatabaseManager()  # Create an instance of DatabaseManager
            print("Creating tables...")
            db_manager.create_tables()  # Call the method on the instance
            print("Inserting initial data...")
            db_manager.insert_initial_data()  # Call the method on the instance

            print("Connecting to the database...")
            self.db_connection = DatabaseConnection.DatabaseConnection()
        except Exception as e:
            messagebox.showerror("Startup Error", str(e))
            sys.exit(1)

        self.root = root
        print("Setting up initial window...")
        self.initial_window = LoginPortal.InitialWindow(self.root, self.db_connection)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    app.run()
