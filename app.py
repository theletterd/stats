from flask import Flask
from flask_bcrypt import Bcrypt

import secret

app = Flask(__name__)
app.secret_key = secret.FLASK_SECRET_KEY

bcrypt = Bcrypt(app)

import routes


if __name__ == '__main__':
    app.run()
