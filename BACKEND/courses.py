from BACKEND.database import Database

class CoursesManager(Database):
    def get_user_courses(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    courses.id,
                    courses.course_name,
                    courses.component,
                    courses.semester,
                    courses.credits,
                    courses.instructor
                FROM enrollments
                JOIN courses ON enrollments.course_id = courses.id
                WHERE enrollments.user_id = ?
                ORDER BY courses.course_name
            """, (user_id,))
            return cursor.fetchall()

    def get_all_courses(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id,
                    course_name,
                    component,
                    semester,
                    credits,
                    instructor
                FROM courses
                ORDER BY 
                    CASE 
                        WHEN semester IS NULL THEN 99
                        ELSE CAST(semester AS INTEGER)
                    END,
                    course_name
            """)
            return cursor.fetchall()

    def get_course_by_id(self, course_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id,
                    course_name,
                    component,
                    semester,
                    credits,
                    instructor
                FROM courses
                WHERE id = ?
            """, (course_id,))
            return cursor.fetchone()

    def get_semesters(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT semester
                FROM courses
                WHERE semester IS NOT NULL
                ORDER BY CAST(semester AS INTEGER)
            """)
            return cursor.fetchall()

    def get_courses_by_semester(self, semester):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id,
                    course_name,
                    component,
                    semester,
                    credits,
                    instructor
                FROM courses
                WHERE semester = ?
                ORDER BY course_name
            """, (semester,))
            return cursor.fetchall()

    def get_course_prerequisites(self, course_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    required.id,
                    required.course_name,
                    required.component,
                    required.semester,
                    required.credits,
                    required.instructor
                FROM prerequisites
                JOIN courses AS required
                    ON prerequisites.required_course_id = required.id
                WHERE prerequisites.course_id = ?
                ORDER BY 
                    CASE 
                        WHEN required.semester IS NULL THEN 99
                        ELSE CAST(required.semester AS INTEGER)
                    END,
                    required.course_name
            """, (course_id,))
            return cursor.fetchall()

    def get_courses_unlocked_by(self, course_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    unlocked.id,
                    unlocked.course_name,
                    unlocked.component,
                    unlocked.semester,
                    unlocked.credits,
                    unlocked.instructor
                FROM prerequisites
                JOIN courses AS unlocked
                    ON prerequisites.course_id = unlocked.id
                WHERE prerequisites.required_course_id = ?
                ORDER BY 
                    CASE 
                        WHEN unlocked.semester IS NULL THEN 99
                        ELSE CAST(unlocked.semester AS INTEGER)
                    END,
                    unlocked.course_name
            """, (course_id,))
            return cursor.fetchall()

    def get_interests(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id,
                    interest_name
                FROM interests
                ORDER BY interest_name
            """)
            return cursor.fetchall()

    def get_courses_by_interest(self, interest_name):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    courses.id,
                    courses.course_name,
                    courses.component,
                    courses.semester,
                    courses.credits,
                    courses.instructor
                FROM course_interests
                JOIN courses 
                    ON course_interests.course_id = courses.id
                JOIN interests 
                    ON course_interests.interest_id = interests.id
                WHERE interests.interest_name = ?
                ORDER BY 
                    CASE 
                        WHEN courses.semester IS NULL THEN 99
                        ELSE CAST(courses.semester AS INTEGER)
                    END,
                    courses.course_name
            """, (interest_name,))
            return cursor.fetchall()

    def get_interests_for_course(self, course_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    interests.id,
                    interests.interest_name
                FROM course_interests
                JOIN interests
                    ON course_interests.interest_id = interests.id
                WHERE course_interests.course_id = ?
                ORDER BY interests.interest_name
            """, (course_id,))
            return cursor.fetchall()