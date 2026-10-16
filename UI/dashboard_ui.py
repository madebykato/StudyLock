from BACKEND.dashboard import DashboardManager
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, 
    QVBoxLayout, QFrame, QGridLayout
)

class DashboardPage(QWidget):
    def __init__(self, user_id=1):
        super().__init__()

        self.user_id = user_id
        self.manager = DashboardManager()

        self.title = QLabel("Dashboard")
        self.subtitle = QLabel("Your study overview")

        self.cards = {}

        self.refresh_button = QPushButton("Refresh")

        self.setup_ui()
        self.refresh_button.clicked.connect(self.load_dashboard)
        self.load_dashboard()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 35, 40, 40)
        main_layout.setSpacing(22)

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
                font-size: 19px;
                font-family: Segoe UI;
            }
        """)

        grid = QGridLayout()
        grid.setSpacing(20)

        card_names = [
    ("total_items", "Total Tasks"),
    ("completed_items", "Completed"),
    ("current_items", "Current"),

    ("completion_rate", "Completion Rate"),
    ("next_deadline", "Next Deadline"),
    ("upcoming_exams", "Upcoming Exams"),

    ("total_study_minutes", "Total Study Mins"),
    ("weekly_study_minutes", "Weekly Study Mins"),
    ("average_focus", "Average Focus")
]

        positions = [
            (0, 0), (0, 1), (0, 2),
            (1, 0), (1, 1), (1, 2),
            (2, 0), (2, 1), (2, 2)
        ]

        for index, (key, label) in enumerate(card_names):
            card, value_label = self.create_stat_card(label)
            self.cards[key] = value_label
            row, col = positions[index]
            grid.addWidget(card, row, col)

        self.refresh_button.setFixedHeight(52)
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.setStyleSheet(self.button_style())

        main_layout.addWidget(self.title)
        main_layout.addWidget(self.subtitle)
        main_layout.addSpacing(10)
        main_layout.addLayout(grid)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.refresh_button)

        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: white; }")

    def create_stat_card(self, title):
        card = QFrame()
        card.setMinimumHeight(135)
        card.setStyleSheet("""
            QFrame {
                background-color: #FFF9FB;
                border: 1px solid #FADADD;
                border-radius: 22px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #D94F8C;
                font-size: 17px;
                font-weight: bold;
                font-family: Segoe UI;
            }
        """)

        value_label = QLabel("0")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setWordWrap(True)
        value_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #3D3C3C;
                font-size: 22px;
                font-weight: 600;
                font-family: Georgia;
            }
        """)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)

        return card, value_label

    def load_dashboard(self):
        data = self.manager.dashboard_summary(self.user_id)

        for key, label in self.cards.items():
            value = data.get(key, "—")

            if key == "completion_rate":
                value = f"{value}%"

            if key == "average_focus":
                value = f"{value}%"

            label.setText(str(value))

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
        """