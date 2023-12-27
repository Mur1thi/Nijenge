import os
from pathlib import Path
from flask import Flask, g, request, session, redirect, url_for, render_template
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

from models import User, error, Fundraiser, login_required, has_active_fundraiser, Contribution
from models import db

app = Flask(__name__)
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Toa.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-SQLAlchemy
db.init_app(app)

# Get the path to the virtual environment configuration file
venv_cfg_path = Path(os.environ.get('VIRTUAL_ENV')) / 'pyvenv.cfg'

# Read the key from the configuration file
with open(venv_cfg_path, 'r') as f:
    for line in f:
        if line.startswith('export SECRET_KEY='):
            secret_key = line.split('=')[1].strip()
            break

app.config['SECRET_KEY'] = secret_key

# Initialize Flask-Migrate
migrate = Migrate(app, db)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logout')
def logout():
    """Logs the user out by removing the user ID from the session."""

    # Remove the user ID from the session
    session.pop('user_id', None)  # Use pop() to avoid errors if key doesn't exist

    # Redirect to the login page or another appropriate route
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                g.user = user  # Assign user to g for access in other routes
                return redirect(url_for('index'))  # 'index' is the main page
            else:
                return error("Invalid username or password", 400)  # Provide informative error message
        except Exception as e:
            return error(str(e), 500)  # Handling general errors

    return render_template('login.html')  # Render login form for GET requests


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


@app.route('/fundraiser', methods=['GET', 'POST'])
@login_required  # Decorator to check for login status
def fundraiser():
    if has_active_fundraiser():
        # Redirect to fundraiser_success page if user has an active fundraiser
        user_fundraiser = Fundraiser.query.filter_by(user_id=g.user.id).first()
        return redirect(url_for('fundraiser_success', fundraiser_id=user_fundraiser.id))
    else:
        return create_fundraiser()


def create_fundraiser():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        end_date = request.form['end_date']  # Extract from form data
        end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M")  # Convert to datetime
        target_funds = request.form['target_funds']

        try:
            # Check if user already has an active fundraiser
            user_fundraiser = Fundraiser.query.filter_by(user_id=g.user.id).first()
            if user_fundraiser:
                return error(
                    "You already have an active fundraiser. Please complete or cancel it before creating a new one.",
                    400)

            # Create the new fundraiser
            new_fundraiser = Fundraiser(
                user_id=g.user.id,
                name=name,
                description=description,
                end_date=end_date,  # Use the formatted string
                target_funds=target_funds
            )
            db.session.add(new_fundraiser)
            db.session.commit()

            return redirect(url_for('fundraiser_success', fundraiser_id=new_fundraiser.id))  # Redirect to success page

        except Exception as e:
            return error(str(e), 500)  # Handle any errors

    # Render the form for GET requests
    # Retrieve the fundraiser object
    fundraiser = Fundraiser.query.filter_by(user_id=g.user.id).first()
    return render_template('fundraiser.html', fundraiser=fundraiser)


@app.route('/fundraiser_success/<int:fundraiser_id>', methods=['GET', 'POST'])
@login_required  # Ensures the user is logged in
def fundraiser_success(fundraiser_id):
    fundraiser = Fundraiser.query.get_or_404(fundraiser_id)  # Retrieve fundraiser

    if request.method == 'POST':
        message = request.form['message']  # Extract from form data
        save_contribution(fundraiser_id, message)
        return redirect(
            url_for('fundraiser_success', fundraiser_id=fundraiser_id))  # Redirect after saving contribution
    else:
        if not fundraiser:
            return error("Error updating fundraiser", 404)
        # Render the success page for GET requests
        return render_template('fundraiser_success.html', fundraiser=fundraiser)


from datetime import datetime
import re  # Import regular expressions for robust parsing


def save_contribution(fundraiser_id, message):
    try:
        message = request.form['message']
        print(f"Message: {message}")

        contribution_reference = re.search(r'\b[A-Z0-9]{10}\b', message)
        print(f"Contribution Reference Match: {contribution_reference}")
        contribution_reference = contribution_reference.group()

        amount = re.search(r'Ksh([\d,]+)\.', message)
        print(f"Amount Match: {amount}")
        amount = amount.group(1)

        contributor_name = re.search(r'from ([A-Z\s]+) \d', message)
        print(f"Contributor Name Match: {contributor_name}")
        contributor_name = contributor_name.group(1).strip()

        phone_number = re.search(r'(\d+) on', message)
        print(f"Phone Number Match: {phone_number}")
        phone_number = phone_number.group(1)

        contribution_date = re.search(r'on (\d{1,2}/\d{1,2}/\d{2}) at', message)
        print(f"Contribution Date Match: {contribution_date}")
        contribution_date = datetime.strptime(contribution_date.group(1), '%d/%m/%y').date()

        contribution_time = re.search(r'at (\d{1,2}:\d{2} (?:AM|PM))', message)
        print(f"Contribution Time Match: {contribution_time}")
        contribution_time = datetime.strptime(contribution_time.group(1), '%I:%M %p').time()

        # Create a new Contribution object
        contribution = Contribution(
            fundraiser_id=fundraiser_id,
            contribution_reference=contribution_reference,
            contributor_name=contributor_name,
            phone_number=phone_number,
            amount=amount.replace(',', ''),
            contribution_date=contribution_date,
            contribution_time=contribution_time
        )
        # Add the new Contribution to the current database session
        db.session.add(contribution)

        # Try to commit the changes to save the new Contribution to the database
        try:
            db.session.commit()
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

        # Print the new Contribution ID
        print(f"New Contribution ID: {contribution.contribution_id}")
        # Print the contribution columns
        print(f"\nFundraiser ID: {contribution.fundraiser_id}")
        print(f"Contribution Reference: {contribution.contribution_reference}")
        print(f"Contributor Name: {contribution.contributor_name}")
        print(f"Phone Number: {contribution.phone_number}")
        print(f"Amount: {contribution.amount}")
        print(f"Contribution Date: {contribution.contribution_date}")
        print(f"Contribution Time: {contribution.contribution_time}")

        return {
            'status': 'success',
            'message': 'Contribution saved successfully!',
            'data': {
            'fundraiser_id': fundraiser_id,
            'contribution_reference': contribution_reference,
            'amount': amount,
            'contributor_name': contributor_name,
            'phone_number': phone_number,
            'contribution_date': contribution_date,
            'contribution_time': contribution_time,
            }
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


# End of save_contribution


if __name__ == '__main__':
    app.run(debug=True)
