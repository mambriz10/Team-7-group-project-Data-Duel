import Person

class emails:
    def __init__(self):
        self.emails = {}

    # Used to add a new Person to the list based on their email
    def add(self, email):
        if email not in self.emails:
            self.emails[email] = Person.Person()

    def remove(self, email):
        if email in self.emails:
            del self.emails[email]