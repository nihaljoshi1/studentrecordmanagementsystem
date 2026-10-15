import csv
import os
import re
import sys
from datetime import datetime

# Anchor to the app's location, not the folder you launched from.
# Frozen (PyInstaller exe): next to the exe. Normal run: next to this file.
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "data", "students.csv")
FIELDS = ["StudentID", "FullName", "Gender", "DOB", "Course",
          "Semester", "Mobile", "Email", "Address"]
REQUIRED = ["StudentID", "FullName", "Gender", "DOB", "Course",
            "Semester", "Mobile", "Email"]


def ensure_csv_exists():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()


def load_students():
    """Raises ValueError if the CSV header is wrong, instead of silently
    returning nothing (which would wipe the file on the next save)."""
    ensure_csv_exists()
    # utf-8-sig also reads files re-saved by Excel (which adds a BOM)
    with open(DATA_FILE, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError(
                "students.csv header does not match.\n"
                f"Expected: {','.join(FIELDS)}\n"
                f"Found: {','.join(reader.fieldnames or [])}"
            )
        return [row for row in reader if row.get("StudentID")]


def save_students(students):
    ensure_csv_exists()
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(students)


def is_duplicate_id(student_id, students, exclude_id=None):
    sid = student_id.strip().casefold()
    ex = exclude_id.strip().casefold() if exclude_id else None
    return any(
        s["StudentID"].strip().casefold() == sid and sid != ex
        for s in students
    )


def validate_student(data):
    errors = []

    for field in REQUIRED:
        if not data.get(field, "").strip():
            errors.append(f"{field} is required.")

    dob = data.get("DOB", "").strip()
    if dob:
        try:
            if datetime.strptime(dob, "%Y-%m-%d") > datetime.now():
                errors.append("DOB cannot be in the future.")
        except ValueError:
            errors.append("DOB must be a real date in YYYY-MM-DD format.")

    semester = data.get("Semester", "").strip()
    if semester and not re.fullmatch(r"[1-8]", semester):
        errors.append("Semester must be a number from 1 to 8.")

    mobile = data.get("Mobile", "").strip()
    if mobile and not re.fullmatch(r"[0-9]{10}", mobile):
        errors.append("Mobile number must be exactly 10 digits.")

    email = data.get("Email", "").strip()
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        errors.append("Email is invalid.")

    return errors

# ---------------- CRUD (used by main.py) ----------------
def _clean(data):
    return {f: str(data.get(f, "")).strip() for f in FIELDS}


def get_all_students():
    return load_students()


def get_total_count():
    return len(load_students())


def add_student(data):
    """Returns (success, message)."""
    data = _clean(data)
    students = load_students()
    errors = validate_student(data)
    if data["StudentID"] and is_duplicate_id(data["StudentID"], students):
        errors.append(f"Student ID '{data['StudentID']}' already exists.")
    if errors:
        return False, "\n".join(errors)
    students.append(data)
    save_students(students)
    return True, f"Student '{data['StudentID']}' added successfully."


def update_student(student_id, data):
    """Returns (success, message). The ID itself is never changed."""
    students = load_students()
    index = next((i for i, s in enumerate(students)
                  if s["StudentID"] == student_id), None)
    if index is None:
        return False, f"Student ID '{student_id}' not found."
    data = _clean(data)
    data["StudentID"] = student_id
    errors = validate_student(data)
    if errors:
        return False, "\n".join(errors)
    students[index] = data
    save_students(students)
    return True, f"Student '{student_id}' updated successfully."


def delete_student(student_id):
    """Returns (success, message)."""
    students = load_students()
    remaining = [s for s in students if s["StudentID"] != student_id]
    if len(remaining) == len(students):
        return False, f"Student ID '{student_id}' not found."
    save_students(remaining)
    return True, f"Student '{student_id}' deleted successfully."


def search_students(query):
    """Exact ID match or partial, case-insensitive name match."""
    q = query.strip().casefold()
    if not q:
        return load_students()
    return [s for s in load_students()
            if s["StudentID"].strip().casefold() == q
            or q in s["FullName"].casefold()]