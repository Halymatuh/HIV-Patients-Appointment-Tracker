import tkinter as tk
from tkinter import messagebox
import csv
from datetime import datetime

# File to store records
FILE_NAME = "patients.csv"

# Create file if it doesn't exist
try:
    with open(FILE_NAME, "x", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Age", "Clinic ID", "Appointment Date"])
except FileExistsError:
    pass


def save_patient():
    name = entry_name.get()
    age = entry_age.get()
    clinic_id = entry_id.get()
    appointment = entry_date.get()

    if not name or not age or not clinic_id or not appointment:
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        datetime.strptime(appointment, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Use date format YYYY-MM-DD")
        return

    with open(FILE_NAME, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, age, clinic_id, appointment])

    messagebox.showinfo("Success", "Patient record saved")

    entry_name.delete(0, tk.END)
    entry_age.delete(0, tk.END)
    entry_id.delete(0, tk.END)
    entry_date.delete(0, tk.END)


# GUI setup
root = tk.Tk()
root.title("HIV Patient Tracker")

tk.Label(root, text="Name").grid(row=0, column=0)
tk.Label(root, text="Age").grid(row=1, column=0)
tk.Label(root, text="Clinic ID").grid(row=2, column=0)
tk.Label(root, text="Appointment (YYYY-MM-DD)").grid(row=3, column=0)

entry_name = tk.Entry(root)
entry_age = tk.Entry(root)
entry_id = tk.Entry(root)
entry_date = tk.Entry(root)

entry_name.grid(row=0, column=1)
entry_age.grid(row=1, column=1)
entry_id.grid(row=2, column=1)
entry_date.grid(row=3, column=1)

tk.Button(root, text="Save Patient", command=save_patient).grid(row=4, column=1)

root.mainloop()
