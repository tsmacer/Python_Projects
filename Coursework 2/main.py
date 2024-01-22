import sys
import config
from model import User, Urn
from views import *


def show_consent_dialog(user):
    consent_dialog = ConsentDialog(user)
    return consent_dialog.exec_() == QDialog.Accepted


def show_demographic_dialog(user):
    participant_info_dialog = DemographicDialog(user)
    return participant_info_dialog.exec_() == QDialog.Accepted


def show_urn_dialog(user):
    urn_dialog = UrnDialog(user)
    urn_dialog.exec_()


def start_experiment():
    """
        This function initialises and starts the experiment.

        Begins with the consent dialog presented to participant. If consent is given, user gives demographic information
        about themselves. The actual experiment begins with the urn display and ball draw. At the end, participant data
        is saved in a .csv file.
    """
    app = QApplication([])

    user = User()

    if show_consent_dialog(user):
        if show_demographic_dialog(user):
            show_urn_dialog(user)
            user.save_to_file()


start_experiment()
