class User:
    def __init__(self, full_name, email, user_id=None):
        self.id = user_id
        self.full_name = full_name
        self.email = email

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Course:
    def __init__(
        self,
        course_name,
        component=None,
        semester=None,
        credits=None,
        instructor=None,
        course_id=None
    ):
        self.id = course_id
        self.course_name = course_name
        self.component = component
        self.semester = semester
        self.credits = credits
        self.instructor = instructor

    def __str__(self):
        if self.instructor:
            return f"{self.course_name} - {self.instructor}"
        return self.course_name


class Item:
    def __init__(
        self,
        title,
        user_id,
        item_type,
        course_id=None,
        deadline=None,
        room=None,
        completed=False,
        created_at=None,
        completed_at=None,
        item_id=None
    ):
        self.id = item_id
        self.user_id = user_id
        self.course_id = course_id
        self.title = title
        self.item_type = item_type
        self.deadline = deadline
        self.room = room
        self.completed = completed
        self.created_at = created_at
        self.completed_at = completed_at

    def mark_completed(self):
        self.completed = True

    def mark_incomplete(self):
        self.completed = False

    def is_exam(self):
        return self.item_type.lower() == "exam"

    def is_overdue(self, today):
        if not self.deadline or self.completed:
            return False
        return self.deadline < today

    def __str__(self):
        status = "Done" if self.completed else "Not done"
        return f"{self.title} ({self.item_type}) - {status}"


class StudySession:
    def __init__(
        self,
        user_id,
        duration_minutes,
        course_id=None,
        started_at=None,
        ended_at=None,
        session_date=None,
        session_id=None
    ):
        self.id = session_id
        self.user_id = user_id
        self.course_id = course_id
        self.duration_minutes = duration_minutes
        self.started_at = started_at
        self.ended_at = ended_at
        self.session_date = session_date

    def study_hours(self):
        return self.duration_minutes / 60

    def __str__(self):
        return f"{self.duration_minutes} min study session"


class FocusSession:
    def __init__(
        self,
        user_id,
        duration_minutes,
        focus_score,
        distracted_seconds=0,
        started_at=None,
        ended_at=None,
        session_date=None,
        session_id=None
    ):
        self.id = session_id
        self.user_id = user_id
        self.duration_minutes = duration_minutes
        self.focus_score = focus_score
        self.distracted_seconds = distracted_seconds
        self.started_at = started_at
        self.ended_at = ended_at
        self.session_date = session_date

    def is_good_focus(self):
        return self.focus_score >= 80

    def distracted_minutes(self):
        return self.distracted_seconds / 60

    def __str__(self):
        return f"{self.duration_minutes} min, focus: {self.focus_score}%"


class Interest:
    def __init__(self, interest_name, interest_id=None):
        self.id = interest_id
        self.interest_name = interest_name

    def __str__(self):
        return self.interest_name