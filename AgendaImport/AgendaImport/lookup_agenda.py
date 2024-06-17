from db_table import db_table
import sys

column = sys.argv[1].lower()
value = " "
value = value.join(sys.argv[2:]).lower()
table_columns = ["date", "time_start", "time_end", "title", "location", "description", "speaker"]

# Check if proper column is passed
if column not in table_columns:
    print("Must input proper column.")
    sys.exit()

# Access existing agenda table
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

# Select all rows that match the column name and value
selected_rows = agenda_table.select([k for k in agenda_table.schema], {column: value})

# Format output
for j in range(len(selected_rows)):
    for k in selected_rows[j]:
        print(selected_rows[j][k], "\t", end=" ")
    print()
