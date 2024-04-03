import csv
import tkinter as tk
from datetime import datetime
from google.oauth2 import service_account
import gspread

class SignOutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Sign-Out")
        self.root.configure(bg="#FFA500")  # Use orange color as the main theme, reminiscent of a tiger

        self.class_rosters = {
            "Period 1": ["Student 1", "Student 2", "Student 3", "Student 4"],
            "Period 2 ": ["Student 5", "Student 6", "Student 7", "Student 8"],
            # Add more classes and students as needed
        }

        self.selected_class = tk.StringVar()
        self.selected_class.set("Class 1")  # Default class selection

        self.class_selector_label = tk.Label(self.root, text="Select Class:", bg="#FFA500", font=("Comic Sans MS", 12))
        self.class_selector_label.pack()

        self.class_selector = tk.OptionMenu(self.root, self.selected_class, *self.class_rosters.keys())
        self.class_selector.config(bg="#d3d3d3", width=20, font=("Comic Sans MS", 12))
        self.class_selector.pack(pady=5)

        self.student_var = tk.StringVar(self.root)

        self.sign_out_frame = tk.Frame(self.root, bg="#FFA500")
        self.sign_out_frame.pack()

        self.student_dropdown_label = tk.Label(self.sign_out_frame, text="Select Student:", bg="#FFA500", font=("Comic Sans MS", 12))
        self.student_dropdown_label.pack()

        self.student_dropdown = tk.OptionMenu(self.sign_out_frame, self.student_var, *self.class_rosters[self.selected_class.get()])
        self.student_dropdown.config(bg="#d3d3d3", width=20, font=("Comic Sans MS", 12))
        self.student_dropdown.pack(pady=5)

        self.sign_out_button = tk.Button(self.sign_out_frame, text="I'm in the restroom", command=self.sign_out, bg="#4caf50", fg="white", font=("Comic Sans MS", 12))
        self.sign_out_button.pack(pady=5)

        self.display_frame = tk.Frame(self.root, bg="#FFA500")
        self.display_frame.pack()

        self.sign_in_button = tk.Button(self.display_frame, text="I'm back", command=self.sign_in, bg="#f44336", fg="white", font=("Comic Sans MS", 12))
        self.sign_in_button.pack(pady=5)
        self.sign_in_button.pack_forget()

        self.mr_stewart_label = tk.Label(self.display_frame, text="Mr. Stewart - Room 112", bg="#FFA500", font=("Comic Sans MS", 12))
        self.mr_stewart_label.pack()

        self.preview_label = tk.Label(self.display_frame, text="Sign-Out Status:", bg="#FFA500", font=("Comic Sans MS", 12))
        self.preview_label.pack()

        self.student_status_text = tk.Text(self.display_frame, height=10, width=50)
        self.student_status_text.pack()

        self.load_data()
        self.update_display()
        self.update_student_dropdown()

        # Bind event to class selector
        self.selected_class.trace_add("write", self.update_student_dropdown)

        # Load Google Sheets credentials
        self.credentials = service_account.Credentials.from_service_account_file('credentials.json') # replace 'credentials.json' with your credentials file
        self.client = gspread.authorize(self.credentials)
        self.sheet = self.client.open("SignOutLog").sheet1  # replace "SignOutLog" with the name of your Google Sheet

    def sign_out(self):
        student = self.student_var.get()
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("sign_out_log.csv", "a") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([time_now, student, "Out"])
        self.sheet.append_row([time_now, student, "Out"])  # Write data to Google Sheet
        self.update_display()

    def sign_in(self):
        student = self.student_var.get()
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("sign_out_log.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)
        with open("sign_out_log.csv", "w") as csvfile:
            writer = csv.writer(csvfile)
            for row in data:
                if row[1] == student and row[2] == "Out":
                    row[0] = time_now
                    row[2] = "In"
                writer.writerow(row)
        self.sheet.append_row([time_now, student, "In"])  # Write data to Google Sheet
        self.update_display()

    def update_display(self):
        self.student_status_text.delete("1.0", tk.END)
        with open("sign_out_log.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[2] == "Out":
                    self.student_status_text.insert(tk.END, f"{row[1]} is in the restroom\n")
                    self.sign_out_button.pack_forget()
                    self.sign_in_button.pack()
                    break
                else:
                    self.student_status_text.insert(tk.END, f"No student is currently out\n")
                    self.sign_in_button.pack_forget()
                    self.sign_out_button.pack()

    def load_data(self):
        try:
            with open("sign_out_log.csv", "r") as csvfile:
                pass
        except FileNotFoundError:
            with open("sign_out_log.csv", "w") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Timestamp", "Student", "Status"])

    def update_student_dropdown(self, *args):
        self.student_var.set('')
        self.student_dropdown['menu'].delete(0, 'end')
        for student in self.class_rosters[self.selected_class.get()]:
            self.student_dropdown['menu'].add_command(label=student, command=tk._setit(self.student_var, student))


if __name__ == "__main__":
    root = tk.Tk()
    app = SignOutApp(root)
    root.mainloop()
