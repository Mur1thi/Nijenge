from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from models import User, Fundraiser, Contribution  # import db models

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yoursecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Toa.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials'

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Logout logic


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))


@app.route('/fundraiser/<int:id>')
@login_required
def get_fundraiser(id):
    fundraiser = Fundraiser.query.get_or_404(id)
    if fundraiser.user_id != current_user.id:
        return "Not authorized"
    return render_template('fundraiser.html', fundraiser=fundraiser)


# Other routes and views

if __name__ == '__main__':
    app.run(debug=True)
