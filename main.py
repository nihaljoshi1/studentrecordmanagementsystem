"""
main.py
Student Record Management System: GUI layer.
All data logic lives in utils.py.
"""

from tkinter import ttk, messagebox
import customtkinter as ctk
import utils

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

FIELD_LABELS = [
    ("StudentID", "Student ID"),
    ("FullName", "Full Name"),
    ("Gender", "Gender"),
    ("DOB", "Date of Birth (YYYY-MM-DD)"),
    ("Course", "Course"),
    ("Semester", "Semester"),
    ("Mobile", "Mobile Number"),
    ("Email", "Email Address"),
    ("Address", "Address"),
]

TABLE_COLUMNS = [f[0] for f in FIELD_LABELS]
TABLE_HEADINGS = [f[1] for f in FIELD_LABELS]


class StudentApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Student Record Management System")
        self.geometry("1150x600")
        self.minsize(950, 550)

        # None = Add mode, string = Update mode (ID of the loaded record)
        self.editing_id = None
        self.entries = {}

        self._build_layout()
        self.refresh_table()

    # ---------------- LAYOUT ----------------
    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_left_panel()
        self._build_right_panel()

    def _build_left_panel(self):
        left = ctk.CTkFrame(self, width=320, corner_radius=10)
        left.grid(row=0, column=0, sticky="ns", padx=(15, 8), pady=15)
        left.grid_propagate(False)

        ctk.CTkLabel(left, text="Student Details",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 20), padx=15)

        for field_name, label_text in FIELD_LABELS:
            ctk.CTkLabel(left, text=label_text, anchor="w").pack(fill="x", padx=20, pady=(4, 0))

            if field_name == "Gender":
                widget = ctk.CTkComboBox(left, values=["Male", "Female", "Other"], width=260)
                widget.set("Male")
            else:
                widget = ctk.CTkEntry(left, width=260)

            widget.pack(padx=20, pady=(0, 6))
            self.entries[field_name] = widget

        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.pack(pady=(15, 10), fill="x", padx=20)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(btn_frame, text="Add", command=self.on_add).grid(
            row=0, column=0, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(btn_frame, text="Update", command=self.on_update).grid(
            row=0, column=1, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(btn_frame, text="Delete", fg_color="#b3261e", hover_color="#8c1e18",
                      command=self.on_delete).grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(btn_frame, text="Clear", fg_color="gray40", hover_color="gray30",
                      command=self.clear_form).grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        ctk.CTkButton(left, text="Exit", fg_color="gray25", hover_color="gray15",
                      command=self.quit).pack(pady=(5, 15), padx=20, fill="x")

    def _build_right_panel(self):
        right = ctk.CTkFrame(self, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 15), pady=15)
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        top_bar = ctk.CTkFrame(right, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        top_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(top_bar, placeholder_text="Search by Student ID or Name")
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self.on_search())

        ctk.CTkButton(top_bar, text="Search", width=90, command=self.on_search).grid(
            row=0, column=1, padx=4)
        ctk.CTkButton(top_bar, text="Refresh", width=90, command=self.on_refresh).grid(
            row=0, column=2, padx=4)

        self.count_label = ctk.CTkLabel(right, text="Total Students: 0",
                                        font=ctk.CTkFont(size=14, weight="bold"))
        self.count_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 8))

        table_frame = ctk.CTkFrame(right, fg_color="transparent")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.tree = ttk.Treeview(table_frame, columns=TABLE_COLUMNS,
                                 show="headings", selectmode="browse")
        for col, heading in zip(TABLE_COLUMNS, TABLE_HEADINGS):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=110, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ---------------- FORM HELPERS ----------------
    def get_form_data(self):
        return {f: w.get().strip() for f, w in self.entries.items()}

    def set_form_data(self, record):
        # Disabled entries ignore insert/delete, so unlock the ID first
        self.entries["StudentID"].configure(state="normal")
        for field, widget in self.entries.items():
            value = record.get(field, "")
            if isinstance(widget, ctk.CTkComboBox):
                widget.set(value if value else "Male")
            else:
                widget.delete(0, "end")
                widget.insert(0, value)

    def clear_form(self):
        self.entries["StudentID"].configure(state="normal")  # unlock BEFORE clearing
        for widget in self.entries.values():
            if isinstance(widget, ctk.CTkComboBox):
                widget.set("Male")
            else:
                widget.delete(0, "end")
        self.editing_id = None
        self.tree.selection_remove(self.tree.selection())

    def lock_id_field(self):
        self.entries["StudentID"].configure(state="disabled")

    # ---------------- TABLE ----------------
    def refresh_table(self, records=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            if records is None:
                records = utils.get_all_students()
            total = utils.get_total_count()
        except ValueError as e:  # CSV header mismatch
            messagebox.showerror("Data Error", str(e))
            records, total = [], 0

        for r in records:
            values = [r.get(col, "") for col in TABLE_COLUMNS]
            # iid = StudentID so we can look the record up reliably later
            self.tree.insert("", "end", iid=r["StudentID"], values=values)

        self.count_label.configure(text=f"Total Students: {total}")

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        student_id = selected[0]
        # Re-read from CSV: Treeview can mangle values like "007" into 7
        try:
            record = next((r for r in utils.get_all_students()
                           if r["StudentID"] == student_id), None)
        except ValueError as e:
            messagebox.showerror("Data Error", str(e))
            return
        if record is None:
            return
        self.set_form_data(record)
        self.editing_id = record["StudentID"]
        self.lock_id_field()

    # ---------------- ACTIONS ----------------
    def on_add(self):
        if self.editing_id:
            messagebox.showwarning("Record Selected",
                                   "A record is loaded for editing. Click Clear before adding a new student.")
            return
        success, msg = utils.add_student(self.get_form_data())
        if success:
            messagebox.showinfo("Success", msg)
            self.clear_form()
            self.refresh_table()
        else:
            messagebox.showerror("Error", msg)

    def on_update(self):
        if not self.editing_id:
            messagebox.showwarning("No Selection", "Select a student from the table before updating.")
            return
        data = self.get_form_data()
        data["StudentID"] = self.editing_id  # disabled entry may return ""; enforce it
        success, msg = utils.update_student(self.editing_id, data)
        if success:
            messagebox.showinfo("Success", msg)
            self.clear_form()
            self.refresh_table()
        else:
            messagebox.showerror("Error", msg)

    def on_delete(self):
        if not self.editing_id:
            messagebox.showwarning("No Selection", "Select a student from the table before deleting.")
            return
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete student '{self.editing_id}'? This cannot be undone."):
            return
        success, msg = utils.delete_student(self.editing_id)
        if success:
            messagebox.showinfo("Success", msg)
            self.clear_form()
            self.refresh_table()
        else:
            messagebox.showerror("Error", msg)

    def on_search(self):
        try:
            results = utils.search_students(self.search_entry.get())
        except ValueError as e:
            messagebox.showerror("Data Error", str(e))
            return
        if not results:
            messagebox.showinfo("Search", "No matching students found.")
        self.refresh_table(records=results)

    def on_refresh(self):
        self.search_entry.delete(0, "end")
        self.refresh_table()


if __name__ == "__main__":
    try:
        utils.ensure_csv_exists()
    except OSError as e:
        messagebox.showerror("File Error", f"Cannot create data file:\n{e}")
        raise SystemExit(1)
    app = StudentApp()
    app.mainloop()