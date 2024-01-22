import random
import config


class Urn:
    def __init__(self, unknown=False, size=100):
        self.size = size  # Size of urn
        self.unknown = unknown
        self.red_size = random.randint(0, self.size)  # If unknown is true, randomly generates number of red balls in the urn

    # Getters
    def get_size(self):
        return self.size

    def is_unknown(self):
        return self.unknown

    # Setters
    def set_size(self, size):
        self.size = size

    def set_unknown(self, unknown):
        self.unknown = unknown

    def describe(self):
        return f"Urn: [Size: {self.size}, Unknown: {self.unknown}]"

    def draw(self):
        if self.unknown:
            balls = ['Red'] * self.red_size + ['Blue'] * (self.size - self.red_size)
            random.shuffle(balls)
            return random.choice(balls)
        else:  # If known, then 50:50
            if random.uniform(0, 1) < 0.5:  # Generates a float between 0 and 1. If number is less than 0.5 draw red, if more draw blue.
                return 'Red'
            else:
                return 'Blue'


class User:
    def __init__(self):
        self.accept_consent = False
        self.age = 0
        self.education = ""
        self.gender = ""
        self.urn_size = (
            random.choice(
                config.URN_SIZES))  # Drawn from uniform distribution so equal amount of participants per condition with adequate sample size
        self.urn = Urn(size=self.urn_size)
        self.unknown_urn_pos = random.choice(config.URN_POSITIONS)
        self.choice = None
        self.result = None

    # Getters
    def get_accept_consent(self):
        return self.accept_consent

    def get_age(self):
        return self.age

    def get_education(self):
        return self.education

    def get_gender(self):
        return self.gender

    def get_urn_size(self):
        return self.urn_size

    def get_choice(self):
        return self.choice

    def get_unknown_urn_pos(self):
        return self.unknown_urn_pos

    # Setters
    def set_accept_consent(self, accept_consent):
        self.accept_consent = accept_consent

    def set_age(self, age):
        self.age = age

    def set_education(self, education):
        self.education = education

    def set_gender(self, gender):
        self.gender = gender

    def set_urn_size(self, urn_size):
        self.urn_size = urn_size

    def set_choice(self, choice):
        self.choice = choice

    def describe(self):
        return f"User: [Accept Consent: {self.accept_consent}, Age: {self.age}, Education: {self.education}, " \
               f"Gender: {self.gender}, Urn Size: {self.urn_size}, Choice: {self.choice}]"

    def save_to_file(self, filename='data/results.csv'):
        file = open(filename, 'a')
        line = (f'{self.age}, {self.gender}, {self.get_education()}, '
                f'{self.urn_size}, {self.unknown_urn_pos}, {self.choice}, {self.result}')
        file.write(f"{line}\n")
        file.close()
