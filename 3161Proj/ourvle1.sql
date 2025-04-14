CREATE DATABASE ourvle1;
USE ourvle1;

-- USERS TABLE
CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(255) NOT NULL UNIQUE, 
    FirstName VARCHAR(255),
    LastName VARCHAR(255) NOT NULL,
    Password VARCHAR(255),
    Role ENUM('admin', 'lecturer', 'students') NOT NULL
);

-- COURSES TABLE
CREATE TABLE Courses (
    CourseID INT PRIMARY KEY AUTO_INCREMENT,
    CourseCode VARCHAR(20) UNIQUE,
    CourseName VARCHAR(100),
    LecturerID INT,
    FOREIGN KEY (LecturerID) REFERENCES Users(UserID)
);

-- ENROLLMENTS TABLE
CREATE TABLE Enrollments (
    StudentID INT,
    CourseID INT,
    PRIMARY KEY (StudentID, CourseID),
    FOREIGN KEY (StudentID) REFERENCES Users(UserID),
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);

-- CALENDAR EVENTS
CREATE TABLE CalendarEvents (
    EventID INT PRIMARY KEY AUTO_INCREMENT,
    CourseID INT,
    Title VARCHAR(255),
    EventDate DATE,
    Description TEXT,
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);

-- FORUMS
CREATE TABLE Forums (
    ForumID INT PRIMARY KEY AUTO_INCREMENT,
    CourseID INT,
    Title VARCHAR(255), 
    CreatedBy INT,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID),
    FOREIGN KEY (CreatedBy) REFERENCES Users(UserID)
);

-- THREADS
CREATE TABLE Threads (
    ThreadID INT PRIMARY KEY AUTO_INCREMENT,
    ForumID INT, 
    Title VARCHAR(255),
    CreatedBy INT,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ForumID) REFERENCES Forums(ForumID),
    FOREIGN KEY (CreatedBy) REFERENCES Users(UserID)
);

-- REPLIES
CREATE TABLE Replies (
    ReplyID INT PRIMARY KEY AUTO_INCREMENT, 
    ThreadID INT,
    ParentReplyID INT NULL,
    Content TEXT,
    CreatedBy INT,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ThreadID) REFERENCES Threads(ThreadID),
    FOREIGN KEY (ParentReplyID) REFERENCES Replies(ReplyID),
    FOREIGN KEY (CreatedBy) REFERENCES Users(UserID)
);

-- COURSE CONTENT
CREATE TABLE CourseContent (
    ContentID INT PRIMARY KEY AUTO_INCREMENT, 
    CourseID INT,
    Title VARCHAR(255),
    ContentLink TEXT,
    UploadedBy INT,
    UploadDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID),
    FOREIGN KEY (UploadedBy) REFERENCES Users(UserID)
);

-- ASSIGNMENTS
CREATE TABLE Assignments (
    AssignmentID INT PRIMARY KEY AUTO_INCREMENT, 
    CourseID INT,
    Title VARCHAR(255),
    Description TEXT, 
    DueDate DATE,
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);

-- SUBMISSIONS
CREATE TABLE Submissions (
    SubmissionID INT PRIMARY KEY AUTO_INCREMENT, 
    AssignmentID INT, 
    StudentID INT,
    FileLink TEXT, 
    SubmissionDate DATETIME, 
    FOREIGN KEY (AssignmentID) REFERENCES Assignments(AssignmentID),
    FOREIGN KEY (StudentID) REFERENCES Users(UserID)
);

-- GRADES
CREATE TABLE Grades (
    GradeID INT PRIMARY KEY AUTO_INCREMENT,
    SubmissionID INT, 
    Grade DECIMAL(5,2),
    GradedBy INT,
    GradedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SubmissionID) REFERENCES Submissions(SubmissionID),
    FOREIGN KEY (GradedBy) REFERENCES Users(UserID)
);
