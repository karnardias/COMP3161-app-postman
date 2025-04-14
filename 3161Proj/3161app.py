from flask import Flask, request, make_response, jsonify,session
import mysql.connector

app = Flask(__name__)
app.secret_key = "ourvlekey"

def getdbconnection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  
        database="ourvle1"
    )


@app.route("/tester", methods=["GET"])  
def tester():
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()  
        cursor.execute("SELECT DATABASE();")
        database_name = cursor.fetchone()
        cursor.close()
        cnx.close()
        return make_response({"Message": "Connected to database", "database": database_name[0]}, 200) 
    except Exception as e:
        return make_response({"Error": str(e)}, 500) 



@app.route("/hello_world", methods=["GET"])
def hello_world():
    return make_response({"Message": "hello world"}, 200)


@app.route("/registeruser", methods=["POST"])
def registeruser():
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()
        data = request.json

        if not isinstance(data, dict):
            return make_response({"Error": "Invalid input format"}, 400)

        username = data["username"]
        password = data["password"]
        fname = data["firstName"]
        lname = data["lastName"]
        role = data["role"]
        
        if not all([username, password, fname, lname, role]):
            return make_response({"Error": "Username,passsword,firstname,lastname and role are required"}, 400)
        if role not in ["admin", "lecturer", "students"]:
            return make_response({"Error": "Invalid role. Must be admin, lecturer, or students."}, 400)


        cursor.execute("INSERT INTO Users (Username, FirstName, LastName, Password, Role) VALUES (%s, %s, %s, %s, %s)", 
                       (username, fname, lname, password, role))
        
        cnx.commit()
        return make_response({"Success": "User  added"}, 201)
    except Exception as e:
        return make_response({"Error": str(e)}, 400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
   

@app.route("/login", methods=["POST"])
def loginuser():
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()
        data = request.json
        username = data["username"]
        password = data["password"]

        cursor.execute("SELECT UserID, Password, Role FROM Users WHERE Username = %s", (username,))
        user = cursor.fetchone()

        if user is None:
            return make_response({"Error": "Wrong Username or Password"}, 401)
        if user[1] == password:
            session["role"] = user[2]  
            session["user_id"] = user[0] 
            return make_response({"Message": "Login successful", "userId": user[0]}, 200)
        else:
            return make_response({"Error": "Wrong Username or Password"}, 401)
    except Exception as e:
        return make_response({"Error": str(e)}, 400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
            

def getcurrentuserrole():
    return session.get("role")  
def getcurrentuserid():
    return session.get("user_id")  
    
@app.route("/createcourses", methods=["POST"])
def createcourse():
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()
        data = request.json
        course_id = data.get("CourseID")  
        course_code = data.get("CourseCode")
        course_name = data.get("CourseName")
        lecturer_id = data.get("LecturerID")

     
        currentrole = getcurrentuserrole()
        
        if currentrole != "admin":
        	return make_response({"Error": "Only admins can create courses"}, 403)
        	

        cursor.execute("INSERT INTO Courses (CourseID, CourseCode, CourseName, LecturerID) VALUES (%s, %s, %s, %s)",(course_id, course_code, course_name, lecturer_id))
        
        cnx.commit()
        return make_response({"Message": "Course created successfully!"}, 201)
    except Exception as e:
        return make_response({"Error": str(e)}, 400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
            
@app.route("/courses/<int:course_id>/assignlecturer", methods=["POST"])
def assignlecturertocourse(course_id):
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()

        current_role = getcurrentuserrole()
        if current_role != "admin":
            return make_response({"Error": "Only admins can assign lecturers to courses"}, 403)

        data = request.json
        lecturer_id = data.get("LecturerID")

        if not lecturer_id:
            return make_response({"Error": "LecturerID is required"}, 400)

        cursor.execute("SELECT LecturerID FROM Courses WHERE CourseID = %s", (course_id,))
        existing_lecturer = cursor.fetchone()

        if existing_lecturer and existing_lecturer[0] is not None:
            return make_response({"Error": "This course already has a lecturer assigned"}, 400)

        cursor.execute("UPDATE Courses SET LecturerID = %s WHERE CourseID = %s", (lecturer_id, course_id))
        cnx.commit()

        return make_response({"Message": "Lecturer assigned to course successfully!"}, 200)

    except Exception as e:
        return make_response({"Error": str(e)}, 400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
            
@app.route("/allcourses", methods=["GET"])
def retrieveallcourses():
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()
        cursor.execute("SELECT CourseID, CourseCode, CourseName, LecturerID FROM Courses")
        courses = cursor.fetchall()

        course_list = [{"CourseID": row[0], "CourseCode": row[1], "CourseName": row[2], "LecturerID": row[3]} for row in courses]
        return make_response(course_list, 200)
    except Exception as e:
        return make_response({"Error": str(e)}, 400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
            
@app.route("/students/<int:student_id>/courses", methods=["GET"])
def retrivecourse4student(student_id):
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()
        
        cursor.execute("SELECT Role FROM Users WHERE UserID = %s", (student_id,))
        user = cursor.fetchone()
        if user is None or user[0] != "students":
            return make_response({"Error": "Invalid student ID or user is not a student"}, 400)

 
        cursor.execute(""" SELECT Courses.CourseID, Courses.CourseCode, Courses.CourseName FROM Courses JOIN Enrollments ON Courses.CourseID = Enrollments.CourseID WHERE Enrollments.StudentID = %s """, (student_id,))
        courses = cursor.fetchall()

        course_list = [{"CourseID": row[0], "CourseCode": row[1], "CourseName": row[2]} for row in courses]
        return make_response(course_list, 200)
    except Exception as e:
        return make_response({"Error": str(e)}, 400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
            
@app.route("/lecturers/<int:lecturer_id>/courses", methods=["GET"])
def retrivecourse4lecturer(lecturer_id):
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()
        cursor.execute("SELECT Role FROM Users WHERE UserID = %s", (lecturer_id,))

        user = cursor.fetchone()
        if user is None or user[0] != "lecturer":
            return make_response({"Error": "Invalid lecturer ID or user is not a lecturer"}, 400)

        cursor.execute("""SELECT CourseID, CourseCode, CourseName FROM Courses WHERE LecturerID = %s """, (lecturer_id,))
        courses = cursor.fetchall()

        course_list = [{"CourseID": row[0], "CourseCode": row[1], "CourseName": row[2]} for row in courses]
        return make_response(course_list, 200)
    except Exception as e:
        return make_response({"Error": str(e)}, 400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
                      

@app.route("/students/<int:student_id>/courses/registerstudentincourse", methods=["POST"])
def registerstudentincourse(student_id):
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()

        user_id = session["user_id"]
        cursor.execute("SELECT Role FROM Users WHERE UserID = %s", (user_id,))
        user = cursor.fetchone()

        if user is None or user[0] != "students":
            return make_response({"Error": "Only students can register in courses"}, 403)

        data = request.json
        course_id = data["courseId"]

      
        cursor.execute("SELECT 1 FROM Enrollments WHERE StudentID = %s AND CourseID = %s", (user_id, course_id))
        if cursor.fetchone():
            return make_response({"Error": "Already enrolled in this course"}, 400)

      
        cursor.execute("INSERT INTO Enrollments (StudentID, CourseID) VALUES (%s, %s)", (user_id, course_id))
        cnx.commit()
        return make_response({"Message": "Successfully registered in the course!"}, 201)

    except Exception as e:
        return make_response({"Error": str(e)}, 400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
 
 

@app.route("/courses/<int:course_id>/members", methods=["GET"])
def retrievemembers(course_id):
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()
        cursor.execute("""SELECT Users.FirstName, Users.LastName, Users.UserID FROM Users JOIN Enrollments ON Users.UserID = Enrollments.StudentID WHERE Enrollments.CourseID = %s """, (course_id,))
        members = cursor.fetchall()
        
        member_list = [{"FirstName": row[0], "LastName": row[1], "UserID": row[2]}  for row in members]
        return make_response(member_list, 200)
    except Exception as e:
        return make_response({"Error": str(e)}, 400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
            
           
@app.route("/courses/<int:course_id>/calendar_events", methods=["GET"])
def retrievecalendareventsforcourse(course_id):
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()
        
        cursor.execute("SELECT EventID, Title, EventDate, Description FROM CalendarEvents WHERE CourseID = %s", (course_id,))
        events = cursor.fetchall()

        event_list = [{"EventID": row[0], "Title": row[1], "EventDate": row[2], "Description": row[3]} for row in events]
        return make_response(event_list, 200)
    except Exception as e:
        return make_response({"Error": str(e)}, 400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

@app.route("/students/<int:student_id>/calendarevents/<string:event_date>", methods=["GET"])
def retrievecalendareventsforstudent(student_id, event_date):
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()

        cursor.execute("""SELECT CourseID FROM Enrollments WHERE StudentID = %s """, (student_id,))
        enrolled_courses = cursor.fetchall()

        if not enrolled_courses:
            return make_response({"Error": "Student is not enrolled in any courses"}, 404)


        course_ids = [str(row[0]) for row in enrolled_courses]  
        
        if not course_ids:
            return make_response({"Error": "No enrolled courses found for the student"}, 404)

        coursestring = ", ".join(course_ids) 
        query = f""" SELECT EventID, Title, EventDate, Description FROM CalendarEvents WHERE CourseID IN ({coursestring}) AND EventDate = "{event_date}" """
    
        cursor.execute(query)
        events = cursor.fetchall()

        event_list = [{"EventID": row[0], "Title": row[1], "EventDate": row[2], "Description": row[3]} for row in events]
        return make_response(event_list, 200)
    except Exception as e:
        return make_response({"Error": str(e)}, 400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
            
@app.route("/courses/<int:course_id>/calendarevents", methods=["POST"])
def createcalendarevent(course_id):
    cursor = None
    cnx = None
    try:
        cnx = getdbconnection()
        cursor = cnx.cursor()
        data = request.json

        title = data.get("Title")
        eventdate = data.get("EventDate")
        description = data.get("Description")

        if not all([title, eventdate,description]):
            return make_response({"Error": "Title, Event Date and Description are required"}, 400)

        cursor.execute("""INSERT INTO CalendarEvents (CourseID, Title, EventDate, Description) VALUES (%s, %s, %s, %s) """, (course_id, title, eventdate, description))
        
        cnx.commit()
        return make_response({"Message": "Calendar event created successfully!"}, 201)
    except Exception as e:
        return make_response({"Error": str(e)}, 400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
if __name__ == "__main__":
    app.run(port=4000)
