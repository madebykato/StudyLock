from BACKEND.courses import CoursesManager
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QLineEdit, QTableWidget,
    QTableWidgetItem, QMessageBox
)

class CoursesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = CoursesManager()
        self.title_label = QLabel("Courses")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #E75480;
                font-size: 24px;
                font-weight: bold;
                font-family: Georgia;
            }
        """)

        self.course_name_input = QLineEdit()
        self.course_name_input.setPlaceholderText("Course name")
        self.Lecturer_input = QLineEdit()
        self.Lecturer_input.setPlaceholderText("Lecturer")
        self.add_button = QPushButton("Add Course")
        self.refresh_button = QPushButton("Refresh")

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Course Name", "Lecturer"])

        self.setup_layout()
        self.connect_buttons()
        self.load_courses()

    def setup_layout(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label)
        form_layout = QHBoxLayout()
        form_layout.addWidget(self.course_name_input)
        form_layout.addWidget(self.Lecturer_input)
        form_layout.addWidget(self.add_button)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.refresh_button)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    def connect_buttons(self):
        self.add_button.clicked.connect(self.add_course)
        self.refresh_button.clicked.connect(self.load_courses)

    def add_course(self):
        course_name = self.course_name_input.text().strip()
        Lecturer = self.Lecturer_input.text().strip()

        if course_name == "":
            QMessageBox.warning(self, "Error!!!", "Course name cant be empty.")
            return

        self.manager.add_course(course_name, Lecturer)
        self.course_name_input.clear()
        self.Lecturer_input.clear()

        self.load_courses()

    def load_courses(self):
        courses = self.manager.get_courses()
        self.table.setRowCount(len(courses))
        for row_index, course in enumerate(courses):
            course_id, course_name, Lecturer = course

            self.table.setItem(row_index, 0, QTableWidgetItem(str(course_id)))
            self.table.setItem(row_index, 1, QTableWidgetItem(course_name))
            self.table.setItem(row_index, 2, QTableWidgetItem(Lecturer))