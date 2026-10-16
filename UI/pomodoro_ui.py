from BACKEND.pomodoro import PomodoroTimer
from BACKEND.courses import CoursesManager
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QComboBox, QSpinBox, QMessageBox, QListView,
    QAbstractSpinBox
)


class PomodoroPage(QWidget):
    def __init__(self, user_id=1):
        super().__init__()

        self.user_id = user_id

        self.timer_backend = PomodoroTimer()
        self.courses_manager = CoursesManager()

        self.qt_timer = QTimer()
        self.qt_timer.timeout.connect(self.update_timer)

        self.title = QLabel("Pomodoro")
        self.mode_label = QLabel("Focus Time")
        self.time_label = QLabel("25:00")
        self.status_label = QLabel("Choose your subject and start studying!")

        self.course_label = QLabel("Subject:")
        self.study_label = QLabel("Study:")
        self.break_label = QLabel("Break:")

        self.course_box = QComboBox()
        self.course_box.setView(QListView())

        self.study_spin = QSpinBox()
        self.break_spin = QSpinBox()

        self.study_minus_button = QPushButton("-")
        self.study_plus_button = QPushButton("+")

        self.break_minus_button = QPushButton("-")
        self.break_plus_button = QPushButton("+")

        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.resume_button = QPushButton("Resume")
        self.reset_button = QPushButton("Reset")

        self.setup_ui()
        self.load_courses()
        self.connect_buttons()
        self.update_timer_display()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 35, 40, 40)
        main_layout.setSpacing(25)

        card = QFrame()
        card.setStyleSheet(self.card_style())

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(45, 45, 45, 45)
        card_layout.setSpacing(18)

        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #E75480;
                font-size: 52px;
                font-weight: bold;
                font-family: Georgia;
            }
        """)

        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #D94F8C;
                font-size: 28px;
                font-weight: bold;
                font-family: Segoe UI;
            }
        """)

        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #3D3C3C;
                font-size: 86px;
                font-weight: bold;
                font-family: Georgia;
            }
        """)

        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #3D3C3C;
                font-size: 18px;
                font-family: Segoe UI;
            }
        """)

        for label in [self.course_label, self.study_label, self.break_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    background: transparent;
                    border: none;
                    color: #D94F8C;
                    font-size: 16px;
                    font-weight: 600;
                    font-family: Segoe UI;
                }
            """)

        self.course_box.setFixedWidth(330)
        self.course_box.setFixedHeight(50)
        self.course_box.setCursor(Qt.CursorShape.PointingHandCursor)
        self.course_box.setStyleSheet(self.combo_style())

        self.study_spin.setRange(1, 180)
        self.study_spin.setValue(25)
        self.study_spin.setSuffix(" min")
        self.study_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.break_spin.setRange(1, 60)
        self.break_spin.setValue(5)
        self.break_spin.setSuffix(" min")
        self.break_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        for spin in [self.study_spin, self.break_spin]:
            spin.setFixedWidth(115)
            spin.setFixedHeight(50)
            spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spin.setStyleSheet(self.spin_style())

        for button in [
            self.study_minus_button,
            self.study_plus_button,
            self.break_minus_button,
            self.break_plus_button
        ]:
            button.setFixedSize(45, 45)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(self.small_button_style())

        course_row = QHBoxLayout()
        course_row.setSpacing(12)
        course_row.addStretch()
        course_row.addWidget(self.course_label)
        course_row.addWidget(self.course_box)
        course_row.addStretch()

        study_row = QHBoxLayout()
        study_row.setSpacing(10)
        study_row.addStretch()
        study_row.addWidget(self.study_label)
        study_row.addWidget(self.study_minus_button)
        study_row.addWidget(self.study_spin)
        study_row.addWidget(self.study_plus_button)
        study_row.addStretch()

        break_row = QHBoxLayout()
        break_row.setSpacing(10)
        break_row.addStretch()
        break_row.addWidget(self.break_label)
        break_row.addWidget(self.break_minus_button)
        break_row.addWidget(self.break_spin)
        break_row.addWidget(self.break_plus_button)
        break_row.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)

        for button in [
            self.start_button,
            self.pause_button,
            self.resume_button,
            self.reset_button
        ]:
            button.setFixedHeight(55)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(self.button_style())
            button_layout.addWidget(button)

        card_layout.addStretch()
        card_layout.addWidget(self.title)
        card_layout.addWidget(self.mode_label)
        card_layout.addWidget(self.time_label)
        card_layout.addWidget(self.status_label)
        card_layout.addSpacing(18)
        card_layout.addLayout(course_row)
        card_layout.addLayout(study_row)
        card_layout.addLayout(break_row)
        card_layout.addSpacing(22)
        card_layout.addLayout(button_layout)
        card_layout.addStretch()

        card.setLayout(card_layout)

        main_layout.addWidget(card)
        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: white; }")

    def load_courses(self):
        self.course_box.clear()
        self.course_box.addItem("No subject selected", None)

        courses = self.courses_manager.get_user_courses(self.user_id)

        for course in courses:
            self.course_box.addItem(course["course_name"], course["id"])

    def connect_buttons(self):
        self.start_button.clicked.connect(self.start_timer)
        self.pause_button.clicked.connect(self.pause_timer)
        self.resume_button.clicked.connect(self.resume_timer)
        self.reset_button.clicked.connect(self.reset_timer)

        self.study_minus_button.clicked.connect(self.decrease_study_time)
        self.study_plus_button.clicked.connect(self.increase_study_time)

        self.break_minus_button.clicked.connect(self.decrease_break_time)
        self.break_plus_button.clicked.connect(self.increase_break_time)

        self.study_spin.valueChanged.connect(self.update_timer_display)
        self.break_spin.valueChanged.connect(self.update_timer_display)

    def increase_study_time(self):
        self.study_spin.setValue(self.study_spin.value() + 1)

    def decrease_study_time(self):
        self.study_spin.setValue(self.study_spin.value() - 1)

    def increase_break_time(self):
        self.break_spin.setValue(self.break_spin.value() + 1)

    def decrease_break_time(self):
        self.break_spin.setValue(self.break_spin.value() - 1)

    def update_timer_display(self):
        if not self.qt_timer.isActive():
            self.timer_backend.set_durations(
                self.study_spin.value(),
                self.break_spin.value()
            )
            self.time_label.setText(self.timer_backend.get_time_left())
            self.mode_label.setText(self.timer_backend.get_mode_label())

    def start_timer(self):
        study_minutes = self.study_spin.value()
        break_minutes = self.break_spin.value()
        course_id = self.course_box.currentData()

        self.timer_backend.set_durations(study_minutes, break_minutes)
        self.timer_backend.start(self.user_id, course_id)

        self.qt_timer.start(1000)

        self.status_label.setText("Pomodoro started")
        self.start_button.setEnabled(False)
        self.study_spin.setEnabled(False)
        self.break_spin.setEnabled(False)
        self.course_box.setEnabled(False)

        self.study_minus_button.setEnabled(False)
        self.study_plus_button.setEnabled(False)
        self.break_minus_button.setEnabled(False)
        self.break_plus_button.setEnabled(False)

    def update_timer(self):
        result = self.timer_backend.tick()

        self.time_label.setText(result["time_left"])
        self.mode_label.setText(self.timer_backend.get_mode_label())

        if result["status"] == "study_completed":
            QMessageBox.information(
                self,
                "Study Session Saved",
                "Your Pomodoro study session was saved to analytics."
            )
            self.status_label.setText("Break started")

        elif result["status"] == "break_completed":
            self.status_label.setText("Break finished. New focus session started.")

    def pause_timer(self):
        self.timer_backend.pause()
        self.status_label.setText("Paused")

    def resume_timer(self):
        self.timer_backend.resume()
        self.status_label.setText("Running")

    def reset_timer(self):
        self.qt_timer.stop()

        self.timer_backend.set_durations(
            self.study_spin.value(),
            self.break_spin.value()
        )

        self.timer_backend.reset()

        self.time_label.setText(self.timer_backend.get_time_left())
        self.mode_label.setText(self.timer_backend.get_mode_label())
        self.status_label.setText("Timer reset")

        self.start_button.setEnabled(True)
        self.study_spin.setEnabled(True)
        self.break_spin.setEnabled(True)
        self.course_box.setEnabled(True)

        self.study_minus_button.setEnabled(True)
        self.study_plus_button.setEnabled(True)
        self.break_minus_button.setEnabled(True)
        self.break_plus_button.setEnabled(True)

    def card_style(self):
        return """
            QFrame {
                background-color: #FFF9FB;
                border: 1px solid #FADADD;
                border-radius: 24px;
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
                font-size: 16px;
                font-family: Segoe UI;
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
                font-size: 16px;
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

    def spin_style(self):
        return """
            QSpinBox {
                background-color: white;
                color: #3D3C3C;
                border: 1px solid #FADADD;
                border-radius: 16px;
                font-size: 16px;
                font-family: Segoe UI;
                padding: 4px;
            }

            QSpinBox:disabled {
                background-color: #FFF1F6;
                color: #999999;
            }
        """

    def button_style(self):
        return """
            QPushButton {
                background-color: #FFB5C3;
                color: #3D3C3C;
                border: none;
                border-radius: 16px;
                font-size: 17px;
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

            QPushButton:disabled {
                background-color: #FADADD;
                color: #999999;
            }
        """

    def small_button_style(self):
        return """
            QPushButton {
                background-color: #FFB5C3;
                color: #3D3C3C;
                border: none;
                border-radius: 14px;
                font-size: 22px;
                font-weight: bold;
                font-family: Segoe UI;
            }

            QPushButton:hover {
                background-color: #F4A7B9;
                color: white;
            }

            QPushButton:pressed {
                background-color: #E88AAD;
            }

            QPushButton:disabled {
                background-color: #FADADD;
                color: #999999;
            }
        """