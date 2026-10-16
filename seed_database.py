import sqlite3
import hashlib
import os

DB_NAME = "studylock.db"

def hash_password(password):
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000
    )
    return salt.hex(), password_hash.hex()


conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")


tables = [
    "course_interests",
    "user_interests",
    "interests",
    "prerequisites",
    "focus_sessions",
    "study_sessions",
    "items",
    "enrollments",
    "courses",
    "users",
    "exams",
    "tasks",
    "students"
]

for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table}")


cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT UNIQUE NOT NULL,
    component TEXT,
    semester TEXT,
    credits INTEGER,
    instructor TEXT
)
""")

cursor.execute("""
CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    status TEXT DEFAULT 'in_progress',
    UNIQUE(user_id, course_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
""")

cursor.execute("""
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER,
    title TEXT NOT NULL,
    item_type TEXT NOT NULL,
    deadline TEXT,
    room TEXT,
    completed INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
""")

cursor.execute("""
CREATE TABLE study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER,
    duration_minutes INTEGER NOT NULL,
    started_at TEXT,
    ended_at TEXT,
    session_date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
""")

cursor.execute("""
CREATE TABLE focus_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    duration_minutes INTEGER,
    focus_score INTEGER,
    distracted_seconds INTEGER,
    started_at TEXT,
    ended_at TEXT,
    session_date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

cursor.execute("""
CREATE TABLE prerequisites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    required_course_id INTEGER NOT NULL,
    FOREIGN KEY(course_id) REFERENCES courses(id),
    FOREIGN KEY(required_course_id) REFERENCES courses(id)
)
""")

cursor.execute("""
CREATE TABLE interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interest_name TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE course_interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    interest_id INTEGER NOT NULL,
    FOREIGN KEY(course_id) REFERENCES courses(id),
    FOREIGN KEY(interest_id) REFERENCES interests(id)
)
""")

cursor.execute("""
CREATE TABLE user_interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    interest_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(interest_id) REFERENCES interests(id)
)
""")

users_raw = [
    ("მარიამ კაპანაძე", "mariam.kapanadze@uni.edu.ge", "password123"),
    ("გიორგი პატარაია", "giorgi.pataria@uni.edu.ge", "password123"),
    ("ნინი მოდებაძე", "nini.modebadze@uni.edu.ge", "password123"),
    ("ელისაბედ გოგუა", "elisabed.gogua@uni.edu.ge", "password123"),
    ("დათო მალანია", "dato.malania@uni.edu.ge", "password123")
]

for full_name, email, password in users_raw:
    salt, password_hash = hash_password(password)
    cursor.execute("""
    INSERT INTO users (full_name, email, password_salt, password_hash)
    VALUES (?, ?, ?, ?)
    """, (full_name, email, salt, password_hash))



courses = [
    # 2sem
    ("Python", "Current Semester", "II", 6, "Nuca Melia"),
    ("Calculus 2", "Current Semester", "II", 6, "Andria Melikishvili"),
    ("Intro to Networking", "Current Semester", "II", 6, "Lia Kapanadze"),
    ("Operating Systems", "Current Semester", "II", 3, "Mikheil Beridze"),
    ("National Language", "Current Semester", "II", 6, "Manana Tsiklauri"),
    ("Theoretical Foundations Of CS", "Current Semester", "II", 3, "Nino Tsulaia"),

    # curriculum 
    ("კალკულუსი (I)", "თავისუფალი კომპონენტი", None, 6, None),
    ("კალკულუსი (II)", "თავისუფალი კომპონენტი", None, 6, None),
    ("სახელმწიფო ენის სპეციალური კურსი", "თავისუფალი კომპონენტი", None, 6, None),
    ("შესავალი მეწარმეობაში", "თავისუფალი კომპონენტი", None, 6, None),
    ("ალბათობის თეორია და მათემატიკური სტატისტიკა", "თავისუფალი კომპონენტი", None, 6, None),
    ("წერის ტექნიკა", "თავისუფალი კომპონენტი", None, 3, None),
    ("ინოვაციების მენეჯმენტი და სტარტაპი", "თავისუფალი კომპონენტი", None, 6, None),

    ("დისკრეტული მათემატიკა", "ძირითადი სწავლის კომპონენტი", "I", 6, None),
    ("პროგრამირების საწყისები (python)", "ძირითადი სწავლის კომპონენტი", "I", 6, None),
    ("კომპიუტერის არქიტექტურა", "ძირითადი სწავლის კომპონენტი", "I", 3, None),
    ("მონაცემთა ბაზების საწყისები", "ძირითადი სწავლის კომპონენტი", "I", 6, None),

    ("კომპიუტერული მეცნიერების თეორიული საფუძვლები", "ძირითადი სწავლის კომპონენტი", "II", 3, None),
    ("ოპერაციული სისტემა", "ძირითადი სწავლის კომპონენტი", "II", 3, None),
    ("პროგრამირება (python)", "ძირითადი სწავლის კომპონენტი", "II", 6, None),

    ("მონაცემთა სტრუქტურები და ალგორითმები (I)", "ძირითადი სწავლის კომპონენტი", "III", 6, None),
    ("წრფივი ალგებრა (გაღრმავებული კურსი)", "ძირითადი სწავლის კომპონენტი", "III", 6, None),
    ("ხელოვნური ინტელექტის საწყისები", "ძირითადი სწავლის კომპონენტი", "III", 3, None),

    ("კომპიუტერული ქსელების საწყისები", "ძირითადი სწავლის კომპონენტი", "IV", 6, None),
    ("მონაცემთა სტრუქტურები და ალგორითმები (II)", "ძირითადი სწავლის კომპონენტი", "IV", 6, None),
    ("პროგრამული ინჟინერია", "ძირითადი სწავლის კომპონენტი", "IV", 6, None),
    ("ხელოვნური ინტელექტი და მანქანური სწავლება", "ძირითადი სწავლის კომპონენტი", "IV", 6, None),

    ("მონაცემთა ბაზების ადმინისტრირება", "ძირითადი სწავლის კომპონენტი", "V", 6, None),
    ("ხელოვნური ინტელექტი, ეთიკა და სამართალი", "ძირითადი სწავლის კომპონენტი", "V", 3, None),
    ("ელექტრომაგნეტიზმის საფუძვლები", "ძირითადი სწავლის კომპონენტი", "V", 6, None),
    ("პროგრამირების პარადიგმები", "ძირითადი სწავლის კომპონენტი", "V", 6, None),
    ("მონაცემთა სტრუქტურები და ალგორითმები (გაღრმავებული კურსი)", "ძირითადი სწავლის კომპონენტი", "V", 6, None),

    ("რიცხვითი მეთოდები", "ძირითადი სწავლის კომპონენტი", "VI", 6, None),
    ("შესავალი ელექტრონიკასა და რობოტიქსში", "ძირითადი სწავლის კომპონენტი", "VI", 6, None),
    ("მანქანური სწავლება (ღრმა დასწავლა)", "ძირითადი სწავლის კომპონენტი", "VI", 6, None),

    ("მონაცემთა მეცნიერება", "ძირითადი სწავლის კომპონენტი", "VII", 6, None),
    ("ბუნებრივი ენის დამუშავება (NLP)", "ძირითადი სწავლის კომპონენტი", "VII", 6, None),
    ("კომპიუტერული ხედვა", "ძირითადი სწავლის კომპონენტი", "VII", 3, None),

    ("Big Data ანალიტიკა", "ძირითადი სწავლის კომპონენტი", "VIII", 6, None),
    ("მონაცემთა უსაფრთხოება", "ძირითადი სწავლის კომპონენტი", "VIII", 6, None),
    ("პრაქტიკული პროექტი", "ძირითადი სწავლის კომპონენტი", "VIII", 6, None),

    ("სტრუქტურული დაპროგრამება", "არჩევითი", None, 6, None),
    ("BlockChain ტექნოლოგიები (IBM Blockain)", "არჩევითი", None, 6, None),
    ("ვებ პროგრამირება (Back End Development)", "არჩევითი", None, 6, None),
    ("ვებ პროგრამირება (Front End Development)", "არჩევითი", None, 6, None),
    ("პროგრამული უზრუნველყოფის ტესტირების საფუძვლები", "არჩევითი", None, 6, None),
    ("მონაცემთა ანალიტიკა (Python)", "არჩევითი", None, 6, None),
    ("მობილური აპლიკაციები", "არჩევითი", None, 3, None),
    ("ობიექტზე ორიენტირებული პროგრამირება (C# ენის ბაზაზე)", "არჩევითი", None, 6, None),
    ("ვებპროგრამირება Flask-ის ბაზაზე", "არჩევითი", None, 6, None),
    ("ინფორმაციული უსაფრთხოება", "არჩევითი", None, 6, None),
    ("ნეირონული ქსელები", "არჩევითი", None, 6, None),
    ("პროგრამული უზრუნველყოფის ავტომატიზირებული ტესტირება", "არჩევითი", None, 6, None),
    ("ვებ პროგრამირება React პლატფორმაზე", "არჩევითი", None, 6, None),
    ("დაპროგრამება JVM პლატფორმაზე (I)", "არჩევითი", None, 6, None),
    ("კრიპტოგრაფიის საფუძვლები", "არჩევითი", None, 6, None),
    ("მობილური აპლიკაციების დეველოპმენტი (Android)", "არჩევითი", None, 6, None),
    ("დაპროგრამება JVM პლატფორმაზე (II)", "არჩევითი", None, 6, None),
    ("კიბერუსაფრთხოება", "არჩევითი", None, 6, None),
    ("აპლიკაციის პროგრამული ინტერფეისის ტესტირება", "არჩევითი", None, 6, None),

    ("აკადემიური წერა", "თავისუფალის არჩევითი", None, 3, None),
    ("ინგლისური ენის პრაქტიკული კურსი (B1)", "უცხო ენები", None, 3, None),
    ("ინგლისური ენის პრაქტიკული კურსი (B2)", "უცხო ენები", None, 6, None),
]

cursor.executemany("""
INSERT INTO courses (course_name, component, semester, credits, instructor)
VALUES (?, ?, ?, ?, ?)
""", courses)


def get_course_id(course_name):
    cursor.execute("SELECT id FROM courses WHERE course_name = ?", (course_name,))
    row = cursor.fetchone()
    if row is None:
        print(f"Missing course: {course_name}")
        return None
    return row[0]


current_courses = [
    "Python",
    "Calculus 2",
    "Intro to Networking",
    "Operating Systems",
    "National Language",
    "Theoretical Foundations Of CS"
]

for user_id in range(1, len(users_raw) + 1):
    for course_name in current_courses:
        course_id = get_course_id(course_name)
        cursor.execute("""
        INSERT INTO enrollments (user_id, course_id, status)
        VALUES (?, ?, ?)
        """, (user_id, course_id, "in_progress"))



items = [
    (1, "Python", "Finish Python project", "Project", "2026-07-14", None, 0),
    (1, "Calculus 2", "Calculus Final Exam", "Exam", "2026-07-16", "A203", 0),
    (1, "Intro to Networking", "Prepare VLAN report", "Task", "2026-07-18", None, 1),
    (1, "Operating Systems", "Operating Systems Quiz", "Quiz", "2026-07-20", "A105", 0),
    (1, "National Language", "Essay submission", "Task", "2026-07-21", None, 0),
    (1, "Theoretical Foundations Of CS", "Review finite automata", "Task", "2026-07-23", None, 0),
]

for user_id, course_name, title, item_type, deadline, room, completed in items:
    course_id = get_course_id(course_name)
    cursor.execute("""
    INSERT INTO items
    (user_id, course_id, title, item_type, deadline, room, completed)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, course_id, title, item_type, deadline, room, completed))


study_sessions = [
    (1, "Python", 25, "2026-07-22 18:00", "2026-07-22 18:25", "2026-07-22"),
    (1, "Calculus 2", 40, "2026-07-21 20:00", "2026-07-21 20:40", "2026-07-21"),
    (1, "Python", 20, "2026-07-23 19:00", "2026-07-23 19:20", "2026-07-23"),
]

for user_id, course_name, duration, started_at, ended_at, session_date in study_sessions:
    course_id = get_course_id(course_name)
    cursor.execute("""
    INSERT INTO study_sessions
    (user_id, course_id, duration_minutes, started_at, ended_at, session_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, course_id, duration, started_at, ended_at, session_date))


focus_sessions = [
    (1, 25, 88, 120, "2026-07-22 18:00", "2026-07-22 18:25", "2026-07-22"),
    (1, 40, 76, 360, "2026-07-21 20:00", "2026-07-21 20:40", "2026-07-21"),
    (1, 20, 91, 60, "2026-07-23 19:00", "2026-07-23 19:20", "2026-07-23"),
]

cursor.executemany("""
INSERT INTO focus_sessions
(user_id, duration_minutes, focus_score, distracted_seconds, started_at, ended_at, session_date)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", focus_sessions)


prerequisites = [
    ("Calculus 2", "კალკულუსი (I)"),
    ("Operating Systems", "კომპიუტერის არქიტექტურა"),
    ("Theoretical Foundations Of CS", "კალკულუსი (I)"),
    ("Theoretical Foundations Of CS", "პროგრამირების საწყისები (python)"),

    ("კალკულუსი (II)", "კალკულუსი (I)"),
    ("ალბათობის თეორია და მათემატიკური სტატისტიკა", "კალკულუსი (II)"),
    ("ინოვაციების მენეჯმენტი და სტარტაპი", "შესავალი მეწარმეობაში"),

    ("კომპიუტერული მეცნიერების თეორიული საფუძვლები", "კალკულუსი (I)"),
    ("კომპიუტერული მეცნიერების თეორიული საფუძვლები", "პროგრამირების საწყისები (python)"),

    ("ოპერაციული სისტემა", "კომპიუტერის არქიტექტურა"),

    ("მონაცემთა სტრუქტურები და ალგორითმები (I)", "კალკულუსი (I)"),
    ("მონაცემთა სტრუქტურები და ალგორითმები (I)", "პროგრამირების საწყისები (python)"),

    ("ხელოვნური ინტელექტის საწყისები", "კალკულუსი (I)"),
    ("ხელოვნური ინტელექტის საწყისები", "პროგრამირება (python)"),

    ("მონაცემთა სტრუქტურები და ალგორითმები (II)", "მონაცემთა სტრუქტურები და ალგორითმები (I)"),

    ("პროგრამული ინჟინერია", "პროგრამირების საწყისები (python)"),
    ("პროგრამული ინჟინერია", "მონაცემთა სტრუქტურები და ალგორითმები (I)"),
    ("პროგრამული ინჟინერია", "ინგლისური ენის პრაქტიკული კურსი (B2)"),

    ("ხელოვნური ინტელექტი და მანქანური სწავლება", "ალბათობის თეორია და მათემატიკური სტატისტიკა"),
    ("ხელოვნური ინტელექტი და მანქანური სწავლება", "ხელოვნური ინტელექტის საწყისები"),

    ("მონაცემთა ბაზების ადმინისტრირება", "მონაცემთა ბაზების საწყისები"),

    ("პროგრამირების პარადიგმები", "კომპიუტერული მეცნიერების თეორიული საფუძვლები"),

    ("რიცხვითი მეთოდები", "კომპიუტერული მეცნიერების თეორიული საფუძვლები"),
    ("რიცხვითი მეთოდები", "კალკულუსი (II)"),

    ("მანქანური სწავლება (ღრმა დასწავლა)", "ხელოვნური ინტელექტი და მანქანური სწავლება"),

    ("მონაცემთა მეცნიერება", "წრფივი ალგებრა (გაღრმავებული კურსი)"),
    ("მონაცემთა მეცნიერება", "ალბათობის თეორია და მათემატიკური სტატისტიკა"),
    ("მონაცემთა მეცნიერება", "პროგრამირების საწყისები (python)"),

    ("ბუნებრივი ენის დამუშავება (NLP)", "მონაცემთა სტრუქტურები და ალგორითმები (I)"),
    ("ბუნებრივი ენის დამუშავება (NLP)", "კალკულუსი (II)"),
    ("ბუნებრივი ენის დამუშავება (NLP)", "წრფივი ალგებრა (გაღრმავებული კურსი)"),
    ("ბუნებრივი ენის დამუშავება (NLP)", "ხელოვნური ინტელექტის საწყისები"),
    ("ბუნებრივი ენის დამუშავება (NLP)", "მანქანური სწავლება (ღრმა დასწავლა)"),

    ("კომპიუტერული ხედვა", "კალკულუსი (II)"),
    ("კომპიუტერული ხედვა", "წრფივი ალგებრა (გაღრმავებული კურსი)"),
    ("კომპიუტერული ხედვა", "პროგრამირება (python)"),
    ("კომპიუტერული ხედვა", "მანქანური სწავლება (ღრმა დასწავლა)"),

    ("Big Data ანალიტიკა", "დისკრეტული მათემატიკა"),

    ("მონაცემთა უსაფრთხოება", "კომპიუტერული ქსელების საწყისები"),
    ("ინფორმაციული უსაფრთხოება", "კომპიუტერული ქსელების საწყისები"),
    ("კიბერუსაფრთხოება", "ოპერაციული სისტემა"),
    ("კიბერუსაფრთხოება", "ინფორმაციული უსაფრთხოება"),

    ("კრიპტოგრაფიის საფუძვლები", "წრფივი ალგებრა (გაღრმავებული კურსი)"),
    ("კრიპტოგრაფიის საფუძვლები", "ალბათობის თეორია და მათემატიკური სტატისტიკა"),
    ("კრიპტოგრაფიის საფუძვლები", "პროგრამირების საწყისები (python)"),
]

for course_name, required_name in prerequisites:
    course_id = get_course_id(course_name)
    required_id = get_course_id(required_name)

    if course_id is not None and required_id is not None:
        cursor.execute("""
        INSERT INTO prerequisites (course_id, required_course_id)
        VALUES (?, ?)
        """, (course_id, required_id))


interests = [
    ("Math",),
    ("Programming",),
    ("Databases",),
    ("AI",),
    ("Data Science",),
    ("Cybersecurity",),
    ("Networking",),
    ("Software Engineering",),
    ("Web Development",),
    ("Mobile Development",),
    ("Testing",),
    ("Hardware / Robotics",),
    ("Business / Startup",),
    ("Writing / Communication",),
    ("Research",),
    ("General",)
]

cursor.executemany("""
INSERT INTO interests (interest_name)
VALUES (?)
""", interests)


def get_interest_id(interest_name):
    cursor.execute(
        "SELECT id FROM interests WHERE interest_name = ?",
        (interest_name,)
    )
    row = cursor.fetchone()
    if row is None:
        print(f"Missing interest: {interest_name}")
        return None
    return row[0]


course_tags = {
    "Python": ["Programming", "Software Engineering", "AI", "Data Science", "Cybersecurity"],
    "Calculus 2": ["Math", "AI", "Data Science"],
    "Intro to Networking": ["Networking", "Cybersecurity"],
    "Operating Systems": ["Programming", "Cybersecurity"],
    "National Language": ["Writing / Communication"],
    "Theoretical Foundations Of CS": ["Math", "Programming"],

    "კალკულუსი (I)": ["Math"],
    "კალკულუსი (II)": ["Math"],
    "ალბათობის თეორია და მათემატიკური სტატისტიკა": ["Math", "Data Science", "AI"],
    "დისკრეტული მათემატიკა": ["Math", "Programming"],
    "წრფივი ალგებრა (გაღრმავებული კურსი)": ["Math", "AI", "Data Science"],

    "პროგრამირების საწყისები (python)": ["Programming", "Software Engineering", "AI", "Data Science", "Cybersecurity"],
    "პროგრამირება (python)": ["Programming", "Software Engineering", "AI", "Data Science"],
    "მონაცემთა სტრუქტურები და ალგორითმები (I)": ["Programming", "Software Engineering"],
    "მონაცემთა სტრუქტურები და ალგორითმები (II)": ["Programming", "Software Engineering"],
    "პროგრამირების პარადიგმები": ["Programming", "Software Engineering"],

    "მონაცემთა ბაზების საწყისები": ["Databases", "Software Engineering"],
    "მონაცემთა ბაზების ადმინისტრირება": ["Databases", "Software Engineering"],

    "კომპიუტერული ქსელების საწყისები": ["Networking", "Cybersecurity"],
    "მონაცემთა უსაფრთხოება": ["Cybersecurity", "Networking"],
    "ინფორმაციული უსაფრთხოება": ["Cybersecurity"],
    "კიბერუსაფრთხოება": ["Cybersecurity"],
    "კრიპტოგრაფიის საფუძვლები": ["Cybersecurity", "Math"],

    "ხელოვნური ინტელექტის საწყისები": ["AI", "Data Science"],
    "ხელოვნური ინტელექტი და მანქანური სწავლება": ["AI", "Data Science"],
    "მანქანური სწავლება (ღრმა დასწავლა)": ["AI", "Data Science"],
    "ბუნებრივი ენის დამუშავება (NLP)": ["AI", "Data Science"],
    "კომპიუტერული ხედვა": ["AI", "Data Science"],
    "მონაცემთა მეცნიერება": ["Data Science", "AI"],
    "Big Data ანალიტიკა": ["Data Science"],

    "ვებ პროგრამირება (Back End Development)": ["Web Development", "Software Engineering"],
    "ვებ პროგრამირება (Front End Development)": ["Web Development", "Software Engineering"],
    "ვებპროგრამირება Flask-ის ბაზაზე": ["Web Development", "Programming"],
    "ვებ პროგრამირება React პლატფორმაზე": ["Web Development"],

    "მობილური აპლიკაციები": ["Mobile Development", "Software Engineering"],
    "მობილური აპლიკაციების დეველოპმენტი (Android)": ["Mobile Development", "Programming"],

    "პროგრამული ინჟინერია": ["Software Engineering"],
    "პროგრამული უზრუნველყოფის ტესტირების საფუძვლები": ["Testing", "Software Engineering"],
    "პროგრამული უზრუნველყოფის ავტომატიზირებული ტესტირება": ["Testing", "Software Engineering"],
    "აპლიკაციის პროგრამული ინტერფეისის ტესტირება": ["Testing", "Software Engineering"],

    "კომპიუტერის არქიტექტურა": ["Hardware / Robotics", "Programming"],
    "ოპერაციული სისტემა": ["Programming", "Cybersecurity"],
    "შესავალი ელექტრონიკასა და რობოტიქსში": ["Hardware / Robotics"],
    "ელექტრომაგნეტიზმის საფუძვლები": ["Hardware / Robotics", "Math"],

    "შესავალი მეწარმეობაში": ["Business / Startup"],
    "ინოვაციების მენეჯმენტი და სტარტაპი": ["Business / Startup"],

    "წერის ტექნიკა": ["Writing / Communication"],
    "აკადემიური წერა": ["Writing / Communication"],
    "სახელმწიფო ენის სპეციალური კურსი": ["Writing / Communication"],
    "ინგლისური ენის პრაქტიკული კურსი (B1)": ["Writing / Communication"],
    "ინგლისური ენის პრაქტიკული კურსი (B2)": ["Writing / Communication"],
}

for course_name, tags in course_tags.items():
    course_id = get_course_id(course_name)

    if course_id is not None:
        for tag in tags:
            interest_id = get_interest_id(tag)

            if interest_id is not None:
                cursor.execute("""
                INSERT INTO course_interests (course_id, interest_id)
                VALUES (?, ?)
                """, (course_id, interest_id))



cursor.execute("""
INSERT INTO user_interests (user_id, interest_id)
VALUES (?, ?)
""", (1, get_interest_id("Cybersecurity")))


conn.commit()

print("\nDatabase created successfully.")

cursor.execute("SELECT COUNT(*) FROM users")
print("Users:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM courses")
print("All courses in Course Map:", cursor.fetchone()[0])

cursor.execute("""
SELECT courses.course_name
FROM enrollments
JOIN courses ON enrollments.course_id = courses.id
WHERE enrollments.user_id = 1
""")
print("\nUser 1 current courses:")
for row in cursor.fetchall():
    print("-", row[0])

cursor.execute("SELECT COUNT(*) FROM prerequisites")
print("\nPrerequisites:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM interests")
print("Interests:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM course_interests")
print("Course tags:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM items")
print("Items:", cursor.fetchone()[0])

conn.close()