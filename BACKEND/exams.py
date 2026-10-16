'''
from BACKEND.database import Database

class ExamsManager(Database):
    def add_exam(self, course_id, exam_title, exam_date, room):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                insert into exams (course_id, exam_title, exam_date, room)
                values (?, ?, ?, ?)
            """, 
            (course_id, exam_title, exam_date, room))
            conn.commit()

    def get_exams(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                select exams.id, exams.exam_title, courses.course_name,
                exams.exam_date, exams.room
                from exams
                join courses on exams.course_id = courses.id
                order by exams.exam_date
            """)
            return cursor.fetchall()

    def get_upcoming_exams(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                select exams.id, exams.exam_title, courses.course_name,
                exams.exam_date, exams.room
                from exams
                join courses on exams.course_id = courses.id
                where date(exams.exam_date) >= date('now')
                order by date(exams.exam_date)
            """)
            return cursor.fetchall()

    def delete_exam(self, exam_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                delete from exams
                where id = ?
            """, (exam_id,))
            conn.commit()
            '''