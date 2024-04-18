from flask import render_template, session, redirect, url_for, g, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

from functools import wraps

"""
Decorator that checks if a user is logged in before executing the decorated function.

Parameters:
    func (function): The function to be decorated.

Returns:
    function: The decorated function.

"""
def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        g.user = User.query.get(session['user_id'])  # Retrieve user information
        return func(*args, **kwargs)

    return decorated_function


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


# from https://github.com/jacebrowning/memegen#special-characters
def error(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    return render_template("error.html", top=code, bottom=escape(message)), code


class Fundraiser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    end_date = db.Column(db.DateTime, nullable=False)
    target_funds = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('fundraisers', lazy=True))

    def __repr__(self):
        return f'<Fundraiser {self.name}>'

    @property
    def funds_raised(self):
        """
        Calculates the total amount of funds raised for the fundraiser associated with the current instance.
        Returns the total amount raised as an integer. If no funds are raised, returns 0.
        """
        total = (
            db.session.query(func.sum(Contribution.amount))
            .filter_by(fundraiser_id=self.id)
            .scalar()
        )
        return total or 0


# Fundraiser checker function
"""This code snippet defines a function has_active_fundraiser that checks if the current user has an active fundraiser 
by querying the database for a fundraiser associated with the user ID stored in the session. If a fundraiser is found, 
it returns True, otherwise it returns False."""
def has_active_fundraiser():
    """Checks if the current user has an active fundraiser and returns the fundraiser ID."""
    if "user_id" in session:  # Ensure user is logged in
        user_fundraiser = Fundraiser.query.filter_by(user_id=session["user_id"]).first()
        if user_fundraiser:
            return user_fundraiser.id
    return None

from datetime import datetime

class Contribution(db.Model):
    __tablename__ = 'contributions'

    contribution_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fundraiser_id = db.Column(db.Integer, db.ForeignKey('fundraiser.id'), nullable=False)
    contribution_reference = db.Column(db.Text, nullable=False)
    contributor_name = db.Column(db.Text, nullable=False)
    phone_number = db.Column(db.Text, nullable=False)
    amount = db.Column(db.DECIMAL, nullable=False)
    contribution_date = db.Column(db.Date, nullable=False)
    contribution_time = db.Column(db.Time, nullable=False)
    # new timestamp column
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    fundraiser = db.relationship('Fundraiser', backref='contributions')

    def to_dict(self):
        return {
            'contribution_reference': self.contribution_reference,
            'contributor_name': self.contributor_name,
            'phone_number': self.phone_number,
            'amount': self.amount,
            'contribution_time': self.contribution_time.strftime("%H:%M:%S"),  # Convert time to string
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),  # Convert timestamp to string
            'contribution_date': self.contribution_date.strftime("%Y-%m-%d"),  # Convert date to string
        }


    def __repr__(self):
        return f'<Contribution {self.contribution_id} for Fundraiser {self.fundraiser_id}>'
