import DatabaseConnection
import sqlite3
import datetime

class DatabaseManager:
    def __init__(self):
        try:
            print("Initializing DatabaseConnection...")
            self.db_connection = DatabaseConnection.DatabaseConnection()
            print("DatabaseConnection initialized.")
        except Exception as e:
            print(f"Error during DatabaseConnection initialization: {e}")
            raise

    def create_tables(self):
        try:
            print("Dropping existing tables if they exist...")
            self.db_connection.execute_query("DROP TABLE IF EXISTS medical_records;")
            self.db_connection.execute_query("DROP TABLE IF EXISTS appointments;")
            self.db_connection.execute_query("DROP TABLE IF EXISTS doctors;")
            self.db_connection.execute_query("DROP TABLE IF EXISTS patients;")
            self.db_connection.execute_query("DROP TABLE IF EXISTS admins;")
            print("Tables dropped successfully.")

            print("Creating tables...")
            self.db_connection.execute_query('''
                CREATE TABLE doctors (
                    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL,
                    age INTEGER
                );''')
            self.db_connection.execute_query('''
                CREATE TABLE admins (
                    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                );''')
            self.db_connection.execute_query('''
                CREATE TABLE patients (
                    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL,
                    age INTEGER
                );''')
            self.db_connection.execute_query('''
                CREATE TABLE IF NOT EXISTS appointments (
                    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doctor_id INTEGER NOT NULL,
                    patient_id INTEGER NOT NULL,
                    appointment_time DATETIME NOT NULL,
                    details TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
                );''')
            self.db_connection.execute_query('''
                CREATE TABLE IF NOT EXISTS medical_records (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    doctor_id INTEGER NOT NULL,
                    record_date DATE NOT NULL,
                    record_details TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
                );''')
            print("Tables created successfully.")
        except Exception as e:
            print(f"Error during table creation: {e}")
            raise

    def insert_initial_data(self):
        try:
            print("Inserting initial data...")
            self.db_connection.execute_query(
                "INSERT INTO admins (email, password) VALUES (?, ?)",
                ('admin@example.com', 'adminpass')
            )
            print("Admin inserted.")

            doctors = [(f'doctor{i}@example.com', 'password', f'Doctor User {i}', 30 + i % 10) for i in range(1, 31)]
            patients = [(f'patient{i}@example.com', 'password', f'Patient User {i}', 20 + i % 10) for i in range(1, 31)]

            for doctor in doctors:
                self.db_connection.execute_query(
                    "INSERT INTO doctors (email, password, name, age) VALUES (?, ?, ?, ?)",
                    doctor
                )
            print("Doctors inserted.")

            for patient in patients:
                self.db_connection.execute_query(
                    "INSERT INTO patients (email, password, name, age) VALUES (?, ?, ?, ?)",
                    patient
                )
            print("Patients inserted.")

            current_time = datetime.datetime.now()
            appointments = []
            for i in range(30):
                for j in range(2):
                    appointments.append((i + 1, i + 1, current_time.strftime('%Y-%m-%d %H:%M:%S'), 'Routine Checkup'))
                    current_time += datetime.timedelta(days=1)

            for appointment in appointments:
                self.db_connection.execute_query(
                    "INSERT INTO appointments (doctor_id, patient_id, appointment_time, details) VALUES (?, ?, ?, ?)",
                    appointment
                )
            print("Appointments inserted.")

            # Insert initial medical records
            records = [(i + 1, (i % 30) + 1, (current_time - datetime.timedelta(days=i)).strftime('%Y-%m-%d'), f'Medical Record {i + 1}') for i in range(30)]

            for record in records:
                self.db_connection.execute_query(
                    "INSERT INTO medical_records (patient_id, doctor_id, record_date, record_details) VALUES (?, ?, ?, ?)",
                    record
                )
            print("Medical records inserted.")

        except Exception as e:
            print(f"Error during initial data insertion: {e}")
            raise