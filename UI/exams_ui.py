'''
from BACKEND.exams import ExamsManager
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox
)

class ExamsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = ExamsManager()

        self.course_id_input = QLineEdit()
        self.course_id_input.setPlaceholderText("Course ID")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Type")
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("YYYY-MM-DD")
        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("Room")
        self.add_button = QPushButton("Add Exam")
        self.delete_button = QPushButton("Delete Exam")
        self.refresh_button = QPushButton("View All Exams")
        self.upcoming_button = QPushButton("Show Upcoming Exams")

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Type", "Course", "Date", "Room"])

        self.title_label = QLabel("Exams")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #E75480;
                font-size: 20px;
                font-weight: bold;
                font-family: Georgia;
            }
        """)
        self.setup_layout()
        self.connect_buttons()
        self.load_exams()

    def setup_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        form = QHBoxLayout()
        form.addWidget(self.course_id_input)
        form.addWidget(self.title_input)
        form.addWidget(self.date_input)
        form.addWidget(self.room_input)
        form.addWidget(self.add_button)

        buttons = QHBoxLayout()
        buttons.addWidget(self.refresh_button)
        buttons.addWidget(self.upcoming_button)
        buttons.addWidget(self.delete_button)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def connect_buttons(self):
        self.add_button.clicked.connect(self.add_exam)
        self.refresh_button.clicked.connect(self.load_exams)
        self.upcoming_button.clicked.connect(self.load_upcoming_exams)
        self.delete_button.clicked.connect(self.delete_exam)

    def add_exam(self):
        try:
            course_id = int(self.course_id_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error!!!", "Course ID must be a number.")
            return
        title = self.title_input.text().strip()
        date = self.date_input.text().strip()
        room = self.room_input.text().strip()

        if title == "":
            QMessageBox.warning(self, "Error!!!", "Type cant be empty.")
            return
        self.manager.add_exam(course_id, title, date, room)

        self.course_id_input.clear()
        self.title_input.clear()
        self.date_input.clear()
        self.room_input.clear()
        self.load_exams()

    def load_exams(self):
        exams = self.manager.get_exams()
        self.fill_table(exams)

    def load_upcoming_exams(self):
        exams = self.manager.get_upcoming_exams()
        self.fill_table(exams)

    def fill_table(self, exams):
        self.table.setRowCount(len(exams))
        for row, exam in enumerate(exams):
            for col, value in enumerate(exam):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def delete_exam(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error!!!", "Select an exam first.")
            return
        exam_id = int(self.table.item(selected_row, 0).text())
        self.manager.delete_exam(exam_id)
        self.load_exams()
        '''