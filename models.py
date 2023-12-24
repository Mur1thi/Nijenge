from flask import render_template, session, redirect, url_for, g, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from functools import wraps


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


# Fundraiser checker function
def has_active_fundraiser():
    """Checks if the current user has an active fundraiser."""
    if 'user_id' in session:  # Ensure user is logged in
        user_fundraiser = Fundraiser.query.filter_by(user_id=session['user_id']).first()
        return user_fundraiser is not None
    return False


class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fundraiser_id = db.Column(db.Integer, db.ForeignKey('fundraiser.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    fundraiser = db.relationship('Fundraiser', backref=db.backref('contributions', lazy=True))
    user = db.relationship('User', backref=db.backref('contributions', lazy=True))

    def __repr__(self):
        return f'<Contribution ${self.amount} to {self.fundraiser.name}>'
