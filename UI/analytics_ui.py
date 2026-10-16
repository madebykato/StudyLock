from BACKEND.analytics import Analytics
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFrame, QTextEdit, QMessageBox
)

class AnalyticsPage(QWidget):
    def __init__(self, user_id=1):
        super().__init__()

        self.user_id = user_id
        self.analytics = Analytics(user_id=self.user_id)

        self.title = QLabel("Analytics")
        self.subtitle = QLabel("Productivity analysis based on your activity and data")

        self.efficiency_score_label = QLabel("0")
        self.focus_label = QLabel("Focus: 0%")
        self.completion_label = QLabel("Completion: 0%")
        self.consistency_label = QLabel("Consistency: 0%")
        self.weekly_hours_label = QLabel("Weekly hours: 0")

        self.best_time_label = QLabel("Best study time range: Not enough data yet")
        self.pomodoro_label = QLabel("Recommended Pomodoro: Not enough data yet")

        self.details_box = QTextEdit()
        self.risk_box = QTextEdit()

        self.refresh_button = QPushButton("Refresh analytics")
        self.efficiency_button = QPushButton("About Efficiency Score")

        self.setup_ui()
        self.connect_buttons()
        self.load_analytics()

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

        top_layout = QHBoxLayout()
        top_layout.setSpacing(18)

        efficiency_card = self.create_efficiency_card()
        habits_card = self.create_habits_card()

        top_layout.addWidget(efficiency_card)
        top_layout.addWidget(habits_card)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(18)

        self.details_box.setReadOnly(True)
        self.risk_box.setReadOnly(True)

        for box in [self.details_box, self.risk_box]:
            box.setStyleSheet("""
                QTextEdit {
                    background-color: #FFF9FB;
                    color: #3D3C3C;
                    border: 1px solid #FADADD;
                    border-radius: 18px;
                    padding: 14px;
                    font-size: 15px;
                    font-family: Segoe UI;
                }
            """)

        bottom_layout.addWidget(self.details_box)
        bottom_layout.addWidget(self.risk_box)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(14)

        for button in [self.refresh_button, self.efficiency_button]:
            button.setFixedHeight(50)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(self.button_style())
            button_layout.addWidget(button)

        main_layout.addWidget(self.title)
        main_layout.addWidget(self.subtitle)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: white; }")

    def create_efficiency_card(self):
        card = QFrame()
        card.setStyleSheet(self.card_style())

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)

        label = QLabel("Efficiency Score")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #D94F8C;
                font-size: 22px;
                font-weight: bold;
                font-family: Segoe UI;
            }
        """)

        self.efficiency_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.efficiency_score_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #E75480;
                font-size: 72px;
                font-weight: bold;
                font-family: Georgia;
            }
        """)

        for stat_label in [
            self.focus_label,
            self.completion_label,
            self.consistency_label,
            self.weekly_hours_label
        ]:
            stat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_label.setStyleSheet(self.small_label_style())

        layout.addWidget(label)
        layout.addWidget(self.efficiency_score_label)
        layout.addWidget(self.focus_label)
        layout.addWidget(self.completion_label)
        layout.addWidget(self.consistency_label)
        layout.addWidget(self.weekly_hours_label)

        card.setLayout(layout)
        return card

    def create_habits_card(self):
        card = QFrame()
        card.setStyleSheet(self.card_style())

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(16)

        title = QLabel("Study Recommendations")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #D94F8C;
                font-size: 22px;
                font-weight: bold;
                font-family: Segoe UI;
            }
        """)

        for label in [self.best_time_label, self.pomodoro_label]:
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(self.small_label_style())

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.best_time_label)
        layout.addWidget(self.pomodoro_label)
        layout.addStretch()

        card.setLayout(layout)
        return card

    def connect_buttons(self):
        self.refresh_button.clicked.connect(self.load_analytics)
        self.efficiency_button.clicked.connect(self.show_efficiency_explanation)

    def load_analytics(self):
        self.analytics = Analytics(user_id=self.user_id)

        efficiency = self.analytics.efficiency_score()

        self.efficiency_score_label.setText(str(efficiency["score"]))
        self.focus_label.setText(f"Focus: {efficiency['focus_score']}%")
        self.completion_label.setText(
            f"Completion: {efficiency['completion_rate']}%"
        )
        self.consistency_label.setText(
            f"Consistency: {efficiency['consistency']}%"
        )
        self.weekly_hours_label.setText(
            f"Weekly hours: {efficiency['weekly_hours']}"
        )

        feedback_text = "Efficiency Feedback\n\n"
        for feedback in efficiency["feedback"]:
            feedback_text += f"• {feedback}\n"

        feedback_text += (
            f"\nAverage completion time: "
            f"{efficiency['average_completion_days']} day(s)"
        )

        self.details_box.setText(feedback_text)

        risks = self.analytics.risk_by_course()
        risk_text = "Course Risk Prediction\n\n"

        if not risks:
            risk_text += "No course data yet."
        else:
            for course in risks:
                risk_text += (
                    f"{course['course']} — {course['risk_level']} risk "
                    f"({course['risk_score']})\n"
                )
                for reason in course["reasons"]:
                    risk_text += f"   • {reason}\n"
                risk_text += "\n"

        self.risk_box.setText(risk_text)

        best_time = self.analytics.best_study_time()

        if best_time is None:
            self.best_time_label.setText("Best study time: Not enough data")
        else:
            self.best_time_label.setText(
                f"Best study time: "
                f"{best_time['start_hour']}:00 - {best_time['end_hour']}:00 "
                f"with {best_time['average_focus']}% focus"
            )

        recommended = self.analytics.recommended_pomodoro()

        if recommended is None:
            self.pomodoro_label.setText(
                "Recommended Pomodoro: Not enough data"
            )
        else:
            self.pomodoro_label.setText(
                f"Recommended Pomodoro: "
                f"{recommended['recommended_minutes']} minutes"
            )

    def show_efficiency_explanation(self):
        QMessageBox.information(
            self,
            "Efficiency Score",
            "Efficiency Score is calculated using:\n\n"
            "• Average focus score\n"
            "• Task completion rate\n"
            "• Study consistency\n"
            "• Weekly study time\n\n"
            "This makes the score more meaningful than a simple task counter."
        )

    def card_style(self):
        return """
            QFrame {
                background-color: #FFF9FB;
                border: 1px solid #FADADD;
                border-radius: 22px;
            }
        """

    def small_label_style(self):
        return """
            QLabel {
                background: transparent;
                border: none;
                color: #3D3C3C;
                font-size: 17px;
                font-family: Segoe UI;
            }
        """

    def button_style(self):
        return """
            QPushButton {
                background-color: #FFB5C3;
                color: #3D3C3C;
                border: none;
                border-radius: 15px;
                font-size: 16px;
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