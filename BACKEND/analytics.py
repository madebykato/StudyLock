from BACKEND.database import Database
from datetime import date, datetime, timedelta

class Analytics(Database):
    def __init__(self, user_id, db_name="studylock.db"):
        super().__init__(db_name)
        self.user_id = user_id
        
    def get_study_sessions(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT course_id, duration_minutes, started_at, ended_at, session_date
                FROM study_sessions
                WHERE user_id = ?
                AND ended_at IS NOT NULL
                ORDER BY started_at DESC
            """, (self.user_id,))
            return cursor.fetchall()

    def get_focus_sessions(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT focus_score, duration_minutes, distracted_seconds,
                       started_at, ended_at, session_date
                FROM focus_sessions
                WHERE user_id = ?
                AND ended_at IS NOT NULL
                ORDER BY started_at DESC
            """, (self.user_id,))
            return cursor.fetchall()

    def get_items(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, course_id, title, item_type, deadline,
                       completed, created_at, completed_at
                FROM items
                WHERE user_id = ?
            """, (self.user_id,))
            return cursor.fetchall()

    def get_courses(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT courses.id, courses.course_name
                FROM enrollments
                JOIN courses ON enrollments.course_id = courses.id
                WHERE enrollments.user_id = ?
                ORDER BY courses.course_name
            """, (self.user_id,))
            return cursor.fetchall()

    def get_upcoming_exams(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT course_id, title, deadline
                FROM items
                WHERE user_id = ?
                AND item_type = 'Exam'
                AND completed = 0
                AND date(deadline) BETWEEN date('now') AND date('now', '+14 days')
            """, (self.user_id,))
            return cursor.fetchall()


    def safe_date(self, value):
        if not value:
            return None

        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None

    def safe_datetime(self, value):
        if not value:
            return None

        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    def average_completion_days(self, items):
        completed_items = [
            item for item in items
            if item["completed"] == 1
            and item["created_at"]
            and item["completed_at"]
        ]

        if not completed_items:
            return 0

        total_days = 0
        counted = 0

        for item in completed_items:
            created = self.safe_datetime(item["created_at"])
            completed = self.safe_datetime(item["completed_at"])

            if created is None or completed is None:
                continue

            difference = completed - created
            total_days += max(difference.total_seconds() / 86400, 0)
            counted += 1

        if counted == 0:
            return 0

        return total_days / counted

# efficiency 
    def efficiency_score(self):
        study_sessions = self.get_study_sessions()
        focus_sessions = self.get_focus_sessions()
        items = self.get_items()

        if not study_sessions and not focus_sessions:
            return {
                "score": 0,
                "focus_score": 0,
                "completion_rate": 0,
                "consistency": 0,
                "weekly_hours": 0,
                "average_completion_days": 0,
                "feedback": ["No study sessions logged yet."]
            }

        # focus
        valid_focus_scores = [
            session["focus_score"]
            for session in focus_sessions
            if session["focus_score"] is not None
        ]

        if valid_focus_scores:
            avg_focus = sum(valid_focus_scores) / len(valid_focus_scores)
        else:
            avg_focus = 0

        # completion
        if items:
            done = sum(1 for item in items if item["completed"] == 1)
            completion_rate = done / len(items)
        else:
            completion_rate = 0

        # consistency
        today = date.today()
        days_studied = set()

        for session in study_sessions:
            session_day = self.safe_date(session["started_at"])

            if session_day is not None:
                days_studied.add(session_day)

        consistency_count = 0

        for i in range(7):
            check_day = today - timedelta(days=i)

            if check_day in days_studied:
                consistency_count += 1

        consistency = consistency_count / 7

        # weekly study hrrs
        week_ago = today - timedelta(days=7)
        weekly_minutes = 0

        for session in study_sessions:
            session_day = self.safe_date(session["started_at"])

            if session_day is not None and session_day >= week_ago:
                weekly_minutes += session["duration_minutes"] or 0

        weekly_hours = weekly_minutes / 60
        time_score = min(weekly_hours / 20, 1)

        # average task completion time
        avg_completion_days = self.average_completion_days(items)

        # final 
        score = (
            avg_focus * 0.35
            + completion_rate * 100 * 0.30
            + consistency * 100 * 0.20
            + time_score * 100 * 0.15
        )

        score = round(score)

        feedback = []

        if avg_focus >= 80:
            feedback.append("Really strong focus levels, good job!")
        elif avg_focus >= 60:
            feedback.append("Decent focus, but distractions are creeping in, beware!")
        else:
            feedback.append("Focus is way too low. Try shorter sessions!")

        if consistency >= 0.7:
            feedback.append("Good consistency!")
        elif consistency >= 0.4:
            feedback.append("Try to study more regularly!")
        else:
            feedback.append("Very inconsistent study pattern.")

        if completion_rate >= 0.8:
            feedback.append("Task completion is good!")
        elif completion_rate >= 0.5:
            feedback.append("Some tasks are getting done, but unfinished work is still building up.")
        else:
            feedback.append("Task completion could improve.")

        if weekly_hours < 5:
            feedback.append("You are not logging much study time this week...")

        if avg_completion_days >= 4:
            feedback.append("Tasks take several days to finish, try breaking them into smaller parts")
        elif avg_completion_days > 0:
            feedback.append("Your average task completion time is reasonable.")

        return {
            "score": score,
            "focus_score": round(avg_focus, 1),
            "completion_rate": round(completion_rate * 100, 1),
            "consistency": round(consistency * 100, 1),
            "weekly_hours": round(weekly_hours, 1),
            "average_completion_days": round(avg_completion_days, 1),
            "feedback": feedback
        }

#risk
    def risk_by_course(self):
        courses = self.get_courses()
        items = self.get_items()
        exams = self.get_upcoming_exams()
        study_sessions = self.get_study_sessions()

        exam_course_ids = {
            exam["course_id"]
            for exam in exams
            if exam["course_id"] is not None
        }

        results = []

        for course in courses:
            course_id = course["id"]
            course_name = course["course_name"]

            course_items = [
                item for item in items
                if item["course_id"] == course_id
            ]

            course_sessions = [
                session for session in study_sessions
                if session["course_id"] == course_id
            ]

            risk = 0
            reasons = []

            if course_items:
                unfinished = sum(
                    1 for item in course_items
                    if item["completed"] == 0
                )

                ratio = unfinished / len(course_items)
                risk += ratio * 40

                if unfinished > 0:
                    reasons.append(f"{unfinished} unfinished item(s)")
            else:
                risk += 10
                reasons.append("no tasks or exams added")

            # exam soon
            if course_id in exam_course_ids:
                risk += 30
                reasons.append("exam within 14 days")

            # study time(course)
            total_minutes = sum(
                session["duration_minutes"] or 0
                for session in course_sessions
            )

            if total_minutes == 0:
                risk += 20
                reasons.append("No study time is logged, time to study!")
            elif total_minutes < 60:
                risk += 10
                reasons.append("less than 1 hour studied..")

            if risk >= 60:
                level = "High"
            elif risk >= 35:
                level = "Medium"
            else:
                level = "Low"

            if not reasons:
                reasons.append("You're on track, good job!")

            results.append({
                "course": course_name,
                "risk_level": level,
                "risk_score": round(risk, 1),
                "reasons": reasons
            })

        results.sort(key=lambda result: -result["risk_score"])
        return results

# best study time
    def best_study_time(self):
        focus_sessions = self.get_focus_sessions()

        if not focus_sessions:
            return None

        blocks = {}

        for session in focus_sessions:
            session_time = self.safe_datetime(session["started_at"])

            if session_time is None:
                continue

            focus_score = session["focus_score"]

            if focus_score is None:
                continue

            block_start = (session_time.hour // 2) * 2
            blocks.setdefault(block_start, []).append(focus_score)

        if not blocks:
            return None

        best_block = None
        best_avg = -1

        for block_start, scores in blocks.items():
            avg = sum(scores) / len(scores)

            if avg > best_avg:
                best_avg = avg
                best_block = block_start

        return {
            "start_hour": best_block,
            "end_hour": best_block + 2,
            "average_focus": round(best_avg, 1)
        }

#rec pomodoro 
    def recommended_pomodoro(self):
        focus_sessions = self.get_focus_sessions()

        if not focus_sessions:
            return None

        buckets = {}

        for session in focus_sessions:
            minutes = session["duration_minutes"]
            focus_score = session["focus_score"]

            if minutes is None or focus_score is None:
                continue

            rounded = max(5, round(minutes / 5) * 5)
            buckets.setdefault(rounded, []).append(focus_score)

        if not buckets:
            return None

        reliable = {
            length: scores
            for length, scores in buckets.items()
            if len(scores) >= 2
        }

        if not reliable:
            reliable = buckets

        breakdown = {}

        for length, scores in reliable.items():
            breakdown[length] = round(sum(scores) / len(scores), 1)

        best_length = max(breakdown, key=breakdown.get)

        return {
            "breakdown": breakdown,
            "recommended_minutes": best_length
        }