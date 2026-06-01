import tkinter as tk
from tkinter import messagebox, ttk
import csv
from datetime import datetime
import os

from sklearn.linear_model import LogisticRegression
import numpy as np

FILE_NAME = "patients.csv"

# --------------------------
# Ensure CSV has correct format
# --------------------------
def ensure_csv_format():
    correct_header = ["ID", "Name", "Age", "Phone", "AppointmentDate", "DaysToAppointment", "Risk"]

    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(correct_header)
        return

    # Check if existing file has correct header
    with open(FILE_NAME, "r", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            header = []

    # If header is wrong (old format or empty), backup and recreate
    if header != correct_header:
        backup_name = f"patients_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        os.rename(FILE_NAME, backup_name)
        with open(FILE_NAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(correct_header)
        messagebox.showinfo("CSV Updated", f"Old data backed up to: {backup_name}\nNew format created.")

ensure_csv_format()

# --------------------------
# Fake training data
# --------------------------
X_train = np.array([
    [20, 2], [35, 10], [50, 1], [60, 15],
    [25, 3], [45, 7], [70, 20], [30, 5],
])
y_train = np.array([1, 0, 1, 0, 1, 0, 0, 1])

model = LogisticRegression()
model.fit(X_train, y_train)


# --------------------------
# Helper: Get next ID
# --------------------------
def get_next_id():
    with open(FILE_NAME, "r", newline="") as f:
        reader = list(csv.reader(f))
        if len(reader) <= 1:
            return 1
        # Find last non-empty row with a valid ID
        for row in reversed(reader[1:]):
            if row and row[0].strip().isdigit():
                return int(row[0]) + 1
        return 1


# --------------------------
# AI Risk function
# --------------------------
def predict_risk(age, days_to_appointment):
    return model.predict([[age, days_to_appointment]])[0]


# --------------------------
# Read all patients
# --------------------------
def read_all_patients():
    patients = []
    with open(FILE_NAME, "r", newline="") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if row and len(row) >= 7:
                patients.append(row)
    return patients


# --------------------------
# Save patient
# --------------------------
def save_patient():
    name = entry_name.get().strip()
    age = entry_age.get().strip()
    phone = entry_phone.get().strip()
    appointment = entry_date.get().strip()

    if not name or not age or not appointment:
        messagebox.showerror("Error", "Name, Age, and Appointment Date are required")
        return

    try:
        age = int(age)
        appointment_date = datetime.strptime(appointment, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Invalid age or date format (YYYY-MM-DD)")
        return

    today = datetime.today()
    days_to_appointment = (appointment_date - today).days
    risk = predict_risk(age, days_to_appointment)
    patient_id = get_next_id()

    with open(FILE_NAME, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([patient_id, name, age, phone, appointment, days_to_appointment, risk])

    if risk == 1:
        msg = "⚠ High risk patient: send reminder SMS or call."
    else:
        msg = "✓ Low risk patient: normal follow-up."

    messagebox.showinfo("Saved", f"Patient ID: {patient_id}\n{name}\n{msg}")

    entry_name.delete(0, tk.END)
    entry_age.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_date.delete(0, tk.END)


# --------------------------
# View Patients Window
# --------------------------
def open_view_patients():
    view_window = tk.Toplevel(root)
    view_window.title("Patient Records")
    view_window.geometry("950x450")

    # Search bar
    search_frame = tk.Frame(view_window)
    search_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(search_frame, text="Search by Name:").pack(side="left")
    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side="left", padx=5)

    def refresh_table(filter_text=""):
        # Clear existing
        for item in tree.get_children():
            tree.delete(item)

        patients = read_all_patients()
        count = 0
        for row in patients:
            if filter_text and filter_text.lower() not in row[1].lower():
                continue
            risk_text = "High ⚠" if row[6] == "1" else "Low ✓"
            display_row = row[:6] + [risk_text]
            tree.insert("", "end", values=display_row)
            count += 1

        status_label.config(text=f"Total Patients: {count}")

    def do_search():
        refresh_table(search_entry.get().strip())

    tk.Button(search_frame, text="Search", command=do_search).pack(side="left", padx=5)
    tk.Button(search_frame, text="Show All", command=lambda: [search_entry.delete(0, tk.END), refresh_table()]).pack(side="left", padx=5)

    # Treeview (table)
    columns = ("ID", "Name", "Age", "Phone", "Appointment", "Days Left", "Risk")
    tree = ttk.Treeview(view_window, columns=columns, show="headings")

    col_widths = {"ID": 50, "Name": 150, "Age": 50, "Phone": 120, "Appointment": 120, "Days Left": 80, "Risk": 80}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=col_widths.get(col, 100), anchor="center")

    scrollbar_y = ttk.Scrollbar(view_window, orient="vertical", command=tree.yview)
    scrollbar_x = ttk.Scrollbar(view_window, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x.pack(side="bottom", fill="x")
    tree.pack(fill="both", expand=True, padx=10)

    status_label = tk.Label(view_window, text="Total Patients: 0", anchor="w")
    status_label.pack(fill="x", padx=10, pady=5)

    refresh_table()


# --------------------------
# Edit Patient Window
# --------------------------
def open_edit_patient():
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Patient")
    edit_window.geometry("450x400")

    tk.Label(edit_window, text="Search by Patient ID or Name:", font=("Arial", 10, "bold")).pack(pady=5)

    search_frame = tk.Frame(edit_window)
    search_frame.pack(pady=5)

    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side="left", padx=5)

    edit_fields = {}
    current_id = tk.StringVar()

    def load_patient():
        query = search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter an ID or Name")
            return

        patients = read_all_patients()
        found = None

        for row in patients:
            if row[0] == query or row[1].lower() == query.lower():
                found = row
                break
            # Also allow partial name match
            if query.lower() in row[1].lower():
                found = row
                break

        if not found:
            messagebox.showwarning("Not Found", f"No patient found matching: {query}")
            return

        current_id.set(found[0])

        edit_fields["name"].delete(0, tk.END)
        edit_fields["name"].insert(0, found[1])

        edit_fields["age"].delete(0, tk.END)
        edit_fields["age"].insert(0, found[2])

        edit_fields["phone"].delete(0, tk.END)
        edit_fields["phone"].insert(0, found[3])

        edit_fields["date"].delete(0, tk.END)
        edit_fields["date"].insert(0, found[4])

        id_label.config(text=f"Editing Patient ID: {found[0]}")
        messagebox.showinfo("Loaded", f"Loaded: {found[1]} (ID: {found[0]})")

    def save_edits():
        pid = current_id.get()
        if not pid:
            messagebox.showerror("Error", "Please load a patient first")
            return

        name = edit_fields["name"].get().strip()
        age = edit_fields["age"].get().strip()
        phone = edit_fields["phone"].get().strip()
        appointment = edit_fields["date"].get().strip()

        if not all([name, age, appointment]):
            messagebox.showerror("Error", "Name, Age, and Appointment Date are required")
            return

        try:
            age = int(age)
            appointment_date = datetime.strptime(appointment, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid age or date format (YYYY-MM-DD)")
            return

        today = datetime.today()
        days_to_appointment = (appointment_date - today).days
        risk = predict_risk(age, days_to_appointment)

        rows = read_all_patients()

        with open(FILE_NAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Age", "Phone", "AppointmentDate", "DaysToAppointment", "Risk"])
            for row in rows:
                if row[0] == pid:
                    writer.writerow([pid, name, age, phone, appointment, days_to_appointment, risk])
                else:
                    writer.writerow(row)

        messagebox.showinfo("Success", f"Patient ID {pid} updated successfully!")
        edit_window.destroy()

    tk.Button(search_frame, text="Load Patient", command=load_patient, bg="#2196F3", fg="white").pack(side="left")

    id_label = tk.Label(edit_window, text="Editing Patient ID: --", font=("Arial", 10, "bold"), fg="blue")
    id_label.pack(pady=5)

    # Edit form
    form_frame = tk.Frame(edit_window)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Name:", width=20, anchor="e").grid(row=0, column=0, pady=5)
    edit_fields["name"] = tk.Entry(form_frame, width=30)
    edit_fields["name"].grid(row=0, column=1, pady=5)

    tk.Label(form_frame, text="Age:", width=20, anchor="e").grid(row=1, column=0, pady=5)
    edit_fields["age"] = tk.Entry(form_frame, width=30)
    edit_fields["age"].grid(row=1, column=1, pady=5)

    tk.Label(form_frame, text="Phone:", width=20, anchor="e").grid(row=2, column=0, pady=5)
    edit_fields["phone"] = tk.Entry(form_frame, width=30)
    edit_fields["phone"].grid(row=2, column=1, pady=5)

    tk.Label(form_frame, text="Appointment (YYYY-MM-DD):", width=20, anchor="e").grid(row=3, column=0, pady=5)
    edit_fields["date"] = tk.Entry(form_frame, width=30)
    edit_fields["date"].grid(row=3, column=1, pady=5)

    tk.Button(edit_window, text="💾 Save Changes", command=save_edits, bg="#4CAF50", fg="white", width=20, height=2).pack(pady=15)


# --------------------------
# Main GUI
# --------------------------
root = tk.Tk()
root.title("AI HIV Patient Tracker")
root.geometry("400x300")

# Title
tk.Label(root, text="AI HIV Patient Tracker", font=("Arial", 14, "bold")).pack(pady=10)

# --- Add Patient Form ---
form_frame = tk.Frame(root)
form_frame.pack(pady=5)

tk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
entry_name = tk.Entry(form_frame, width=30)
entry_name.grid(row=0, column=1, pady=3)

tk.Label(form_frame, text="Age:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
entry_age = tk.Entry(form_frame, width=30)
entry_age.grid(row=1, column=1, pady=3)

tk.Label(form_frame, text="Phone:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
entry_phone = tk.Entry(form_frame, width=30)
entry_phone.grid(row=2, column=1, pady=3)

tk.Label(form_frame, text="Appointment (YYYY-MM-DD):").grid(row=3, column=0, sticky="e", padx=5, pady=3)
entry_date = tk.Entry(form_frame, width=30)
entry_date.grid(row=3, column=1, pady=3)

tk.Button(root, text=" Save Patient", command=save_patient, bg="#2196F3", fg="white", width=20).pack(pady=10)

# --- Action Buttons ---
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="View Patients", command=open_view_patients, width=18).pack(side="left", padx=5)
tk.Button(btn_frame, text="Edit Patient", command=open_edit_patient, width=18).pack(side="left", padx=5)

root.mainloop()
