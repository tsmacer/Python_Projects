import os

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QDialog, \
    QCheckBox, QHBoxLayout, QComboBox, QFormLayout, QMessageBox, QTextEdit
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize
import config
from model import User, Urn
from utility import read_file, create_label, create_button, create_layout


class ConsentDialog(QDialog):  # Inheriting properties from QDialog
    def __init__(self, user):
        super().__init__()  # Calling initialisation from parent class of QDialog
        self.user = user
        self.init_ui()

    def init_ui(self):  # To set up UI for Consent Form
        self.setWindowTitle('Consent Form')

        # Read consent_text from file
        consent_text = read_file(config.CONSENT_FILE)
        if consent_text is None:
            consent_text = "Error loading consent text."

        # Using create_label from utility.py
        self.consent_label = create_label(consent_text, font_size=10)

        self.consent_checkbox = QCheckBox('I consent')

        # Using create_button from utility.py
        self.accept_button = create_button('Accept', width=100)
        self.cancel_button = create_button('Cancel', width=100)

        self.accept_button.setEnabled(False)  # Initially disable the button as default

        button_layout = create_layout(orientation='horizontal', widgets=[self.cancel_button, self.accept_button],
            alignment=Qt.AlignCenter)

        layout = create_layout(orientation='vertical', widgets=[self.consent_label, self.consent_checkbox])
        layout.addLayout(button_layout)

        self.accept_button.clicked.connect(self.accept_button_clicked)
        self.cancel_button.clicked.connect(self.reject)  # Close the dialog and exit the application (inherited from QDialog)

        self.consent_checkbox.stateChanged.connect(self.update_accept_button_state)

        self.setLayout(layout)

    def update_accept_button_state(self):
        self.accept_button.setEnabled(self.consent_checkbox.isChecked())

    def accept_button_clicked(self):
        if self.consent_checkbox.isChecked():
            # Set values using setters
            self.user.set_accept_consent(True)
            self.accept()  # Inherited from QDialog
        else:
            self.consent_label.setText('Please check the consent box to proceed.')


class DemographicDialog(QDialog):  # Inheriting from QDialog
    INIT_OPTION = 'Select ...'  # Class variable used in all instances

    def __init__(self, user, verbose=False):  # Input argument of object 'user' from class of 'User'
        super().__init__()  # Proper initialisation from QDialog
        self.user = user
        self.verbose = verbose  # For debugging
        self.init_ui()

    def init_ui(self):  # UI for Demographic Information
        self.setWindowTitle('Participant Information')

        self.age_label = QLabel('Age:')
        self.age_input = QLineEdit()

        self.gender_label = QLabel('Gender:')
        self.gender_combobox = QComboBox()
        self.gender_combobox.addItems([DemographicDialog.INIT_OPTION] + config.GENDER_OPTIONS)

        self.education_label = QLabel('Education Level:')
        self.education_combobox = QComboBox()
        self.education_combobox.addItems([DemographicDialog.INIT_OPTION] + config.EDUCATION_OPTIONS)

        self.submit_button = QPushButton('Submit')

        layout = QFormLayout()
        layout.addRow(self.age_label, self.age_input)
        layout.addRow(self.gender_label, self.gender_combobox)
        layout.addRow(self.education_label, self.education_combobox)
        layout.addRow(self.submit_button)

        self.submit_button.clicked.connect(self.submit_button_clicked)

        self.setLayout(layout)

    def submit_button_clicked(self):  # Data Verification and Error Messages
        age_text = self.age_input.text()

        if age_text.isdigit():
            age = int(age_text)
        else:
            self.show_error_message('Invalid Age', 'Please enter a valid age (a number).')
            return

        if age < 18:
            self.show_error_message('Invalid Age', 'You are too young to participate.')
            return
        elif age > 100:
            self.show_error_message('Invalid Age', 'You are too old to participate.')
            return

        gender = self.gender_combobox.currentText()
        education = self.education_combobox.currentText()
        # Both gender and education are checked, so they're not left at their initial positions
        if gender == DemographicDialog.INIT_OPTION:
            self.show_error_message('Invalid Gender', 'Please enter a gender.')
            return
        if education == DemographicDialog.INIT_OPTION:
            self.show_error_message('Invalid Education', 'Please enter an education.')
            return

        self.user.set_age(age)
        self.user.set_education(education)
        self.user.set_gender(gender)
        if self.verbose:  # To print to console
            print(f'Age: {age}, Gender: {gender}, Education Level: {education}')

        self.accept()

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()  # Inherited from QDialog


class FinalMessageDialog(QDialog):  # Inheriting from QDialog
    def __init__(self, user):  # Same as above
        super().__init__()
        self.user = user

        self.setWindowTitle('Debrief')
        self.setGeometry(200, 200, 800, 400)

        # 0 = urn on right, 1 = left urn. (For user.choice)
        # 0 means unknown/random urn on the right, 1 = unknown urn on left (For user.unknown_urn_pos)
        # Using dictionary to map the combinations of outcome where each key is the combined outcome for user choice and unknown urn pos.
        # E.g., (0, 1) -> Chose urn on right whilst unknown urn on left so user chose known urn thereby unknown is set to False.
        outcomes = {(1, 0): False, (1, 1): True, (0, 0): True, (0, 1): False}
        self.user.urn.set_unknown(outcomes[(self.user.choice, self.user.unknown_urn_pos)])

        picked_ball = self.user.urn.draw()  # Calls draw method to randomly pick a ball
        self.user.result = picked_ball

        if picked_ball == "Blue":
            result = "Win"
        else:
            result = "Lost"

        message = f'You drew a {picked_ball.upper()} ball. You {result}!'

        final_label = create_label(message, font_size=14)

        result_message = read_file(config.FINAL_MSG_FILE)

        result_textbox = QTextEdit()
        # Error checking
        if result_message is not None:
            result_textbox.setPlainText(result_message)
        else:
            result_textbox.setPlainText("Error loading final message text.")

        result_textbox.setReadOnly(True)
        result_textbox.setFont(QFont('Arial', 12, QFont.Normal))

        ok_button = QPushButton('Exit')
        ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(final_label, alignment=Qt.AlignCenter)
        layout.addWidget(result_textbox)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)


class UrnDialog(QDialog):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.head_text = read_file(config.URN_HEADER_TEXT_FILE)
        self.init_ui()

    def handle_img1_press(self, event):
        self.show_final_message(choice=1)

    def handle_img2_press(self, event):
        self.show_final_message(choice=0)

    def init_ui(self):
        self.setWindowTitle('Urn Dialog')
        self.setGeometry(100, 100, 600, 300)
        # Error checking
        if self.head_text is None:
            self.head_text = "Error loading header text."

        top_text_label = create_label(self.head_text, font_size=16)

        # Getting user's urn size and unknown urn position
        urn_size = self.user.get_urn_size()
        unknown_urn_pos = self.user.get_unknown_urn_pos()

        # Retrieving the images and creating labels dependent on urn size
        known_img = f'images/known_{urn_size}.png'
        unknown_img = f'images/unknown_{urn_size}.png'
        known_text = f'50 : 50 mix of {urn_size} balls'
        unknown_text = f'Unknown mix of {urn_size} balls'

        # Assign the appropriate image and label depending on unknown urn position
        if unknown_urn_pos == 0:
            img1_name = known_img
            text_label1 = known_text
            img2_name = unknown_img
            text_label2 = unknown_text
        else:
            img1_name = unknown_img
            text_label1 = unknown_text
            img2_name = known_img
            text_label2 = known_text

        # Image 1
        img1_label = QLabel(self)
        img1_pixmap = QPixmap(img1_name)
        img1_label.setPixmap(img1_pixmap)
        img1_label.setToolTip(text_label1)
        img1_label.mousePressEvent = self.handle_img1_press

        #
        # Label at the bottom of Image 1
        bottom_text_label1 = create_label("Urn A: " + text_label1, font_size=12)
        bottom_text_label1.setAlignment(Qt.AlignCenter)

        # Image 2
        img2_label = QLabel(self)
        img2_pixmap = QPixmap(img2_name)
        img2_label.setPixmap(img2_pixmap)
        img2_label.setToolTip(text_label2)
        img2_label.mousePressEvent = self.handle_img2_press

        # Label at the bottom of Image 2
        bottom_text_label2 = create_label("Urn B: " + text_label2, font_size=12)
        bottom_text_label2.setAlignment(Qt.AlignCenter)

        # Layouts
        main_layout = create_layout()

        top_layout = create_layout(orientation='vertical', widgets=[top_text_label])

        layout = create_layout('horizontal')
        layout.addWidget(img1_label, alignment=Qt.AlignCenter)
        layout.addWidget(img2_label, alignment=Qt.AlignCenter)

        bottom_layout = create_layout(orientation='horizontal', widgets=[bottom_text_label1, bottom_text_label2])

        main_layout.addLayout(top_layout)
        main_layout.addLayout(layout)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def show_final_message(self, choice=0):
        self.user.choice = choice
        final_dialog = FinalMessageDialog(self.user)
        if final_dialog.exec_() == QDialog.Accepted:
            self.accept()
