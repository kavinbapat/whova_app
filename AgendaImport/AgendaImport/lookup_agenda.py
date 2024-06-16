from db_table import db_table
import sys

# # Check if correct number of command-line arguments
# n = len(sys.argv)
# if n != 3:
#     print("Must have 2 command-line argument denoting the column being matched and the value being matched.")
#     sys.exit()

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



# result = []
# session_to_subsessions = {}
# last_session = None

# for row in all_rows:
#     if row['session_type'] == 'session':
#         last_session = row
#         session_to_subsessions[row['id']] = [row]
#     elif row['session_type'] == 'subsession' and last_session:
#         session_to_subsessions[last_session['id']].append(row)

# for match in selected_rows:
#     if match['session_type'] == 'session':
#         result.extend(session_to_subsessions.get(match['id'], []))

# for j in range(len(result)):
#     for k in result[j]:
#         print(result[j][k], "\t", end=" ")
#     print("\n")

selected_rows = agenda_table.select([i for i in agenda_table.schema], {column: value})
all_rows = agenda_table.select([i for i in agenda_table.schema])

# Identify sessions and their subsessions
result = []
last_session = None
session_to_subsessions = {}

for row in all_rows:
    if row['session_type'] == 'session':
        last_session = row
        session_to_subsessions[row['id']] = [row]
    elif row['session_type'] == 'subsession' and last_session:
        session_to_subsessions[last_session['id']].append(row)

# Include matching sessions and their subsessions
for match in selected_rows:
    if match['session_type'] == 'session':
        result.extend(session_to_subsessions.get(match['id'], []))
    elif match['session_type'] == 'subsession':
        # Ensure to include the parent session of this subsession
        for session_id, subsessions in session_to_subsessions.items():
            if match in subsessions:
                result.extend(subsessions)
                break

for j in range(len(result)):
    for k in result[j]:
        print(result[j][k], "\t", end=" ")
    print("\n")
