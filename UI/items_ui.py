from PyQt6.QtCore import Qt
from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QMessageBox, QCheckBox, QListView,
    QHeaderView
)

from BACKEND.items import ItemsManager
from BACKEND.courses import CoursesManager


class TasksPage(QWidget):
    def __init__(self, user_id=1):
        super().__init__()

        self.user_id = user_id
        self.items_manager = ItemsManager()
        self.courses_manager = CoursesManager()

        self.title = QLabel("Tasks & Exams")
        self.subtitle = QLabel("All your academic deadlines in one place")

        self.title_input = QLineEdit()
        self.type_box = QComboBox()
        self.course_box = QComboBox()
        self.deadline_input = QLineEdit()
        self.room_input = QLineEdit()

        self.filter_type_box = QComboBox()
        self.filter_course_box = QComboBox()

        self.add_button = QPushButton("Add Item")
        self.delete_button = QPushButton("Delete Selected")
        self.refresh_button = QPushButton("Refresh")

        self.table = QTableWidget()

        self.setup_ui()
        self.load_courses()
        self.connect_buttons()
        self.load_items()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(35, 30, 35, 35)
        main_layout.setSpacing(18)

        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                color: #E75480;
                font-size: 46px;
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

        form_card = QFrame()
        form_card.setStyleSheet(self.card_style())

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setSpacing(14)

        self.title_input.setPlaceholderText("Title")
        self.room_input.setPlaceholderText("Room, optional")

        self.type_box.addItems(["Task", "Exam", "Quiz", "Project", "Homework"])

        self.filter_type_box.addItem("All Types", None)
        self.filter_type_box.addItems(["Task", "Exam", "Quiz", "Project", "Homework"])

        self.deadline_input.setPlaceholderText("Deadline: YYYY-MM-DD")
        self.deadline_input.setText(date.today().strftime("%Y-%m-%d"))

        for combo in [
            self.type_box,
            self.course_box,
            self.filter_type_box,
            self.filter_course_box
        ]:
            combo.setView(QListView())
            combo.setFixedHeight(45)
            combo.setCursor(Qt.CursorShape.PointingHandCursor)
            combo.setStyleSheet(self.combo_style())

        for field in [
            self.title_input,
            self.deadline_input,
            self.room_input
        ]:
            field.setFixedHeight(45)
            field.setStyleSheet(self.input_style())

        self.add_button.setFixedHeight(45)
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.setStyleSheet(self.button_style())

        row1 = QHBoxLayout()
        row1.setSpacing(12)
        row1.addWidget(self.title_input)
        row1.addWidget(self.type_box)
        row1.addWidget(self.course_box)

        row2 = QHBoxLayout()
        row2.setSpacing(12)
        row2.addWidget(self.deadline_input)
        row2.addWidget(self.room_input)
        row2.addWidget(self.add_button)

        form_layout.addLayout(row1)
        form_layout.addLayout(row2)
        form_card.setLayout(form_layout)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)
        filter_layout.addWidget(self.filter_type_box)
        filter_layout.addWidget(self.filter_course_box)
        filter_layout.addWidget(self.refresh_button)

        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Done", "Title", "Type",
            "Course", "Deadline", "Countdown", "Room"
        ])

        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFF9FB;
                color: #3D3C3C;
                border: 1px solid #FADADD;
                border-radius: 18px;
                gridline-color: #FADADD;
                font-size: 14px;
                font-family: Segoe UI;
                selection-background-color: #FFE3EC;
                selection-color: #3D3C3C;
            }

            QHeaderView::section {
                background-color: #FFB5C3;
                color: #3D3C3C;
                border: none;
                padding: 8px;
                font-weight: bold;
                font-family: Segoe UI;
            }
        """)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        for button in [self.delete_button, self.refresh_button]:
            button.setFixedHeight(45)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(self.button_style())

        button_layout.addStretch()
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()

        main_layout.addWidget(self.title)
        main_layout.addWidget(self.subtitle)
        main_layout.addWidget(form_card)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.table)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: white; }")

    def load_courses(self):
        self.course_box.clear()
        self.filter_course_box.clear()

        self.course_box.addItem("No course", None)
        self.filter_course_box.addItem("All Courses", None)

        courses = self.courses_manager.get_user_courses(self.user_id)

        for course in courses:
            self.course_box.addItem(course["course_name"], course["id"])
            self.filter_course_box.addItem(course["course_name"], course["id"])

    def connect_buttons(self):
        self.add_button.clicked.connect(self.add_item)
        self.delete_button.clicked.connect(self.delete_item)
        self.refresh_button.clicked.connect(self.load_items)

        self.filter_type_box.currentIndexChanged.connect(self.load_items)
        self.filter_course_box.currentIndexChanged.connect(self.load_items)

    def add_item(self):
        title = self.title_input.text().strip()
        item_type = self.type_box.currentText()
        course_id = self.course_box.currentData()
        deadline = self.deadline_input.text().strip()
        room = self.room_input.text().strip() or None

        if not title:
            QMessageBox.warning(
                self,
                "Missing title",
                "Please enter a title."
            )
            return

        if not deadline:
            deadline = None

        try:
            if deadline is not None:
                from datetime import date
                date.fromisoformat(deadline)

            self.items_manager.add_item(
                user_id=self.user_id,
                course_id=course_id,
                title=title,
                item_type=item_type,
                deadline=deadline,
                room=room
            )

            self.title_input.clear()
            self.room_input.clear()

            try:
                from datetime import date
                self.deadline_input.setText(date.today().strftime("%Y-%m-%d"))
            except Exception:
                pass

            self.load_items()

            QMessageBox.information(
                self,
                "Item added",
                "Your item was added successfully."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Add Item Error",
                str(error)
            )

    def load_items(self):
        selected_type = self.filter_type_box.currentText()
        selected_course_id = self.filter_course_box.currentData()

        if selected_course_id is not None:
            items = self.items_manager.get_items_by_course(
                self.user_id,
                selected_course_id
            )

            if selected_type != "All Types":
                items = [
                    item for item in items
                    if item["item_type"] == selected_type
                ]

        elif selected_type != "All Types":
            items = self.items_manager.get_items_by_type(
                self.user_id,
                selected_type
            )

        else:
            items = self.items_manager.get_items(self.user_id)

        self.table.setRowCount(0)

        for row_index, item in enumerate(items):
            self.table.insertRow(row_index)

            item_id = item["id"]

            countdown = self.items_manager.get_countdown_text(
                self.user_id,
                item_id
            )

            self.set_table_item(row_index, 0, item_id)
            self.add_done_checkbox(row_index, item_id, item["completed"])

            self.set_table_item(row_index, 2, item["title"])
            self.set_table_item(row_index, 3, item["item_type"])
            self.set_table_item(row_index, 4, item["course_name"] or "No course")
            self.set_table_item(row_index, 5, item["deadline"] or "No deadline")
            self.set_table_item(row_index, 6, countdown)
            self.set_table_item(row_index, 7, item["room"] or "")

    def set_table_item(self, row, column, value):
        table_item = QTableWidgetItem(str(value))
        table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, column, table_item)

    def add_done_checkbox(self, row, item_id, completed):
        checkbox = QCheckBox()
        checkbox.setChecked(bool(completed))
        checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        checkbox.setStyleSheet(self.checkbox_style())

        checkbox.stateChanged.connect(
            lambda state, current_item_id=item_id:
            self.update_completed_status(current_item_id, state)
        )

        wrapper = QWidget()
        wrapper.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(checkbox)

        wrapper.setLayout(layout)
        self.table.setCellWidget(row, 1, wrapper)

    def update_completed_status(self, item_id, state):
        if state == Qt.CheckState.Checked.value:
            self.items_manager.mark_completed(self.user_id, item_id)
        else:
            self.items_manager.mark_incomplete(self.user_id, item_id)

        self.load_items()

    def selected_item_id(self):
        selected_row = self.table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(
                self,
                "No item selected",
                "Please select an item first."
            )
            return None

        item = self.table.item(selected_row, 0)

        if item is None:
            return None

        return int(item.text())

    def delete_item(self):
        item_id = self.selected_item_id()

        if item_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Delete item",
            "Are you sure you want to delete this item?"
        )

        if answer == QMessageBox.StandardButton.Yes:
            self.items_manager.delete_item(self.user_id, item_id)
            self.load_items()

    def card_style(self):
        return """
            QFrame {
                background-color: #FFF9FB;
                border: 1px solid #FADADD;
                border-radius: 22px;
            }
        """

    def input_style(self):
        return """
            QLineEdit, QDateEdit {
                background-color: white;
                color: #3D3C3C;
                border: 1px solid #FADADD;
                border-radius: 14px;
                padding-left: 12px;
                padding-right: 12px;
                font-size: 15px;
                font-family: Segoe UI;
            }

            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #FFB5C3;
            }
        """

    def combo_style(self):
        return """
            QComboBox {
                background-color: white;
                color: #3D3C3C;
                border: 1px solid #FADADD;
                border-radius: 14px;
                padding-left: 12px;
                padding-right: 12px;
                font-size: 15px;
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
                min-height: 34px;
                padding: 8px;
                color: #3D3C3C;
                background-color: white;
            }

            QComboBox QAbstractItemView::item:selected {
                background-color: #FFB5C3;
                color: #3D3C3C;
            }
        """

    def button_style(self):
        return """
            QPushButton {
                background-color: #FFB5C3;
                color: #3D3C3C;
                border: none;
                border-radius: 14px;
                font-size: 15px;
                font-weight: 600;
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

    def checkbox_style(self):
        return """
            QCheckBox {
                background: transparent;
                border: none;
            }

            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 7px;
                border: 2px solid #FFB5C3;
                background-color: white;
            }

            QCheckBox::indicator:hover {
                border: 2px solid #E75480;
                background-color: #FFF1F6;
            }

            QCheckBox::indicator:checked {
                background-color: #FFB5C3;
                border: 2px solid #E75480;
            }
        """