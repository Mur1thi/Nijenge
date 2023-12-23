from flask_bootstrap import Bootstrap
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yoursecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Toa.db'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
Bootstrap(app)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import models
from models import User, Fundraiser, Contribution

# index route
@app.route('/')
def index():
    return render_template('base.html')

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

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

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


@app.route('/fundraisers/new', methods=['GET', 'POST'])
@login_required
def create_fundraiser():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        goal = request.form['goal']

        fundraiser = Fundraiser(name=name, description=description, goal=goal, user=current_user)

        db.session.add(fundraiser)
        db.session.commit()

        return redirect('/dashboard')

    return render_template('create_fundraiser.html')

@app.route('/my_fundraisers')
@login_required
def my_fundraisers():
    fundraisers = Fundraiser.query.filter_by(user_id=current_user.id).all()
    return render_template('my_fundraisers.html', fundraisers=fundraisers)

@app.route('/fundraiser/<int:id>')
@login_required
def fundraiser(id):
    fundraiser = Fundraiser.query.get_or_404(id)
    if fundraiser.user_id != current_user.id:
        flash('Not authorized')
        return redirect('/dashboard')
    return render_template('fundraiser.html', fundraiser=fundraiser)


@app.route('/fundraiser/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_fundraiser(id):
    fundraiser = Fundraiser.query.get(id)
    if fundraiser.user_id != current_user.id:
        flash('Not authorized')
        return redirect(url_for('dashboard'))

    # Allow edit

@app.route('/contribute', methods=['GET', 'POST'])
@login_required
def contribute():
    # Check if user already has active fundraiser
    current_fundraiser = Fundraiser.query.filter_by(user_id=current_user.id, end_date=None).first()
    if current_fundraiser:
        flash('You already have an active fundraiser')
        return redirect(url_for('dashboard'))

    # Get fundraiser to contribute to
    fundraiser_id = request.form.get('fundraiser_id')
    fundraiser = Fundraiser.query.get(fundraiser_id)
    if not fundraiser:
        flash('Invalid fundraiser')
        return redirect(url_for('dashboard'))

    # Create new contribution
    if request.method == 'POST':
        amount = request.form['amount']
        date = request.form['date']

        contribution = Contribution(
            amount=amount,
            date=date,
            fundraiser=fundraiser,
            user=current_user
        )

        db.session.add(contribution)
        db.session.commit()

        flash('Contribution added!')

    return render_template('contribute.html', fundraiser=fundraiser)


# Other routes and views

if __name__ == '__main__':
    app.run(debug=True)
