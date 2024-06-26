import xlrd
from db_table import db_table
import sys

# Check if correct number of command-line arguments
n = len(sys.argv)
if n != 2:
    print("Must have 1 command-line argument denoting the Excel spreadsheet to be imported.")
    sys.exit()

excel_file = sys.argv[1]

# Check if Excel file is passed
arg = excel_file.split('.')
if len(arg) != 2 or arg[1] != 'xls':
    print("Must have Excel file as command-line argument.")
    sys.exit()

# Create the agenda table
agenda_table = db_table("agenda", {
    "id": 'integer PRIMARY KEY',
    "date": "text NOT NULL",
    "time_start": "text NOT NULL",
    "time_end": "text NOT NULL",
    "session_type": "text NOT NULL",
    "title": "text NOT NULL",
    "location": "text",
    "description": "text",
    "speaker": "text"
    }
)

# Open the Excel workbook
book = xlrd.open_workbook(excel_file)

# Select the first sheet
sheet = book.sheet_by_index(0)

# Iterate through rows of Excel sheet and insert agenda data into databse by column
for row_index in range(17, sheet.nrows):

    # Get all values in current row
    curr_date = sheet.cell_value(row_index, 0).lower()
    curr_time_start = sheet.cell_value(row_index, 1).lower()
    curr_time_end = sheet.cell_value(row_index, 2).lower()
    curr_session_type = sheet.cell_value(row_index, 3).lower()
    curr_session_title = sheet.cell_value(row_index, 4).lower()
    curr_room_location = sheet.cell_value(row_index, 5).lower()
    curr_description = sheet.cell_value(row_index, 6).lower()
    curr_speakers = sheet.cell_value(row_index, 7).lower()
    
    # Format data properly for insert
    row = {
        "date": curr_date,
        "time_start": curr_time_start,
        "time_end": curr_time_end,
        "session_type": curr_session_type,
        "title": curr_session_title,
        "location": curr_room_location,
        "description": curr_description,
        "speaker": curr_speakers
    }

    # Insert data into agenda table
    agenda_table.insert(row)

agenda_table.close()