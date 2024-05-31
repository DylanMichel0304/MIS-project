import tkinter as tk
from tkinter import messagebox
import userWindows as fenetre
import sqlite3
import LoginPortal



class InitialWindow:
    def __init__(self, master, db_connection):
        self.master = master
        self.db_connection = db_connection
        self.master.title("Welcome")
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.master, text="Welcome", font=('Helvetica', 16)).grid(row=0, column=0, columnspan=2, pady=20)

        tk.Button(self.master, text="Create Account", command=self.open_create_account).grid(row=1, column=0, padx=20,
                                                                                             pady=10)
        tk.Button(self.master, text="Login", command=self.open_login).grid(row=1, column=1, padx=20, pady=10)

    def open_create_account(self):
        print("Create Account button clicked")  # Debug statement
        self.master.withdraw()
        create_account_window = tk.Toplevel(self.master)
        CreateAccount(create_account_window, self.db_connection)

    def open_login(self):
        print("Login button clicked")  # Debug statement
        self.master.withdraw()
        login_window = tk.Toplevel(self.master)
        LoginPortal(login_window, self.db_connection)


class CreateAccount:
    def __init__(self, master, db_connection):
        self.master = master
        self.db_connection = db_connection
        self.master.title("Create Account")
        self.setup_ui()

    def setup_ui(self):
        print("Setting up Create Account UI")  # Debug statement
        tk.Label(self.master, text="Create Account", font=('Helvetica', 16)).grid(row=0, column=0, columnspan=2,
                                                                                  pady=20)

        tk.Label(self.master, text="Email:").grid(row=1, column=0, padx=10, pady=5)
        self.email_entry = tk.Entry(self.master)
        self.email_entry.grid(row=1, column=1)

        tk.Label(self.master, text="Password:").grid(row=2, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.grid(row=2, column=1)

        tk.Label(self.master, text="Name:").grid(row=3, column=0, padx=10, pady=5)
        self.name_entry = tk.Entry(self.master)
        self.name_entry.grid(row=3, column=1)

        tk.Label(self.master, text="Age:").grid(row=4, column=0, padx=10, pady=5)
        self.age_entry = tk.Entry(self.master)
        self.age_entry.grid(row=4, column=1)

        tk.Label(self.master, text="Role:").grid(row=5, column=0, padx=10, pady=5)
        self.role_var = tk.StringVar(value="doctor")
        tk.Radiobutton(self.master, text="Doctor", variable=self.role_var, value="doctor").grid(row=5, column=1,
                                                                                                sticky='w')
        tk.Radiobutton(self.master, text="Patient", variable=self.role_var, value="patient").grid(row=5, column=1,
                                                                                                  sticky='e')

        tk.Button(self.master, text="Submit", command=self.submit_account).grid(row=6, column=0, columnspan=2, pady=10)

    def submit_account(self):
        print("Submitting account")  # Debug statement
        email = self.email_entry.get()
        password = self.password_entry.get()
        name = self.name_entry.get()
        age = self.age_entry.get()
        role = self.role_var.get()

        if not email or not password or not name or not age:
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            age = int(age)
            table_name = role + 's'
            query = f"INSERT INTO {table_name} (email, password, name, age) VALUES (?, ?, ?, ?)"
            self.db_connection.execute_query(query, (email, password, name, age))
            messagebox.showinfo("Success", f"New {role} account created successfully!")
            self.master.destroy()  # Close the create account window
            self.master.master.deiconify()  # Show the initial window again
        except ValueError:
            messagebox.showerror("Error", "Age must be a valid number")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))


class LoginPortal:
    def __init__(self, master, db_connection):
        self.master = master
        self.db_connection = db_connection
        self.master.title("Login Portal")
        self.setup_ui()

    def setup_ui(self):
        print("Setting up Login UI")  # Debug statement
        # Create labels for email and password
        tk.Label(self.master, text="Email:").grid(row=0, column=0)
        tk.Label(self.master, text="Password:").grid(row=1, column=0)

        # Create entry fields for user input
        self.entry_email = tk.Entry(self.master)
        self.entry_password = tk.Entry(self.master, show="*")  # Hide password input
        self.entry_email.grid(row=0, column=1)
        self.entry_password.grid(row=1, column=1)

        # Create a login button that triggers the handle_login method
        tk.Button(self.master, text="Login", command=self.handle_login).grid(row=2, column=1, pady=10)

    def handle_login(self):
        print("Handling login")  # Debug statement
        entered_email = self.entry_email.get()
        entered_password = self.entry_password.get()
        user_type, user_id = self.authenticate_user(entered_email, entered_password)

        if user_type and user_id:
            messagebox.showinfo("Login Successful", "You have successfully logged in")
            self.master.withdraw()  # Hide the login window instead of destroying it
            if user_type == 'admin':
                new_window = fenetre.AdminWindow(self.master, self.db_connection)
            elif user_type == 'doctor':
                new_window = fenetre.DoctorWindow(self.master, self.db_connection, user_id)
            elif user_type == 'patient':
                new_window = fenetre.PatientWindow(self.master, self.db_connection, user_id)

            # Set up an event to destroy the login window when the new window is closed
            new_window.protocol("WM_DELETE_WINDOW", self.on_new_window_close)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials or email format")

    def on_new_window_close(self):
        self.master.destroy()  # Destroy the hidden login window

    def authenticate_user(self, email, password):
        admin_query = "SELECT admin_id FROM admins WHERE email=? AND password=?"
        doctor_query = "SELECT doctor_id FROM doctors WHERE email=? AND password=?"
        patient_query = "SELECT patient_id FROM patients WHERE email=? AND password=?"

        try:
            admin_result = self.db_connection.execute_query(admin_query, (email, password))
            if admin_result:
                return 'admin', admin_result[0][0]

            doctor_result = self.db_connection.execute_query(doctor_query, (email, password))
            if doctor_result:
                return 'doctor', doctor_result[0][0]

            patient_result = self.db_connection.execute_query(patient_query, (email, password))
            if patient_result:
                return 'patient', patient_result[0][0]

            return None, None
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None, None