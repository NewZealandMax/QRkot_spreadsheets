from .charity_project import CharityProject
from .donation import Donation


def get_donation_model():
    return Donation

def get_project_model():
    return CharityProject
