class UserNotFoundError(Exception):
    pass


class UserNotFoundByIdError(UserNotFoundError):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"User with id - {self.user_id} not found!")

class UserNotFoundByEmailError(UserNotFoundError):
    def __init__(self, user_email):
        self.user_email = user_email
        super().__init__(f"User with email - {self.user_email} not found!")

class UserAlreadyExistsError(Exception):
    def __init__(self, user_email):
        self.user_email = user_email
        super().__init__(f"User with - {self.user_email} already exists!")
