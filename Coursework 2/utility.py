from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt


def read_file(file_path):
    file = open(file_path, 'r')
    content = file.read()
    file.close()
    return content


def create_label(text, font='Arial', font_size=12, font_weight=QFont.Normal):
    label = QLabel(text)
    label.setFont(QFont(font, font_size, font_weight))
    return label


def create_button(text, width=100):
    button = QPushButton(text)
    button.setFixedWidth(width)
    return button


def create_layout(orientation='vertical', widgets=None, alignment=None):
    if orientation == 'horizontal':
        layout = QHBoxLayout()
    else:
        layout = QVBoxLayout()

    if alignment:
        layout.setAlignment(alignment)

    if widgets:
        for widget in widgets:
            layout.addWidget(widget)

    return layout
