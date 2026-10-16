import sys
import os
from datetime import datetime
from importlib import import_module

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFontDatabase, QFont, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QFrame, QScrollArea
)


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


try:
    from theme import apply_app_theme, prettify_window
except ImportError:
    def apply_app_theme(app):
        pass

    def prettify_window(window):
        pass


def import_class(module_name, possible_class_names):
    module = import_module(module_name)

    for class_name in possible_class_names:
        if hasattr(module, class_name):
            return getattr(module, class_name)

    raise ImportError(
        f"None of these classes were found in {module_name}: "
        f"{possible_class_names}"
    )


AuthPage = import_class("UI.auth_ui", ["AuthPage"])
DashboardPage = import_class("UI.dashboard_ui", ["DashboardPage"])
PomodoroPage = import_class("UI.pomodoro_ui", ["PomodoroPage"])
FocusPage = import_class("UI.focus_ui", ["FocusPage"])
ItemsPage = import_class("UI.items_ui", ["TasksPage", "ItemsPage"])
AnalyticsPage = import_class("UI.analytics_ui", ["AnalyticsPage"])
CourseMapPage = import_class("UI.courses_map_ui", ["CourseMapPage", "CoursesMapPage"])


class MainWindow(QMainWindow):

    THEMES = {
        "pink": {
            "background": "#FFF9FB",
            "card": "#FFFFFF",
            "soft": "#FFF1F6",
            "border": "#FADADD",
            "button": "#FFB5C3",
            "hover": "#F4A7B9",
            "accent": "#E75480",
            "dark": "#D94F8C",
            "text": "#2B2B2B"
        },
        "black": {
            "background": "#111111",
            "card": "#1B1B1B",
            "soft": "#292929",
            "border": "#4A4A4A",
            "button": "#333333",
            "hover": "#555555",
            "accent": "#FFFFFF",
            "dark": "#E6E6E6",
            "text": "#FFFFFF"
        },
        "red": {
            "background": "#FFF1F1",
            "card": "#FFFFFF",
            "soft": "#FFD6D6",
            "border": "#FF8F8F",
            "button": "#FF5C5C",
            "hover": "#DC2626",
            "accent": "#B91C1C",
            "dark": "#7F1D1D",
            "text": "#2B2B2B"
        }
    }

    def __init__(self):
        super().__init__()

        self.setWindowTitle("StudyLock")
        self.setMinimumSize(1050, 680)
        self.resize(1200, 760)

        self.current_user = None
        self.current_user_id = None

        self.current_theme_name = "pink"
        self.theme = self.THEMES[self.current_theme_name]

        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        self.auth_page = AuthPage()
        self.auth_page.user_logged_in.connect(self.open_app)

        self.pages.addWidget(self.auth_page)
        self.pages.setCurrentWidget(self.auth_page)

        self.home_page = None

        self.dashboard_page = None
        self.pomodoro_page = None
        self.focus_page = None
        self.items_page = None
        self.analytics_page = None
        self.course_map_page = None

        self.dashboard_content = None
        self.pomodoro_content = None
        self.focus_content = None
        self.items_content = None
        self.analytics_content = None
        self.course_map_content = None

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000)

#login success
    def open_app(self, user):
        self.current_user = user
        self.current_user_id = user["id"]

        self.clear_old_app_pages()
        self.build_app_pages()

        self.pages.setCurrentWidget(self.home_page)
        self.update_time()

    def clear_old_app_pages(self):
        while self.pages.count() > 1:
            widget = self.pages.widget(1)
            self.pages.removeWidget(widget)
            widget.deleteLater()

    def build_app_pages(self):
        self.home_page = self.create_home_page()

        self.dashboard_content = DashboardPage(user_id=self.current_user_id)
        self.pomodoro_content = PomodoroPage(user_id=self.current_user_id)
        self.focus_content = FocusPage(user_id=self.current_user_id)
        self.items_content = ItemsPage(user_id=self.current_user_id)
        self.analytics_content = AnalyticsPage(user_id=self.current_user_id)
        self.course_map_content = CourseMapPage(user_id=self.current_user_id)

        self.dashboard_page = self.create_page_with_home(self.dashboard_content)
        self.pomodoro_page = self.create_page_with_home(self.pomodoro_content)
        self.focus_page = self.create_page_with_home(self.focus_content)
        self.items_page = self.create_page_with_home(self.items_content)
        self.analytics_page = self.create_page_with_home(self.analytics_content)
        self.course_map_page = self.create_page_with_home(self.course_map_content)

        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.pomodoro_page)
        self.pages.addWidget(self.focus_page)
        self.pages.addWidget(self.items_page)
        self.pages.addWidget(self.analytics_page)
        self.pages.addWidget(self.course_map_page)

    # home custom color

    def set_theme(self, theme_name):
        if theme_name not in self.THEMES:
            return

        self.current_theme_name = theme_name
        self.theme = self.THEMES[theme_name]

        if self.home_page is None:
            return

        old_home = self.home_page

        self.home_page = self.create_home_page()
        self.pages.insertWidget(1, self.home_page)
        self.pages.setCurrentWidget(self.home_page)

        self.pages.removeWidget(old_home)
        old_home.deleteLater()

        self.update_time()

    # date/time

    def update_time(self):
        now = datetime.now()

        if hasattr(self, "home_time_label"):
            self.home_time_label.setText(now.strftime("%H:%M"))

        if hasattr(self, "home_date_label"):
            self.home_date_label.setText(now.strftime("%d %B %Y"))

    # wrapper page

    def create_page_with_home(self, content_page):
        wrapper = QWidget()
        wrapper.setStyleSheet("background-color: #FFFFFF;")

        wrapper_layout = QVBoxLayout()
        wrapper_layout.setContentsMargins(24, 18, 24, 24)
        wrapper_layout.setSpacing(12)

        top_layout = QHBoxLayout()

        home_button = QPushButton("Home")
        home_button.setFixedSize(105, 42)
        home_button.setCursor(Qt.CursorShape.PointingHandCursor)
        home_button.clicked.connect(self.show_home)
        home_button.setStyleSheet("""
            QPushButton {
                background-color: #FFF1F6;
                color: #C45C7C;
                border: 1px solid #F2B8C6;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
                font-family: Segoe UI;
            }

            QPushButton:hover {
                background-color: #F8DDE4;
            }

            QPushButton:pressed {
                background-color: #F0B7C6;
            }
        """)

        top_layout.addWidget(home_button)
        top_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #FFFFFF;
                border: none;
            }

            QScrollBar:vertical {
                background: #FFF1F6;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background: #FFB5C3;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #F4A7B9;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        content_page.setMinimumWidth(950)
        scroll_area.setWidget(content_page)

        wrapper_layout.addLayout(top_layout)
        wrapper_layout.addWidget(scroll_area, 1)

        wrapper.setLayout(wrapper_layout)
        return wrapper

   # home

    def create_home_page(self):
        page = QWidget()
        page.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme["background"]};
            }}
        """)

        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedSize(520, 700)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme["card"]};
                border: 2px solid {self.theme["border"]};
                border-radius: 34px;
            }}
        """)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(40, 28, 40, 28)
        card_layout.setSpacing(10)

        small_welcome = QLabel("Welcome to")
        small_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        small_welcome.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                border: none;
                color: {self.theme["text"]};
                font-size: 20px;
                font-weight: 600;
                font-style: italic;
                font-family: Georgia;
            }}
        """)

        title = QLabel("✮ StudyLock ✮")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                border: none;
                color: {self.theme["accent"]};
                font-size: 40px;
                font-weight: bold;
                font-family: Georgia;
            }}
        """)

        if self.current_user:
            user_text = f"Logged in as {self.current_user['full_name']}"
        else:
            user_text = ""

        self.home_user_label = QLabel(user_text)
        self.home_user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.home_user_label.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                border: none;
                color: {self.theme["dark"]};
                font-size: 15px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
        """)

        divider = QLabel()
        pixmap = QPixmap("divide.png")

        if not pixmap.isNull():
            divider.setPixmap(
                pixmap.scaled(
                    500,
                    80,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        else:
            divider.setText("✦ ✦ ✦")

        divider.setAlignment(Qt.AlignmentFlag.AlignCenter)
        divider.setStyleSheet(f"""
            QLabel {{
                border: none;
                background: transparent;
                color: {self.theme["accent"]};
                font-size: 24px;
            }}
        """)

        time_layout = QHBoxLayout()
        time_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.home_time_label = QLabel()
        self.home_date_label = QLabel()

        time_style = f"""
            QLabel {{
                background: transparent;
                color: {self.theme["text"]};
                border: none;
                font-size: 20px;
                font-style: italic;
                font-weight: normal;
                font-family: Georgia;
            }}
        """

        self.home_time_label.setStyleSheet(time_style)
        self.home_date_label.setStyleSheet(time_style)

        dot = QLabel("★")
        dot.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                color: {self.theme["accent"]};
                border: none;
                font-size: 15px;
                font-style: italic;
            }}
        """)

        time_layout.addWidget(self.home_time_label)
        time_layout.addWidget(dot)
        time_layout.addWidget(self.home_date_label)

        card_layout.addWidget(small_welcome)
        card_layout.addWidget(title)
        card_layout.addWidget(self.home_user_label)
        card_layout.addWidget(divider)
        card_layout.addLayout(time_layout)
        card_layout.addSpacing(12)

        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Pomodoro", self.show_pomodoro),
            ("Focus Mode", self.show_focus),
            ("Items", self.show_items),
            ("Analytics", self.show_analytics),
            ("Course Map", self.show_course_map),
        ]

        for text, function in buttons:
            button = QPushButton(text)
            button.setFixedHeight(50)
            button.clicked.connect(function)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme["soft"]};
                    color: {self.theme["text"]};
                    border: 1px solid {self.theme["border"]};
                    border-radius: 16px;
                    font-size: 18px;
                    font-weight: normal;
                    font-family: Segoe UI;
                }}

                QPushButton:hover {{
                    background-color: {self.theme["hover"]};
                    color: white;
                }}

                QPushButton:pressed {{
                    background-color: {self.theme["button"]};
                }}
            """)
            card_layout.addWidget(button)

        theme_label = QLabel("Theme")
        theme_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        theme_label.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                border: none;
                color: {self.theme["dark"]};
                font-size: 14px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
        """)

        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(10)

        theme_buttons = [
            ("Pink", "pink"),
            ("Black", "black"),
            ("Red", "red")
        ]

        for text, theme_name in theme_buttons:
            theme_button = QPushButton(text)
            theme_button.setFixedHeight(34)
            theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
            theme_button.clicked.connect(
                lambda checked=False, name=theme_name: self.set_theme(name)
            )
            theme_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.THEMES[theme_name]["soft"]};
                    color: {self.THEMES[theme_name]["dark"]};
                    border: 1px solid {self.THEMES[theme_name]["border"]};
                    border-radius: 12px;
                    font-size: 13px;
                    font-weight: 600;
                    font-family: Segoe UI;
                }}

                QPushButton:hover {{
                    background-color: {self.THEMES[theme_name]["hover"]};
                    color: white;
                }}
            """)

            theme_layout.addWidget(theme_button)

        logout_button = QPushButton("Logout")
        logout_button.setFixedHeight(36)
        logout_button.clicked.connect(self.logout)
        logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.theme["dark"]};
                border: none;
                font-size: 15px;
                font-weight: 600;
                font-family: Segoe UI;
            }}

            QPushButton:hover {{
                color: {self.theme["accent"]};
                text-decoration: underline;
            }}
        """)

        card_layout.addSpacing(6)
        card_layout.addWidget(theme_label)
        card_layout.addLayout(theme_layout)
        card_layout.addWidget(logout_button)

        card.setLayout(card_layout)
        outer_layout.addWidget(card)

        page.setLayout(outer_layout)
        return page

#navigation
    def show_home(self):
        self.pages.setCurrentWidget(self.home_page)

    def show_dashboard(self):
        if hasattr(self.dashboard_content, "load_dashboard"):
            self.dashboard_content.load_dashboard()

        self.pages.setCurrentWidget(self.dashboard_page)

    def show_pomodoro(self):
        self.pages.setCurrentWidget(self.pomodoro_page)

    def show_focus(self):
        self.pages.setCurrentWidget(self.focus_page)

    def show_items(self):
        if hasattr(self.items_content, "load_items"):
            self.items_content.load_items()

        self.pages.setCurrentWidget(self.items_page)

    def show_analytics(self):
        if hasattr(self.analytics_content, "load_analytics"):
            self.analytics_content.load_analytics()

        self.pages.setCurrentWidget(self.analytics_page)

    def show_course_map(self):
        self.pages.setCurrentWidget(self.course_map_page)

    def logout(self):
        self.current_user = None
        self.current_user_id = None

        self.clear_old_app_pages()
        self.pages.setCurrentWidget(self.auth_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    font_id = QFontDatabase.addApplicationFont("PlayfairDisplay-Black.ttf")

    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 10))

    apply_app_theme(app)

    window = MainWindow()
    prettify_window(window)
    window.showMaximized()

    sys.exit(app.exec())