# sqlite db communication
import sqlite3

#
# Very basic SQLite wrapper
#
# Creates table from schema
# Provides small set of utility functions to query the database
#
# If you need to change the schema of an already created table, reset the database
# If you need to reset the database, just delete the database file (db_table.DB_NAME)
#
class db_table:

    # SQLite database filename
    DB_NAME = "interview_test.db"

    #
    # model initialization
    # records table name and schema
    # creates the table if it does not exist yet in DB
    #
    # \param name    string                name of the DB table
    # \param schema  dict<string, string>  schema of DB table, mapping column name to their DB type & constraint
    #
    # Example: table("users", { "id": "integer PRIMARY KEY", "name": "text" })
    #
    def __init__(self, name, schema):
        # error handling
        if not name:
            raise RuntimeError("invalid table name")
        if not schema:
            raise RuntimeError("invalid database schema")

        # init fields and initiate database connection
        self.name    = name
        self.schema  = schema
        self.db_conn = sqlite3.connect(self.DB_NAME)
        
        # ensure the table is created
        self.create_table()

    #
    # CREATE TABLE IF NOT EXISTS wrapper
    # Create the database table based on self.name and self.schema
    # If table already exists, nothing is done even if the schema has changed
    # If you need to apply schema changes, please delete the database file
    #
    def create_table(self):
        # { "id": "integer", "name": "text" } -> "id integer, name text"
        columns_query_string = ', '.join([ "%s %s" % (k,v) for k,v in self.schema.items() ]) # Change iteritems to items

        # CREATE TABLE IF NOT EXISTS users (id integer PRIMARY KEY, name text)
        #
        # Note that columns are formatted into the string without using sqlite safe substitution mechanism
        # The reason is that sqlite does not provide substitution mechanism for columns parameters
        # In the context of this project, this is fine (no risk of user malicious input)
        self.db_conn.execute("CREATE TABLE IF NOT EXISTS %s (%s)" % (self.name, columns_query_string))
        self.db_conn.commit()

    #
    # SELECT wrapper
    # Query the database by applying the specified filters
    #
    # \param columns  array<string>         columns to be fetched. if empty, will query all the columns
    # \param where    dict<string, string>  where filters to be applied. only combine them using AND and only check for strict equality
    #
    # \return [ { col1: val1, col2: val2, col3: val3 } ]
    #
    # Example table.select(["name"], { "id": "42" })
    #         table.select()
    #         table.select(where={ "name": "John" })
    #
    def select(self, columns = [], where = {}):
        # by default, query all columns
        if not columns:
            columns = [ k for k in self.schema ]

        # build query string
        columns_query_string = ", ".join(columns)
        #query                = "SELECT %s FROM %s" % (columns_query_string, self.name)
        query                = f"SELECT {columns_query_string} FROM {self.name}" # update query string to f string for it to work properly
        # build where query string
        where_values = []
        if where:
            where_query_string = []
            for k, v in where.items():
                if k == 'speaker':
                    where_query_string.append(f"{k} LIKE ?")
                    where_values.append(f"%{v}%")  # Using LIKE for partial match to deal with case of multiple speakers
                else:
                    where_query_string.append(f"{k} = ?")
                    where_values.append(v)
            query += " WHERE " + ' AND '.join(where_query_string)
        
        
        # SELECT id, name FROM users [ WHERE id=42 AND name=John ]
        #
        # Note that columns are formatted into the string without using sqlite safe substitution mechanism
        # The reason is that sqlite does not provide substitution mechanism for columns parameters
        # In the context of this project, this is fine (no risk of user malicious input)
        # for row in self.db_conn.execute(query, where_values):
        #     result_row = {}
        #     # convert from (val1, val2, val3) to { col1: val1, col2: val2, col3: val3 }
        #     for i in range(0, len(columns)):
        #         result_row[columns[i]] = row[i]
        #     result.append(result_row)

        # Add to matched_rows instead of final result because must find and add subsessions to final result

        matched_rows = []
        for row in self.db_conn.execute(query, where_values):
            result_row = {columns[i]: row[i] for i in range(len(columns))}
            matched_rows.append(result_row)

        # Get all rows to easily find subsessions of sessions
        all_rows_query = f"SELECT {columns_query_string} FROM {self.name}"
        all_rows = list(self.db_conn.execute(all_rows_query))

        sessions = {}
        last_session_id = None
        # Find all sessions and their subsessions and add to sessions dict
        for row in all_rows:
            row_dict = {columns[i]: row[i] for i in range(len(columns))}
            if row_dict['session_type'] == 'session':
                last_session_id = row_dict['id']
                sessions[last_session_id] = [row_dict]
            else:
                sessions[last_session_id].append(row_dict)

        result = []

        # Get all session ID's of matching sessions and their subsessions
        session_ids = set()
        for matched_row in matched_rows:
            if matched_row['session_type'] == 'session':
                session_id = matched_row['id']
                session_ids.add(session_id)
            else:
                for session_id, subsessions in sessions.items():
                    if matched_row in subsessions:
                        session_ids.add(session_id)
                        break
        
        # Add all matching sessions and their subsessions to final result
        for session_id in session_ids:
            result.extend(sessions.get(session_id, []))

        return result

    #
    # INSERT INTO wrapper
    # insert the given item into database
    #
    # \param item  dict<string, string>   item to be insert in DB, mapping column to value
    #
    # \return id of the created record
    #
    # Example table.insert({ "id": "42", "name": "John" })
    #
    def insert(self, item):
        # build columns & values queries
        columns_query = ", ".join(item.keys())
        placeholders = ", ".join(["?"] * len(item))
        values = list(item.values())
        # values_query  = ", ".join([ "'%s'" % v for v in item.values()])
        #print(len(item.values()))
        #print(item["Speakers"])
        # INSERT INTO users(id, name) values (42, John)
        #
        # Note that columns are formatted into the string without using sqlite safe substitution mechanism
        # The reason is that sqlite does not provide substitution mechanism for columns parameters
        # In the context of this project, this is fine (no risk of user malicious input)

        cursor = self.db_conn.cursor()
        # cursor.execute("INSERT INTO %s (%s) VALUES (%s)" % (self.name, columns_query, values_query))
        cursor.execute(f"INSERT INTO {self.name} ({columns_query}) VALUES ({placeholders})", values)
        cursor.close()
        self.db_conn.commit()
        return cursor.lastrowid

    #
    # UPDATE wrapper
    # update multiple rows matching the specified condition
    #
    # \param values  dict<string, string>  values to be updates, mapping column to value
    # \param where   dict<string, string>  where filters to be applied. only combine them using AND and only check for strict equality
    #
    # \return number of updated records
    #
    # Example table.update({ "name": "Simon" }, { "id": 42 })
    #
    def update(self, values, where):
        # build set & where queries
        set_query   = ", ".join(["%s = '%s'" % (k,v) for k,v in values.iteritems()])
        where_query = " AND ".join(["%s = '%s'" % (k,v) for k,v in where.iteritems()])

        # UPDATE users SET name = Simon WHERE id = 42
        #
        # Note that columns are formatted into the string without using sqlite safe substitution mechanism
        # The reason is that sqlite does not provide substitution mechanism for columns parameters
        # In the context of this project, this is fine (no risk of user malicious input)
        cursor = self.db_conn.cursor()
        cursor.execute("UPDATE %s SET %s WHERE %s" % (self.name, set_query, where_query))
        cursor.close()
        self.db_conn.commit()
        return cursor.rowcount

    #
    # Close the database connection
    #
    def close(self):
        self.db_conn.close()
