from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QComboBox, QStackedWidget, QTextEdit, QTableWidget,
    QTableWidgetItem, QListView, QHeaderView
)

from BACKEND.courses import CoursesManager


class CourseMapPage(QWidget):
    def __init__(self, user_id=1):
        super().__init__()

        self.user_id = user_id
        self.manager = CoursesManager()

        self.title = QLabel("Course Map")
        self.subtitle = QLabel("Control your subjects using prerequisites\nor\nplan your courses interests")

        self.prereq_button = QPushButton("Prerequisite Map")
        self.interest_button = QPushButton("Interest Guide")

        self.stack = QStackedWidget()

        self.course_box = QComboBox()
        self.course_details = QTextEdit()

        self.interest_box = QComboBox()
        self.interest_table = QTableWidget()

        self.setup_ui()
        self.load_courses()
        self.load_interests()
        self.connect_buttons()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(35, 30, 35, 35)
        main_layout.setSpacing(18)

        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                color: #E75480;
                font-size: 48px;
                font-weight: bold;
                font-family: Georgia;
            }
        """)

        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setStyleSheet("""
            QLabel {
                color: #3D3C3C;
                font-size: 18px;
                font-family: Segoe UI;
            }
        """)

        option_layout = QHBoxLayout()
        option_layout.setSpacing(20)
        option_layout.addStretch()

        for button in [self.prereq_button, self.interest_button]:
            button.setFixedSize(260, 60)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(self.big_button_style())
            option_layout.addWidget(button)

        option_layout.addStretch()

        self.stack.addWidget(self.create_prerequisite_page())
        self.stack.addWidget(self.create_interest_page())

        main_layout.addWidget(self.title)
        main_layout.addWidget(self.subtitle)
        main_layout.addLayout(option_layout)
        main_layout.addWidget(self.stack, 1)

        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: white; }")

    #prerequisites 

    def create_prerequisite_page(self):
        page = QWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        card = QFrame()
        card.setStyleSheet(self.card_style())

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(18)

        self.course_box.setView(QListView())
        self.course_box.setFixedHeight(50)
        self.course_box.setCursor(Qt.CursorShape.PointingHandCursor)
        self.course_box.setStyleSheet(self.combo_style())

        self.course_details.setReadOnly(True)
        self.course_details.setMinimumHeight(500)
        self.course_details.setStyleSheet(self.whiteboard_style())
        self.course_details.setText(
            "Select a course to see its prerequisites and what it unlocks."
        )

        card_layout.addWidget(self.course_box)
        card_layout.addWidget(self.course_details, 1)

        card.setLayout(card_layout)
        layout.addWidget(card)

        page.setLayout(layout)
        return page

    #interesebi

    def create_interest_page(self):
        page = QWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        card = QFrame()
        card.setStyleSheet(self.card_style())

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(18)

        self.interest_box.setView(QListView())
        self.interest_box.setFixedHeight(50)
        self.interest_box.setCursor(Qt.CursorShape.PointingHandCursor)
        self.interest_box.setStyleSheet(self.combo_style())

        self.interest_table.setColumnCount(4)
        self.interest_table.setHorizontalHeaderLabels([
            "Recommended Course", "Component", "Semester", "Credits"
        ])

        self.interest_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.interest_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.interest_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.interest_table.verticalHeader().setVisible(False)
        self.interest_table.setMinimumHeight(520)
        self.interest_table.setStyleSheet(self.table_style())

        card_layout.addWidget(self.interest_box)
        card_layout.addWidget(self.interest_table, 1)

        card.setLayout(card_layout)
        layout.addWidget(card)

        page.setLayout(layout)
        return page

    # load

    def load_courses(self):
        self.course_box.clear()
        self.course_box.addItem("Select a course", None)

        courses = self.manager.get_all_courses()

        for course in courses:
            semester = course["semester"] or "?"
            label = f"{course['course_name']}  •  Semester {semester}"
            self.course_box.addItem(label, course["id"])

    def load_interests(self):
        self.interest_box.clear()
        self.interest_box.addItem("Select an interest", None)

        interests = self.manager.get_interests()

        for interest in interests:
            self.interest_box.addItem(
                interest["interest_name"],
                interest["interest_name"]
            )

    def connect_buttons(self):
        self.prereq_button.clicked.connect(self.show_prerequisite_page)
        self.interest_button.clicked.connect(self.show_interest_page)

        self.course_box.currentIndexChanged.connect(self.show_selected_course)
        self.interest_box.currentIndexChanged.connect(self.show_interest_courses)


    def show_prerequisite_page(self):
        self.stack.setCurrentIndex(0)
        self.prereq_button.setText("✓ Prerequisite Map")
        self.interest_button.setText("Interest Guide")

    def show_interest_page(self):
        self.stack.setCurrentIndex(1)
        self.prereq_button.setText("Prerequisite Map")
        self.interest_button.setText("✓ Interest Guide")

    # prerekvizitebis logika
    def show_selected_course(self):
        course_id = self.course_box.currentData()

        if course_id is None:
            self.course_details.setText(
                "Select a course to see its prerequisites and what it unlocks"
            )
            return

        course = self.manager.get_course_by_id(course_id)
        prerequisites = self.manager.get_course_prerequisites(course_id)
        unlocked_courses = self.manager.get_courses_unlocked_by(course_id)

        if course is None:
            self.course_details.setText("Course not found.")
            return

        text = ""
        text += f"{course['course_name']}\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        text += f"Component: {course['component'] or '—'}\n"
        text += f"Semester: {course['semester'] or '—'}\n"
        text += f"Credits: {course['credits'] or '—'}\n"
        text += f"Instructor: {course['instructor'] or '—'}\n\n"

        text += "Prerequisites\n"
        text += "─────────────\n"

        if prerequisites:
            for prereq in prerequisites:
                semester = prereq["semester"] or "—"
                text += f"• {prereq['course_name']}  /  Semester {semester}\n"
        else:
            text += "• No prerequisites\n"

        text += "\nCourses unlocked after this\n"
        text += "───────────────────────────\n"

        if unlocked_courses:
            for unlocked in unlocked_courses:
                semester = unlocked["semester"] or "—"
                text += f"• {unlocked['course_name']}  /  Semester {semester}\n"
        else:
            text += "• No direct future courses listed\n"

        self.course_details.setText(text)

    # interesis logika 

    def show_interest_courses(self):
        interest_name = self.interest_box.currentData()

        self.interest_table.setRowCount(0)

        if interest_name is None:
            return

        courses = self.manager.get_courses_by_interest(interest_name)

        for row_index, course in enumerate(courses):
            self.interest_table.insertRow(row_index)

            values = [
                course["course_name"],
                course["component"] or "—",
                course["semester"] or "—",
                course["credits"] or "—"
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.interest_table.setItem(row_index, column, item)

    # design

    def card_style(self):
        return """
            QFrame {
                background-color: #FFF9FB;
                border: 1px solid #FADADD;
                border-radius: 24px;
            }
        """

    def big_button_style(self):
        return """
            QPushButton {
                background-color: #FFB5C3;
                color: #3D3C3C;
                border: none;
                border-radius: 18px;
                font-size: 17px;
                font-weight: 700;
                font-family: Segoe UI;
            }

            QPushButton:hover {
                background-color: #F4A7B9;
                color: white;
            }

            QPushButton:pressed {
                background-color: #E88AAD;
            }
        """

    def combo_style(self):
        return """
            QComboBox {
                background-color: white;
                color: #3D3C3C;
                border: 1px solid #FADADD;
                border-radius: 16px;
                padding-left: 16px;
                padding-right: 16px;
                font-size: 16px;
                font-family: Segoe UI;
            }

            QComboBox:focus {
                border: 2px solid #FFB5C3;
            }

            QComboBox::drop-down {
                border: none;
                width: 35px;
            }

            QComboBox::down-arrow {
                image: none;
                border: none;
            }

            QComboBox QAbstractItemView {
                background-color: white;
                color: #3D3C3C;
                border: 1px solid #FADADD;
                selection-background-color: #FFB5C3;
                selection-color: #3D3C3C;
                outline: 0px;
                font-size: 15px;
                font-family: Segoe UI;
            }

            QComboBox QAbstractItemView::item {
                min-height: 36px;
                padding: 8px;
                color: #3D3C3C;
                background-color: white;
            }

            QComboBox QAbstractItemView::item:selected {
                background-color: #FFB5C3;
                color: #3D3C3C;
            }
        """

    def whiteboard_style(self):
        return """
            QTextEdit {
                background-color: white;
                color: #3D3C3C;
                border: 1px solid #FADADD;
                border-radius: 22px;
                padding: 24px;
                font-size: 17px;
                font-family: Segoe UI;
                line-height: 1.4;
            }
        """

    def table_style(self):
        return """
            QTableWidget {
                background-color: white;
                color: #3D3C3C;
                border: 1px solid #FADADD;
                border-radius: 22px;
                gridline-color: #FADADD;
                font-size: 15px;
                font-family: Segoe UI;
                selection-background-color: #FFE3EC;
                selection-color: #3D3C3C;
            }

            QHeaderView::section {
                background-color: #FFB5C3;
                color: #3D3C3C;
                border: none;
                padding: 9px;
                font-weight: bold;
                font-family: Segoe UI;
            }
        """