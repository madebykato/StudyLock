from BACKEND.database import Database

class SessionsManager(Database):
    def add_study_session(
        self,
        user_id,
        course_id,
        duration_minutes,
        started_at,
        ended_at,
        session_date
    ):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO study_sessions
                (user_id, course_id, duration_minutes, started_at, ended_at, session_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                course_id,
                duration_minutes,
                started_at,
                ended_at,
                session_date
            ))
            conn.commit()
            return cursor.lastrowid

    def add_focus_session(
        self,
        user_id,
        duration_minutes,
        focus_score,
        distracted_seconds,
        started_at,
        ended_at,
        session_date
    ):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO focus_sessions
                (user_id, duration_minutes, focus_score, distracted_seconds, started_at, ended_at, session_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                duration_minutes,
                focus_score,
                distracted_seconds,
                started_at,
                ended_at,
                session_date
            ))
            conn.commit()
            return cursor.lastrowid

    def get_study_sessions(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT study_sessions.id, courses.course_name,
                       study_sessions.duration_minutes,
                       study_sessions.started_at,
                       study_sessions.ended_at,
                       study_sessions.session_date
                FROM study_sessions
                LEFT JOIN courses ON study_sessions.course_id = courses.id
                WHERE study_sessions.user_id = ?
                ORDER BY study_sessions.started_at DESC
            """, (user_id,))
            return cursor.fetchall()

    def get_focus_sessions(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, duration_minutes, focus_score,
                       distracted_seconds, started_at, ended_at, session_date
                FROM focus_sessions
                WHERE user_id = ?
                ORDER BY started_at DESC
            """, (user_id,))
            return cursor.fetchall()