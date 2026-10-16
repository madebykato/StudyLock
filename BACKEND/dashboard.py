from BACKEND.database import Database

class DashboardManager(Database):
    def total_items(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM items
                WHERE user_id = ?
            """, (user_id,))
            return cursor.fetchone()[0]

    def completed_items(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM items
                WHERE user_id = ?
                AND completed = 1
            """, (user_id,))
            return cursor.fetchone()[0]

    def current_items(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM items
                WHERE user_id = ?
                AND completed = 0
            """, (user_id,))
            return cursor.fetchone()[0]

    def completion_rate(self, user_id):
        total = self.total_items(user_id)

        if total == 0:
            return 0

        completed = self.completed_items(user_id)
        return round((completed / total) * 100, 1)

    def next_deadline(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    items.title,
                    items.item_type,
                    courses.course_name,
                    items.deadline,
                    items.room
                FROM items
                LEFT JOIN courses ON items.course_id = courses.id
                WHERE items.user_id = ?
                AND items.completed = 0
                AND items.deadline IS NOT NULL
                AND date(items.deadline) >= date('now')
                ORDER BY date(items.deadline) ASC
                LIMIT 1
            """, (user_id,))

            row = cursor.fetchone()

            if row is None:
                return "No upcoming deadlines"

            title = row["title"]
            item_type = row["item_type"]
            course = row["course_name"] or "No course"
            deadline = row["deadline"]
            room = row["room"]

            if room:
                return f"{course}, {deadline}, Room {room}"

            return f"{course}, {deadline}"

    def days_until_next_deadline(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    CAST(julianday(deadline) - julianday(date('now')) AS INTEGER)
                FROM items
                WHERE user_id = ?
                AND completed = 0
                AND deadline IS NOT NULL
                AND date(deadline) >= date('now')
                ORDER BY date(deadline) ASC
                LIMIT 1
            """, (user_id,))

            row = cursor.fetchone()

            if row is None or row[0] is None:
                return None

            return row[0]

    def next_deadline_countdown(self, user_id):
        days_left = self.days_until_next_deadline(user_id)

        if days_left is None:
            return "No deadline"

        if days_left > 1:
            return f"{days_left} days left"

        if days_left == 1:
            return "1 day left"

        if days_left == 0:
            return "Due today"

        if days_left == -1:
            return "Overdue by 1 day"

        return f"Overdue by {abs(days_left)} days"

    def upcoming_exams_count(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM items
                WHERE user_id = ?
                AND item_type = 'Exam'
                AND completed = 0
                AND deadline IS NOT NULL
                AND date(deadline) >= date('now')
            """, (user_id,))
            return cursor.fetchone()[0]

    def total_study_minutes(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(duration_minutes)
                FROM study_sessions
                WHERE user_id = ?
            """, (user_id,))

            total = cursor.fetchone()[0]

            if total is None:
                return 0

            return total

    def weekly_study_minutes(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(duration_minutes)
                FROM study_sessions
                WHERE user_id = ?
                AND date(started_at) >= date('now', '-7 days')
            """, (user_id,))

            total = cursor.fetchone()[0]

            if total is None:
                return 0

            return total

    def average_focus_score(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AVG(focus_score)
                FROM focus_sessions
                WHERE user_id = ?
                AND focus_score IS NOT NULL
            """, (user_id,))

            average = cursor.fetchone()[0]

            if average is None:
                return 0

            return round(average, 1)

    def dashboard_summary(self, user_id):
        return {
            "total_items": self.total_items(user_id),
            "completed_items": self.completed_items(user_id),
            "current_items": self.current_items(user_id),
            "completion_rate": self.completion_rate(user_id),
            "next_deadline": self.next_deadline(user_id),
            "next_deadline_countdown": self.next_deadline_countdown(user_id),
            "upcoming_exams": self.upcoming_exams_count(user_id),
            "total_study_minutes": self.total_study_minutes(user_id),
            "weekly_study_minutes": self.weekly_study_minutes(user_id),
            "average_focus": self.average_focus_score(user_id)
        }