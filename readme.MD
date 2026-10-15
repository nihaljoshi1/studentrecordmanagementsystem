# Student Record Management System

A desktop application for managing student records, built with Python and CustomTkinter. All data is stored locally in a CSV file, so no database or installation is needed.

Developed as a 5th semester diploma minor project.

## Features

- Add, update and delete student records
- View all students in a table
- Search by Student ID (exact match) or name (partial, case-insensitive)
- Live total student count
- Input validation with clear error messages
- Duplicate Student ID prevention
- Delete confirmation dialog
- Student ID is locked while editing a record
- CSV file and `data/` folder are created automatically on first run

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3 |
| GUI | CustomTkinter (built on Tkinter) |
| Table | `ttk.Treeview` |
| Storage | CSV file (`csv` module) |

Developed and tested on Python 3.14 on Windows.

## Project Structure

```
StudentRecordManagement/
├── main.py              GUI layer: layout, widgets, button handlers
├── utils.py             Data layer: CSV I/O, validation, CRUD operations
├── data/
│   └── students.csv     Created automatically on first run
├── requirements.txt
├── .gitignore
└── README.md
```

`main.py` never reads or writes the CSV directly. All data logic lives in `utils.py`, and its functions return a `(success, message)` pair that the GUI displays in a dialog.

## Student Fields

| Field | Required | Rules |
|---|---|---|
| StudentID | Yes | Unique (case-insensitive), cannot be changed after creation |
| FullName | Yes | |
| Gender | Yes | Male, Female or Other |
| DOB | Yes | `YYYY-MM-DD`, a real date, not in the future |
| Course | Yes | |
| Semester | Yes | Number from 1 to 8 |
| Mobile | Yes | Exactly 10 digits |
| Email | Yes | Basic `name@domain.tld` format |
| Address | No | |

## Installation

1. Install Python 3 from [python.org](https://www.python.org/downloads/) and make sure `tkinter` is included (it is by default on Windows).
2. Clone or download this project, then open a terminal in the project folder.
3. Create and activate a virtual environment:

```
   python -m venv venv
   venv\Scripts\activate
```

4. Install the dependencies:

```
   pip install -r requirements.txt
```

## Running the Application

```
python main.py
```

On the first launch, `data/students.csv` is created automatically with this header:

```
StudentID,FullName,Gender,DOB,Course,Semester,Mobile,Email,Address
```

## How to Use

| Action | Steps |
|---|---|
| Add a student | Fill in the form on the left and click **Add** |
| Edit a student | Click a row in the table, change the fields, click **Update**. The Student ID is locked |
| Delete a student | Click a row in the table, click **Delete**, confirm the dialog |
| Add another student after editing | Click **Clear** first. This unlocks the Student ID field |
| Search | Type an ID or part of a name in the search box, press Enter or click **Search** |
| Show all students again | Click **Refresh** |
| Quit | Click **Exit** |

## Building a Standalone Executable (Windows)

From the activated virtual environment:

```
pip install -U pyinstaller
pyinstaller --noconsole --onedir --name StudentRecordManagement --collect-all customtkinter main.py
```

The result is in `dist\StudentRecordManagement\`. Run `StudentRecordManagement.exe` from that folder. The `data/` folder is created next to the executable on first run.

To distribute it, zip the whole `StudentRecordManagement` folder (the executable needs the files beside it) and unzip before running. Delete any test `data/` folder before zipping.

## Troubleshooting

| Problem | Solution |
|---|---|
| "Cannot write to students.csv" | The file is open in Excel or another program. Close it and try again |
| "Data Error: students.csv header does not match" | The first line of the CSV was edited. Restore it to exactly the header shown above |
| Exe closes immediately | Rebuild without `--noconsole` to see the error message |
| Windows SmartScreen warning on the exe | The executable is unsigned. Click "More info", then "Run anyway" |
| `ModuleNotFoundError: customtkinter` | Activate the virtual environment and run `pip install -r requirements.txt` |

## Known Limitations

- Single user only. Two instances writing at the same time can overwrite each other's changes.
- No automatic backup. Copy `data/students.csv` regularly if the records matter.
- The whole CSV is rewritten on every change, which is fine for hundreds of records but not for large datasets.
- No sorting, pagination, import or export.
- A search replaces the table contents until **Refresh** is clicked.
- No login or access control.