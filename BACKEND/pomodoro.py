from datetime import datetime, timedelta
from BACKEND.sessions import SessionsManager



class PomodoroTimer:
    def __init__(self, study_minutes=25, break_minutes=5):
        self.study_minutes = study_minutes
        self.break_minutes = break_minutes

        self.remaining_seconds = study_minutes * 60
        self.is_running = False
        self.is_paused = False
        self.mode = "study"

        self.user_id = None
        self.course_id = None

        self.study_started_at = None
        self.last_saved_session_id = None

        self.sessions_manager = SessionsManager()

    def set_durations(self, study_minutes, break_minutes):
        if study_minutes <= 0:
            raise ValueError("Study minutes must be greater than 0.")

        if break_minutes <= 0:
            raise ValueError("Break minutes must be greater than 0.")

        self.study_minutes = int(study_minutes)
        self.break_minutes = int(break_minutes)

        self.reset()

    def start(self, user_id, course_id=None):
        if user_id is None:
            raise ValueError("User ID is required to start Pomodoro.")

        self.user_id = user_id
        self.course_id = course_id

        self.is_running = True
        self.is_paused = False

        if self.mode == "study" and self.study_started_at is None:
            self.study_started_at = datetime.now()

    def pause(self):
        if self.is_running:
            self.is_paused = True

    def resume(self):
        if self.is_running:
            self.is_paused = False

    def stop(self):
        self.is_running = False
        self.is_paused = False
        self.study_started_at = None

    def reset(self):
        self.remaining_seconds = self.study_minutes * 60
        self.is_running = False
        self.is_paused = False
        self.mode = "study"
        self.study_started_at = None
        self.last_saved_session_id = None

    def get_time_left(self):
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def get_mode_label(self):
        if self.mode == "study":
            return "Focus Time"
        return "Break Time"

    def tick(self):
        if not self.is_running or self.is_paused:
            return {
                "status": "idle",
                "mode": self.mode,
                "time_left": self.get_time_left()
            }

        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1

        if self.remaining_seconds > 0:
            return {
                "status": "ticking",
                "mode": self.mode,
                "time_left": self.get_time_left()
            }

        if self.mode == "study":
            saved_session_id = self._save_completed_study_session()

            self.mode = "break"
            self.remaining_seconds = self.break_minutes * 60
            self.study_started_at = None

            return {
                "status": "study_completed",
                "mode": self.mode,
                "time_left": self.get_time_left(),
                "saved_session_id": saved_session_id
            }

        self.mode = "study"
        self.remaining_seconds = self.study_minutes * 60
        self.study_started_at = datetime.now()

        return {
            "status": "break_completed",
            "mode": self.mode,
            "time_left": self.get_time_left()
        }

    def _save_completed_study_session(self):
        if self.user_id is None:
            return None

        ended_at = datetime.now()

        if self.study_started_at is None:
            started_at = ended_at - timedelta(minutes=self.study_minutes)
        else:
            started_at = self.study_started_at

        session_id = self.sessions_manager.add_study_session(
            user_id=self.user_id,
            course_id=self.course_id,
            duration_minutes=self.study_minutes,
            started_at=started_at.strftime("%Y-%m-%d %H:%M:%S"),
            ended_at=ended_at.strftime("%Y-%m-%d %H:%M:%S"),
            session_date=ended_at.strftime("%Y-%m-%d")
        )

        self.last_saved_session_id = session_id
        return session_id