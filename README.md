# StudyLock

StudyLock is a student productivity application built with Python. It helps students manage courses, track exams, monitor study habits, and stay focused.

## Features

- Course management and course mapping
- Exam tracking and study analytics
- Focus and Pomodoro tools
- User authentication
- Local SQLite database
- Face landmark functionality using MediaPipe and OpenCV

## Requirements

- Python
- Dependencies listed in `requirements.txt`

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create the local database:

   ```bash
   python seed_database.py
   ```

3. Run the application:

   ```bash
   python main.py
   ```

## Notes

The SQLite database is generated locally and is not included in this repository. The `testing/` folder is also excluded.