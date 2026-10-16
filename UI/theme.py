from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QPushButton, QLineEdit,
    QTableWidget, QHeaderView
)

WHITE = "#FFFFFF"
BABY_PINK = "#FFF1F6"
LIGHT_PINK = "#FFB5C3"
PINK = "#F4A7B9"
DARK_PINK = "#D94F8C"
TEXT = "#3D3C3C"


def apply_app_theme(app):
    app.setFont(QFont("Segoe UI", 10))

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(WHITE))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Base, QColor(WHITE))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Button, QColor(LIGHT_PINK))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    app.setPalette(palette)


def style_title(label):
    label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
    label.setStyleSheet(f"color: {DARK_PINK}; background: transparent;")

def style_subtitle(label):
    label.setFont(QFont("Segoe UI", 12))
    label.setStyleSheet(f"color: {TEXT}; background: transparent;")

def style_button(button):
    button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
    button.setMinimumHeight(38)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {LIGHT_PINK};
            color: {TEXT};
            padding: 8px 12px;
        }}

        QPushButton:hover {{
            background-color: {PINK};
        }}

        QPushButton:pressed {{
            background-color: #E88AAD;
        }}
    """)

def style_input(line_edit):
    line_edit.setFont(QFont("Segoe UI", 10))
    line_edit.setMinimumHeight(34)
    line_edit.setStyleSheet(f"""
        QLineEdit {{
            background-color: {BABY_PINK};
            color: {TEXT};
            padding: 7px;
        }}
    """)

def style_table(table):
    table.setAlternatingRowColors(True)
    table.setFont(QFont("Segoe UI", 10))
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    table.setStyleSheet(f"""
        QTableWidget {{
            background-color: {WHITE};
            alternate-background-color: {BABY_PINK};
            color: {TEXT};
            gridline-color: {LIGHT_PINK};
        }}

        QHeaderView::section {{
            background-color: {LIGHT_PINK};
            color: {TEXT};
            font-weight: bold;
            padding: 0px;
        }}
    """)
def prettify_window(window):
    window.setStyleSheet("")

    for button in window.findChildren(QPushButton):
        if button.styleSheet() == "":
            style_button(button)

    for line_edit in window.findChildren(QLineEdit):
        if line_edit.styleSheet() == "":
            style_input(line_edit)

    for table in window.findChildren(QTableWidget):
        if table.styleSheet() == "":
            style_table(table)