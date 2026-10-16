from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QLineEdit, QMessageBox
)

from BACKEND.auth import AuthManager


class AuthPage(QWidget):
    user_logged_in = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.auth_manager = AuthManager()
        self.is_register_mode = False

        self.title = QLabel("StudyLock")
        self.subtitle = QLabel("Login to continue")

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()

        self.main_button = QPushButton("Login")
        self.switch_button = QPushButton("Create an account")

        self.setup_ui()
        self.connect_buttons()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedWidth(520)
        card.setStyleSheet("""
            QFrame {
                background-color: #FFF9FB;
                border: 1px solid #FADADD;
                border-radius: 28px;
            }
        """)

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

        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #3D3C3C;
                font-size: 20px;
                font-family: Segoe UI;
            }
        """)

        self.name_input.setPlaceholderText("Full name")
        self.email_input.setPlaceholderText("Email")
        self.password_input.setPlaceholderText("Password")

        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        for field in [self.name_input, self.email_input, self.password_input]:
            field.setFixedHeight(52)
            field.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    color: #3D3C3C;
                    border: 1px solid #FADADD;
                    border-radius: 16px;
                    padding-left: 16px;
                    padding-right: 16px;
                    font-size: 16px;
                    font-family: Segoe UI;
                }

                QLineEdit:focus {
                    border: 2px solid #FFB5C3;
                }
            """)

        self.name_input.hide()

        self.main_button.setFixedHeight(55)
        self.main_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_button.setStyleSheet("""
            QPushButton {
                background-color: #FFB5C3;
                color: #3D3C3C;
                border: none;
                border-radius: 18px;
                font-size: 18px;
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
        """)

        self.switch_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.switch_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #D94F8C;
                border: none;
                font-size: 15px;
                font-weight: 600;
                font-family: Segoe UI;
            }

            QPushButton:hover {
                color: #E75480;
                text-decoration: underline;
            }
        """)

        card_layout.addWidget(self.title)
        card_layout.addWidget(self.subtitle)
        card_layout.addSpacing(20)

        card_layout.addWidget(self.name_input)
        card_layout.addWidget(self.email_input)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(12)
        card_layout.addWidget(self.main_button)
        card_layout.addWidget(self.switch_button)

        card.setLayout(card_layout)
        main_layout.addWidget(card)

        self.setLayout(main_layout)

        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)

    def connect_buttons(self):
        self.main_button.clicked.connect(self.handle_main_button)
        self.switch_button.clicked.connect(self.switch_mode)

    def switch_mode(self):
        self.is_register_mode = not self.is_register_mode

        self.name_input.clear()
        self.email_input.clear()
        self.password_input.clear()

        if self.is_register_mode:
            self.subtitle.setText("Create your StudyLock account")
            self.name_input.show()
            self.main_button.setText("Register")
            self.switch_button.setText("Already have an account? Login")
        else:
            self.subtitle.setText("Login to continue")
            self.name_input.hide()
            self.main_button.setText("Login")
            self.switch_button.setText("Create an account")

    def handle_main_button(self):
        if self.is_register_mode:
            self.register_user()
        else:
            self.login_user()

    def register_user(self):
        full_name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not full_name or not email or not password:
            QMessageBox.warning(
                self,
                "Missing information",
                "Please fill in all fields."
            )
            return

        result = self.auth_manager.register(full_name, email, password)

        if result["ok"]:
            QMessageBox.information(
                self,
                "Account created",
                "Registration successful. You can now log in."
            )
            self.switch_mode()
            self.email_input.setText(email)
        else:
            QMessageBox.warning(
                self,
                "Registration failed",
                result["message"]
            )

    def login_user(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(
                self,
                "Missing information",
                "Please enter your email and password."
            )
            return

        result = self.auth_manager.login(email, password)

        if result["ok"]:
            self.user_logged_in.emit(result["user"])
        else:
            QMessageBox.warning(
                self,
                "Login failed",
                result["message"]
            )