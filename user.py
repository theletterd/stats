# import bcrypt
import config
from app import bcrypt



class User(object):

    @staticmethod
    def check_login(email, password):
        # 1 - get hashed_password
        #load user object

        # 2 - bcrypt.c
        # bcrypt.checkpw(password.encode("utf-8"), hashed_password)
        hardcoded_password = "butts"
        hashed_password = bcrypt.generate_password_hash(hardcoded_password.encode("utf-8"))

        return bcrypt.check_password_hash(hashed_password, password.encode("utf-8"))

    @staticmethod
    def create_user(email, password):
        # I only expect this to be called from the command line.
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        # we're only allowing a single user.
        assert email == config.ONLY_USER
        pass
