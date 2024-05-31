import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from dicom_viewer2 import DICOMApp
import sqlite3

class AdminWindow(tk.Toplevel):
    def __init__(self, master, db_connection):
        super().__init__(master)
        self.db_connection = db_connection
        self.title("Admin Dashboard")
        self.setup_ui()

    def setup_ui(self):
        print('Setting up UI...')
        header_label = tk.Label(self, text="Admin Dashboard", font=('Helvetica', 16))
        header_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))

        add_doctor_button = tk.Button(self, text="Add Doctor", command=lambda: self.add_user("doctors"))
        add_doctor_button.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        add_patient_button = tk.Button(self, text="Add Patient", command=lambda: self.add_user("patients"))
        add_patient_button.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

        remove_doctor_button = tk.Button(self, text="Remove Doctor", command=lambda: self.remove_user("doctors"))
        remove_doctor_button.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

        remove_patient_button = tk.Button(self, text="Remove Patient", command=lambda: self.remove_user("patients"))
        remove_patient_button.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

        self.grid_columnconfigure([0, 1, 2], weight=1)

    def add_user(self, table_name):
        add_window = tk.Toplevel(self)
        add_window.title(f"Add New {table_name[:-1].capitalize()}")

        tk.Label(add_window, text="Email:").grid(row=0, column=0, padx=10, pady=5)
        email_entry = tk.Entry(add_window)
        email_entry.grid(row=0, column=1)

        tk.Label(add_window, text="Password:").grid(row=1, column=0, padx=10, pady=5)
        password_entry = tk.Entry(add_window)
        password_entry.grid(row=1, column=1)

        tk.Label(add_window, text="Name:").grid(row=2, column=0, padx=10, pady=5)
        name_entry = tk.Entry(add_window)
        name_entry.grid(row=2, column=1)

        tk.Label(add_window, text="Age:").grid(row=3, column=0, padx=10, pady=5)
        age_entry = tk.Entry(add_window)
        age_entry.grid(row=3, column=1)

        submit_button = tk.Button(add_window, text="Submit", command=lambda: self.submit_new_user(email_entry.get(), password_entry.get(), name_entry.get(), age_entry.get(), table_name))
        submit_button.grid(row=4, column=1, pady=10)

    def submit_new_user(self, email, password, name, age, table_name):
        try:
            age = int(age)
            query = f"INSERT INTO {table_name} (email, password, name, age) VALUES (?, ?, ?, ?)"
            self.db_connection.execute_query(query, (email, password, name, age))
            messagebox.showinfo("Success", f"New {table_name[:-1]} added successfully!")
        except ValueError:
            messagebox.showerror("Error", "Age must be a valid number")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def remove_user(self, table_name):
        remove_window = tk.Toplevel(self)
        remove_window.title(f"Remove {table_name[:-1].capitalize()}")

        tk.Label(remove_window, text=f"Select {table_name[:-1].capitalize()} ID:").grid(row=0, column=0, padx=10, pady=10)
        id_entry = tk.Entry(remove_window)
        id_entry.grid(row=0, column=1, padx=10, pady=10)

        confirm_button = tk.Button(remove_window, text="Remove", command=lambda: self.confirm_deletion(id_entry.get(), table_name))
        confirm_button.grid(row=1, column=1, padx=10, pady=10)

    def confirm_deletion(self, id, table_name):
        try:
            id = int(id)
            query = f"DELETE FROM {table_name} WHERE {table_name[:-1]}_id = ?"
            self.db_connection.execute_query(query, (id,))
            messagebox.showinfo("Success", f"{table_name[:-1].capitalize()} removed successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer for ID")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def view_doctors(self):
        self.view_users("doctors")

    def view_patients(self):
        self.view_users("patients")

    def view_users(self, table_name):
        user_window = tk.Toplevel(self)
        user_window.title("View Users")

        tree = ttk.Treeview(user_window, columns=('PatientID', 'Email', 'Name', 'Age'), show='headings')
        tree.heading('Patient', text='PatientID')
        tree.heading('Email', text='Email')
        tree.heading('Name', text='Name')
        tree.heading('Age', text='Age')
        tree.pack(fill='both', expand=True)

        query = f"SELECT * FROM {table_name}"
        try:
            result = self.db_connection.execute_query(query)
            for row in result:
                tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

        scrollbar = ttk.Scrollbar(user_window, orient='vertical', command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

class DoctorWindow(tk.Toplevel):
    def __init__(self, master, db_connection, doctor_id):
        super().__init__(master)
        self.db_connection = db_connection
        self.doctor_id = doctor_id  # Now explicitly using doctor_id
        self.title("Doctor Dashboard")
        self.setup_ui()

    def setup_ui(self):
        header_label = tk.Label(self, text="Doctor Dashboard", font=('Helvetica', 16))
        header_label.grid(row=0, column=0, columnspan=3, pady=(10, 20))

        view_patients_button = tk.Button(self, text="View Patients", command=self.view_patients)
        view_patients_button.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        manage_appointments_button = tk.Button(self, text="Manage Appointments", command=self.manage_appointments)
        manage_appointments_button.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

        access_records_button = tk.Button(self, text="Access Medical Records", command=self.access_medical_records)
        access_records_button.grid(row=1, column=2, padx=10, pady=10, sticky='ew')

        dicom_button = tk.Button(self, text="View DICOM Images", command=self.launch_dicom_viewer)
        dicom_button.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

        update_info_button = tk.Button(self, text="Update Personal Info", command=self.update_info)
        update_info_button.grid(row=3, column=2, padx=10, pady=10, sticky='ew')

        self.grid_columnconfigure([0, 1, 2], weight=1)

    def update_info(self):
        user_details = self.db_connection.execute_query(
            "SELECT password, email, age FROM doctors WHERE doctor_id=?",
            (self.doctor_id,))
        current_details = user_details[0] if user_details else ("", "", "")

        update_window = tk.Toplevel(self)
        update_window.title("Update Personal Info")

        tk.Label(update_window, text="Password:").grid(row=0, column=0)
        password_entry = tk.Entry(update_window)
        password_entry.grid(row=0, column=1)
        password_entry.insert(0, current_details[0])

        tk.Label(update_window, text="Email:").grid(row=1, column=0)
        email_entry = tk.Entry(update_window)
        email_entry.grid(row=1, column=1)
        email_entry.insert(0, current_details[1])

        tk.Label(update_window, text="Age:").grid(row=2, column=0)
        age_entry = tk.Entry(update_window)
        age_entry.grid(row=2, column=1)
        age_entry.insert(0, current_details[2])

        def submit_updates():
            try:
                self.db_connection.execute_query(
                    "UPDATE doctors SET name=?, email=?, age=? WHERE doctor_id=?",
                    (name_entry.get(), email_entry.get(), age_entry.get(), self.doctor_id))
                messagebox.showinfo("Success", "Your information has been updated successfully!")
                update_window.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

        tk.Button(update_window, text="Submit", command=submit_updates).grid(row=3, column=1, pady=10)

    def view_patients(self):
        # Create a top-level window
        patient_window = tk.Toplevel(self)
        patient_window.title("View Patients")

        # Create a Treeview widget
        tree = ttk.Treeview(patient_window, columns=('PatientID', 'Name', 'Age', 'Last Appointment'), show='headings')
        tree.heading('PatientID', text='PatientID')
        tree.heading('Name', text='Name')
        tree.heading('Age', text='Age')
        tree.heading('Last Appointment', text='Last Appointment')
        tree.column('PatientID', width=50)
        tree.column('Name', width=150)
        tree.column('Age', width=50)
        tree.column('Last Appointment', width=100)
        tree.pack(fill='both', expand=True)

        # Query the database for patient data
        try:
            result = self.db_connection.execute_query(
                "SELECT patient_id, name, age, (SELECT MAX(appointment_time) FROM appointments WHERE patient_id = patients.patient_id) AS last_appointment FROM patients")
            for row in result:
                tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

        # Scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(patient_window, orient='vertical', command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def manage_appointments(self):
        self.appt_window = tk.Toplevel(self)
        self.appt_window.title("Manage Appointments")

        self.tree = ttk.Treeview(self.appt_window, columns=('AppointmentID', 'DoctorID', 'PatientID', 'Time', 'Details'), show='headings')
        self.tree.heading('AppointmentID', text='Appointment ID')
        self.tree.heading('DoctorID', text='Doctor ID')
        self.tree.heading('PatientID', text='Patient ID')
        self.tree.heading('Time', text='Appointment Time')
        self.tree.heading('Details', text='Details')
        self.tree.pack(fill='both', expand=True)

        # Fetch appointments from the database for the current doctor
        try:
            query = "SELECT appointment_id, doctor_id, patient_id, appointment_time, details FROM appointments WHERE doctor_id=?"
            result = self.db_connection.execute_query(query, (self.doctor_id,))
            for row in result:
                self.tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

        tk.Label(self.appt_window, text="Add New Appointment:").pack()

        tk.Label(self.appt_window, text="Patient ID:").pack()
        self.patient_id_entry = tk.Entry(self.appt_window)
        self.patient_id_entry.pack()
        self.patient_id_entry.insert(0, "Enter Patient ID")

        tk.Label(self.appt_window, text="Appointment Time (YYYY-MM-DD HH:MM):").pack()
        self.time_entry = tk.Entry(self.appt_window)
        self.time_entry.pack()
        self.time_entry.insert(0, "2024-01-01 12:00")

        tk.Label(self.appt_window, text="Details:").pack()
        self.details_entry = tk.Entry(self.appt_window)
        self.details_entry.pack()
        self.details_entry.insert(0, "Enter appointment details")

        tk.Button(self.appt_window, text="Add Appointment", command=self.add_appointment).pack()
        tk.Button(self.appt_window, text="Delete Appointment", command=self.delete_appointment).pack()

        scrollbar = ttk.Scrollbar(self.appt_window, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def add_appointment(self):
        patient_id = self.patient_id_entry.get()
        time = self.time_entry.get()
        details = self.details_entry.get()

        if patient_id == "Enter Patient ID" or time == "2024-01-01 12:00" or details == "Enter appointment details":
            messagebox.showerror("Input Error", "Please replace the placeholder text with actual appointment details.")
            return

        try:
            self.db_connection.execute_query(
                "INSERT INTO appointments (doctor_id, patient_id, appointment_time, details) VALUES (?, ?, ?, ?)",
                (self.doctor_id, patient_id, time, details))  # Use self.doctor_id here
            messagebox.showinfo("Success", "Appointment added successfully!")
            self.refresh_appointments()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def delete_appointment(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select an appointment to delete.")
            return

        appointment_id = self.tree.item(selected_item[0], 'values')[0]
        try:
            self.db_connection.execute_query(
                "DELETE FROM appointments WHERE appointment_id=?", (appointment_id,))
            messagebox.showinfo("Success", "Appointment deleted successfully!")
            self.refresh_appointments()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def refresh_appointments(self):
        self.tree.delete(*self.tree.get_children())
        query = "SELECT appointment_id, doctor_id, patient_id, appointment_time, details FROM appointments WHERE doctor_id=?"
        result = self.db_connection.execute_query(query, (self.doctor_id,))
        for row in result:
            self.tree.insert('', 'end', values=row)

    def access_medical_records(self):
        records_window = tk.Toplevel(self)
        records_window.title("Medical Records")

        tree = ttk.Treeview(records_window, columns=('RecordID', 'PatientID', 'Date', 'Details'), show='headings')
        tree.heading('RecordID', text='Record ID')
        tree.heading('PatientID', text='Patient ID')
        tree.heading('Date', text='Date of Record')
        tree.heading('Details', text='Details')
        tree.pack(fill='both', expand=True)

        # Fetch medical records from the database for the current doctor
        try:
            query = "SELECT record_id, patient_id, record_date, record_details FROM medical_records WHERE doctor_id=?"
            result = self.db_connection.execute_query(query, (self.doctor_id,))
            for row in result:
                tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

        scrollbar = ttk.Scrollbar(records_window, orient='vertical', command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def launch_dicom_viewer(self):
        self.dicom_viewer = tk.Toplevel(self)
        DICOMApp(self.dicom_viewer)


class PatientWindow(tk.Toplevel):
    def __init__(self, master, db_connection, patient_id):
        super().__init__(master)  # Initialize the superclass
        self.db_connection = db_connection
        self.patient_id = patient_id  # Use patient_id
        self.title("Patient Dashboard")
        self.setup_ui()

    def setup_ui(self):
        header_label = tk.Label(self, text="Patient Dashboard", font=('Helvetica', 16))
        header_label.grid(row=0, column=0, columnspan=3, pady=(10, 20))

        view_appointments_button = tk.Button(self, text="View Appointments", command=self.view_appointments)
        view_appointments_button.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        view_history_button = tk.Button(self, text="View Medical History", command=self.view_medical_history)
        view_history_button.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

        update_info_button = tk.Button(self, text="Update Personal Info", command=self.update_info)
        update_info_button.grid(row=1, column=2, padx=10, pady=10, sticky='ew')

        self.grid_columnconfigure([0, 1, 2], weight=1)

    def view_appointments(self):
        appointment_window = tk.Toplevel(self)
        appointment_window.title("View Appointments")
        appointment_window.grid_rowconfigure(0, weight=1)
        appointment_window.grid_columnconfigure(0, weight=1)

        frame = tk.Frame(appointment_window)
        frame.grid(sticky='nsew')

        tree = ttk.Treeview(frame, columns=('AppointmentID', 'PatientID', 'Time', 'Details'), show='headings')
        tree.heading('AppointmentID', text='Appointment ID')
        tree.heading('PatientID', text='Patient ID')
        tree.heading('Time', text='Appointment Time')
        tree.heading('Details', text='Details')
        tree.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        try:
            result = self.db_connection.execute_query(
                "SELECT appointment_id, patient_id, appointment_time, details FROM appointments WHERE patient_id=?",
                (self.patient_id,))
            for row in result:
                tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def view_medical_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("Medical History")

        tree = ttk.Treeview(history_window, columns=('RecordID', 'DoctorID', 'Date', 'Details'), show='headings')
        tree.heading('RecordID', text='Record ID')
        tree.heading('DoctorID', text='Doctor ID')
        tree.heading('Date', text='Date of Record')
        tree.heading('Details', text='Details')
        tree.pack(fill='both', expand=True)

        try:
            result = self.db_connection.execute_query(
                "SELECT record_id, doctor_id, record_date, record_details FROM medical_records WHERE patient_id=?",
                (self.patient_id,))
            for row in result:
                tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

        scrollbar = ttk.Scrollbar(history_window, orient='vertical', command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def update_info(self):
        user_details = self.db_connection.execute_query(
            "SELECT password, email, age FROM patients WHERE patient_id=?",
            (self.patient_id,))
        current_details = user_details[0] if user_details else ("", "", "")

        update_window = tk.Toplevel(self)
        update_window.title("Update Personal Info")

        tk.Label(update_window, text="Password:").grid(row=0, column=0)
        password_entry = tk.Entry(update_window)
        password_entry.grid(row=0, column=1)
        password_entry.insert(0, current_details[0])

        tk.Label(update_window, text="Email:").grid(row=1, column=0)
        email_entry = tk.Entry(update_window)
        email_entry.grid(row=1, column=1)
        email_entry.insert(0, current_details[1])

        tk.Label(update_window, text="Age:").grid(row=2, column=0)
        age_entry = tk.Entry(update_window)
        age_entry.grid(row=2, column=1)
        age_entry.insert(0, current_details[2])

        def submit_updates():
            try:
                self.db_connection.execute_query(
                    "UPDATE patients SET password=?, email=?, age=? WHERE patient_id=?",
                    (password_entry.get(), email_entry.get(), age_entry.get(), self.patient_id))
                messagebox.showinfo("Success", "Your information has been updated successfully!")
                update_window.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

        tk.Button(update_window, text="Submit", command=submit_updates).grid(row=3, column=1, pady=10)
