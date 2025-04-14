import pandas as pd
import mysql.connector

# Database connection
db_config = {
    "host": "localhost",
    "user": "root",
    "password":"",
    "database": "ourvle1"
}

def sql_escape(value):
    if pd.isnull(value):
        return 'NULL'
    return str(value).replace("'", "''")

def generate_unique_username(cursor, base_username):
    username = base_username
    count = 1
    while True:
        cursor.execute("SELECT 1 FROM Users WHERE Username = %s", (username,))
        if not cursor.fetchone():
            return username
        username = f"{base_username}{count}"
        count += 1

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Insert Students
    students_df = pd.read_csv("students.csv")
    with open("students.sql", "w", encoding="utf-8") as f:
        for _, row in students_df.iterrows():
            base_username = f"{row['FirstName'].lower()}.{row['LastName'].lower()}"
            username = generate_unique_username(cursor, base_username)
            sql = f"""INSERT INTO Users (Username, FirstName, LastName, Password, Role)
VALUES ('{sql_escape(username)}', '{sql_escape(row['FirstName'])}', '{sql_escape(row['LastName'])}',
'{sql_escape(row['Password'])}', 'students');
"""
            f.write(sql)
            cursor.execute("SELECT 1 FROM Users WHERE Username = %s", (username,))
            if not cursor.fetchone():  # Only insert if username doesn't exist
                cursor.execute("INSERT INTO Users (Username, FirstName, LastName, Password, Role) VALUES (%s, %s, %s, %s, %s)", 
                               (username, row['FirstName'], row['LastName'], row['Password'], 'students'))

    # Insert Lecturers
    lecturers_df = pd.read_csv("lecturers.csv")
    with open("lecturers.sql", "w", encoding="utf-8") as f:
        for _, row in lecturers_df.iterrows():
            base_username = f"{row['FirstName'].lower()}.{row['LastName'].lower()}"
            username = generate_unique_username(cursor, base_username)
            sql = f"""INSERT INTO Users (Username, FirstName, LastName, Password, Role)
VALUES ('{sql_escape(username)}', '{sql_escape(row['FirstName'])}', '{sql_escape(row['LastName'])}',
'{sql_escape(row['Password'])}', 'lecturer');
"""
            f.write(sql)
            cursor.execute("SELECT 1 FROM Users WHERE Username = %s", (username,))
            if not cursor.fetchone():  # Only insert if username doesn't exist
                cursor.execute("INSERT INTO Users (Username, FirstName, LastName, Password, Role) VALUES (%s, %s, %s, %s, %s)", 
                               (username, row['FirstName'], row['LastName'], row['Password'], 'lecturer'))

    # Insert Admins
    admins_df = pd.read_csv("admins.csv")
    with open("admins.sql", "w", encoding="utf-8") as f:
        for _, row in admins_df.iterrows():
            base_username = f"{row['FirstName'].lower()}.{row['LastName'].lower()}"
            username = generate_unique_username(cursor, base_username)
            sql = f"""INSERT INTO Users (Username, FirstName, LastName, Password, Role)
VALUES ('{sql_escape(username)}', '{sql_escape(row['FirstName'])}', '{sql_escape(row['LastName'])}',
'{sql_escape(row['Password'])}', 'admin');
"""
            f.write(sql)
            cursor.execute("SELECT 1 FROM Users WHERE Username = %s", (username,))
            if not cursor.fetchone():  # Only insert if username doesn't exist
                cursor.execute("INSERT INTO Users (Username, FirstName, LastName, Password, Role) VALUES (%s, %s, %s, %s, %s)", 
                               (username, row['FirstName'], row['LastName'], row['Password'], 'admin'))

    # Insert Courses (temporarily LecturerID = NULL)
    courses_df = pd.read_csv("courses.csv")
    with open("courses.sql", "w", encoding="utf-8") as f:
        for _, row in courses_df.iterrows():
            cursor.execute("SELECT 1 FROM Courses WHERE CourseCode = %s", (row['CourseCode'],))
            if not cursor.fetchone():  # Only insert if course code doesn't exist
                sql = f"""INSERT INTO Courses (CourseCode, CourseName, LecturerID)
    VALUES ('{sql_escape(row['CourseCode'])}', '{sql_escape(row['CourseName'])}', NULL);
    """
                f.write(sql)
                cursor.execute("INSERT INTO Courses (CourseCode, CourseName, LecturerID) VALUES (%s, %s, %s)", 
                               (row['CourseCode'], row['CourseName'], None))

    conn.commit()
    print("All users and courses inserted with unique usernames.")

except mysql.connector.Error as e:
    print(f"MySQL Error: {e}")

finally:
    conn = mysql.connector.connect(**db_config)
    if conn and conn.is_connected():
        cursor.close()
        conn.close()
