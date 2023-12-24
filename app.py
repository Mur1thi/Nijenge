import os
from pathlib import Path
from flask import Flask, render_template, redirect, url_for, request, session
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate

from models import User, error, Fundraiser, Contribution
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

app = Flask(__name__)
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///toa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Get the path to the virtual environment configuration file
venv_cfg_path = Path(os.environ.get('VIRTUAL_ENV')) / 'pyvenv.cfg'

# Read the key from the configuration file
with open(venv_cfg_path, 'r') as f:
    for line in f:
        if line.startswith('export SECRET_KEY='):
            secret_key = line.split('=')[1].strip()
            break

app.config['SECRET_KEY'] = secret_key

# Initialize SQLAlchemy with Flask app
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            user = User.query.filter_by(username=username).first()

            if not user or not check_password_hash(user.password, password):
                return error("User not found or password incorrect", 403)

            session['user_id'] = user.id
            return redirect(url_for('index'))

        except Exception as e:
            # catch any other exceptions
            return error(str(e), 500)

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Password validation
        if not password or not confirm_password:
            return error("Password and confirmation password are required", 400)
        if password != confirm_password:
            return error("Passwords do not match", 400)

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        # Rest of your registration logic
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)