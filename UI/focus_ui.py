from BACKEND.focus import FocusDetector
import threading
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame,
    QComboBox, QMessageBox, QListView
)


class FocusPage(QWidget):
    focus_finished = pyqtSignal(dict)
    focus_error = pyqtSignal(str)

    def __init__(self, user_id=1):
        super().__init__()

        self.user_id = user_id
        self.detector = None
        self.focus_thread = None
        self.last_result = None
        self.camera_pinned = False

        self.title = QLabel("Focus Mode")
        self.status_label = QLabel("Camera is not running")
        self.score_label = QLabel("Focus score: 0%")
        self.mode_label = QLabel("Mode:")

        self.mode_box = QComboBox()
        self.mode_box.addItems(["soft", "normal", "hard"])
        self.mode_box.setCurrentText("normal")
        self.mode_box.setView(QListView())

        self.start_button = QPushButton("Start Focus")
        self.stop_button = QPushButton("Stop")
        self.pin_button = QPushButton("Pin Camera: OFF")

        self.stop_button.setEnabled(False)

        self.setup_layout()
        self.connect_buttons()

    def setup_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 35, 40, 40)
        main_layout.setSpacing(25)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFF9FB;
                border: 1px solid #FADADD;
                border-radius: 24px;
            }
        """)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #E75480;
                font-size: 48px;
                font-weight: bold;
                font-family: Georgia;
            }
        """)

        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #3D3C3C;
                border: none;
                font-size: 24px;
                font-weight: 500;
                font-family: Segoe UI;
            }
        """)

        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #D94F8C;
                border: none;
                font-size: 36px;
                font-weight: bold;
                font-family: Georgia;
            }
        """)

        self.mode_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.mode_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #3D3C3C;
                font-size: 17px;
                font-family: Segoe UI;
                font-weight: 500;
            }
        """)

        self.mode_box.setFixedWidth(290)
        self.mode_box.setFixedHeight(55)
        self.mode_box.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mode_box.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #3D3C3C;
                border: 1px solid #FADADD;
                border-radius: 16px;
                padding-left: 18px;
                font-size: 17px;
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
                min-height: 32px;
                padding: 8px;
                color: #3D3C3C;
                background-color: white;
            }

            QComboBox QAbstractItemView::item:selected {
                background-color: #FFB5C3;
                color: #3D3C3C;
            }
        """)

        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(14)
        mode_layout.addStretch()
        mode_layout.addWidget(self.mode_label)
        mode_layout.addWidget(self.mode_box)
        mode_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(18)

        for button in [self.start_button, self.stop_button, self.pin_button]:
            button.setFixedHeight(55)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet("""
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
            """)
            button_layout.addWidget(button)

        card_layout.addStretch()
        card_layout.addWidget(self.title)
        card_layout.addWidget(self.status_label)
        card_layout.addWidget(self.score_label)
        card_layout.addSpacing(20)
        card_layout.addLayout(mode_layout)
        card_layout.addSpacing(25)
        card_layout.addLayout(button_layout)
        card_layout.addStretch()

        card.setLayout(card_layout)
        main_layout.addWidget(card)
        self.setLayout(main_layout)

    def connect_buttons(self):
        self.start_button.clicked.connect(self.start_focus)
        self.stop_button.clicked.connect(self.stop_focus)
        self.pin_button.clicked.connect(self.toggle_pin_camera)

        self.focus_finished.connect(self.handle_focus_finished)
        self.focus_error.connect(self.handle_focus_error)

    def toggle_pin_camera(self):
        self.camera_pinned = not self.camera_pinned

        if self.camera_pinned:
            self.pin_button.setText("Pin Camera: ON")
            self.status_label.setText("Camera will stay pinned on top")
        else:
            self.pin_button.setText("Pin Camera: OFF")
            self.status_label.setText("Camera pinning is off")

    def start_focus(self):
        if self.focus_thread is not None and self.focus_thread.is_alive():
            QMessageBox.warning(
                self,
                "Focus Mode",
                "Focus Mode is already running."
            )
            return

        selected_mode = self.mode_box.currentText()

        self.detector = FocusDetector(mode=selected_mode)
        self.last_result = None

        self.status_label.setText(
            f"Focus Mode running in {selected_mode.upper()} mode. Press ESC to exit."
        )
        self.score_label.setText("Focus score: running...")

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.mode_box.setEnabled(False)
        self.pin_button.setEnabled(False)

        self.focus_thread = threading.Thread(
            target=self.run_focus_worker,
            daemon=True
        )
        self.focus_thread.start()

    def run_focus_worker(self):
        try:
            result = self.detector.run_focus_session(
                user_id=self.user_id,
                duration_minutes=None,
                keep_on_top=self.camera_pinned
            )

            self.focus_finished.emit(result)

        except Exception as error:
            self.focus_error.emit(str(error))

    def stop_focus(self):
        if self.detector is not None:
            if hasattr(self.detector, "request_stop"):
                self.detector.request_stop()
                self.status_label.setText("Stopping Focus Mode...")
            else:
                QMessageBox.information(
                    self,
                    "Stop Focus Mode",
                    "Press ESC on the camera window to stop Focus Mode."
                )

    def handle_focus_finished(self, result):
        self.last_result = result

        self.status_label.setText("Focus session finished")
        self.score_label.setText(f"Focus score: {result['focus_score']}%")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.mode_box.setEnabled(True)
        self.pin_button.setEnabled(True)

        QMessageBox.information(
            self,
            "Focus Session Finished",
            f"Mode: {result['mode']}\n"
            f"Focus score: {result['focus_score']}%\n"
            f"Distracted seconds: {result['distracted_seconds']}\n"
            f"Duration: {result['duration_minutes']} minute(s)"
        )

    def handle_focus_error(self, error_message):
        self.status_label.setText("Focus Mode error")
        self.score_label.setText("Focus score: 0%")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.mode_box.setEnabled(True)
        self.pin_button.setEnabled(True)

        QMessageBox.critical(
            self,
            "Focus Mode Error",
            error_message
        )