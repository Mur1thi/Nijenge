import json
import math
import os
import secrets
from pathlib import Path
import smtplib
import logging
from dotenv import load_dotenv
from email.message import EmailMessage
from flask import (
    Flask,
    g,
    request,
    session,
    redirect,
    url_for,
    render_template,
    jsonify,
)
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from werkzeug.debug import console
from werkzeug.security import generate_password_hash, check_password_hash
from models import (
    User,
    error,
    Fundraiser,
    login_required,
    has_active_fundraiser,
    Contribution,
)
from models import db


# Load environment variables from .env file
load_dotenv("siri.env")

app = Flask(__name__)
Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Toa.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Flask-SQLAlchemy
db.init_app(app)

# Get the path to the virtual environment configuration file
venv_path = os.environ.get("VIRTUAL_ENV")
venv_cfg_path = None

if venv_path is not None:
    venv_cfg_path = Path(venv_path) / "pyvenv.cfg"

app.config["SECRET_KEY"] = secrets.token_urlsafe(16)

# Initialize Flask-Migrate
migrate = Migrate(app, db)


@app.template_filter('tojson_string')
def tojson_string_filter(value):
    return json.dumps(value)


@app.template_filter("currency_format")
def currency_format(value):
    formatted_value = f"KES {value:,.2f}"  # Format as KES with thousands separator and 2 decimal places
    return formatted_value


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/contact", methods=["POST"])
def contact():
    print("From app.py", request.form)  # Print the entire form data

    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    errors = []
    if not name:
        errors.append("Please fill in the name field")
    if not email:
        errors.append("Please fill in the email field")
    if not message:
        errors.append("Please fill in the message field")

    if errors:
        return jsonify({"status": "error", "message": "\n".join(errors)})

    # Send the email
    try:
        subject = os.environ.get("SUBJECT")
        recipient = os.environ.get("RECIPIENT")
        body = f"Name: {name}\nEmail: {email}\nMessage: {message}"

        send_mail(subject, recipient, body)  # Call the send_mail function

        # Email sent successfully, return success response
        return jsonify({"status": "success", "message": "Email sent successfully!"})

    except Exception as e:
        # Return error response with Toastr notification
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"})


# Create a secure SMTP connection for sending emails
def send_mail(subject, recipient, body):
    msg = EmailMessage()  # More modern message handling
    msg["Subject"] = subject
    msg["From"] = os.getenv("MAIL_USERNAME")
    msg["To"] = recipient
    msg.set_content(body)

    password = os.getenv("MAIL_PASSWORD")
    if password is None:
        raise ValueError("MAIL_PASSWORD environment variable is not set")

    mail_username = os.getenv("MAIL_USERNAME")
    if mail_username is None:
        raise ValueError("MAIL_USERNAME environment variable is not set")

    with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as smtp:
        smtp.login(mail_username, password)
        smtp.send_message(msg)


@app.route("/logout")
def logout():
    """Logs the user out by removing the user ID and name from the session."""

    # Remove the user ID and name from the session
    session.pop("user_id", None)  # Use pop() to avoid errors if key doesn't exist
    session.pop("name", None)  # Remove the name from the session

    # Redirect to the login page or another appropriate route
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                session["user_id"] = user.id
                session["username"] = user.username  # Store the username in the session
                name = user.username.split("@")[0]  # Extract the name before the '@' sign
                session["name"] = name  # Store the name in the session
                g.user = user  # Assign user to g for access in other routes
                return redirect(url_for("index"))  # 'index' is the main page
            else:
                return error(
                    "Invalid username or password", 400
                )  # Provide informative error message
        except Exception as e:
            return error(str(e), 500)  # Handling general errors

    return render_template("login.html")  # Render login form for GET requests


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Password validation
        if not password or not confirm_password:
            return error("Password and confirmation password are required", 400)
        if password != confirm_password:
            return error("Passwords do not match", 400)

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        # Rest of your registration logic
        new_user = User()
        new_user.username = username
        new_user.password = hashed_password
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/fundraiser", methods=["GET", "POST"])
@login_required  # Decorator to check for login status
def fundraiser():
    """
    Handles the "/fundraiser" route for both GET and POST requests.
    
    This function is a route handler for the "/fundraiser" URL. It is decorated with the `@login_required` decorator,
    which means that the user must be logged in to access this route.
    
    The function first checks if the user has an active fundraiser by calling the `has_active_fundraiser()` function.
    If the user has an active fundraiser, the function redirects to the "fundraiser_success" page with the fundraiser ID.
    
    If the user does not have an active fundraiser, the function calls the `create_fundraiser()` function.
    
    Parameters:
        None
        
    Returns:
        - If the user has an active fundraiser:
            - If the `user_fundraiser` object is not None:
                - Prints the fundraiser ID.
                - Renders the "fundraiser_success.html" template with the fundraiser ID and the `user_fundraiser` object.
            - If the `user_fundraiser` object is None:
                - Returns the error message "No active fundraiser found for the user".
        - If the user does not have an active fundraiser:
            - Calls the `create_fundraiser()` function.
    """
    if has_active_fundraiser():
        # Redirect to fundraiser_success page if user has an active fundraiser
        user_fundraiser = Fundraiser.query.filter_by(user_id=g.user.id).first()
        if user_fundraiser is not None:
            print("Fundraiser ID:", user_fundraiser.id)  # Print the fundraiser ID
            return render_template(
                "fundraiser_success.html",
                fundraiser_id=user_fundraiser.id,
                fundraiser=user_fundraiser,
            )
        else:
            # Handle the case where user_fundraiser is None
            # You can return an error message or redirect to another page
            return "No active fundraiser found for the user"
    else:
        return create_fundraiser()


def create_fundraiser():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        end_date = request.form["end_date"]  # Extract from form data
        end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M")  # Convert to datetime
        target_funds = request.form["target_funds"]

        try:
            # Check if user already has an active fundraiser
            user_fundraiser = Fundraiser.query.filter_by(user_id=g.user.id).first()
            if user_fundraiser:
                return error(
                    "You already have an active fundraiser. Please complete or cancel it before creating a new one.",
                    400,
                )

            # Create the new fundraiser
            new_fundraiser = Fundraiser(
                user_id=g.user.id,
                name=name,
                description=description,
                end_date=end_date,  # Use the formatted string
                target_funds=target_funds,
            )
            db.session.add(new_fundraiser)
            db.session.commit()

            return redirect(
                url_for("fundraiser_success", fundraiser_id=new_fundraiser.id)
            )  # Redirect to success page

        except Exception as e:
            logging.error(str(e)) # Works like console.log
            return error(str(e), 500)  # Handle any errors

    # Render the form for GET requests
    # Retrieve the fundraiser object
    fundraiser = Fundraiser.query.filter_by(user_id=g.user.id).first()
    return render_template("fundraiser.html", fundraiser=fundraiser)


from datetime import datetime
from flask import jsonify
import math
import re  # Import regular expressions for robust parsing


@app.route("/fundraiser_success/<int:fundraiser_id>", methods=["GET", "POST"])
@login_required
def save_contribution(fundraiser_id):
    """
    Save a contribution made to a fundraiser.

    This route handles both GET and POST requests to save a contribution made to a fundraiser.
    It requires the user to be logged in.

    Parameters:
        fundraiser_id (int): The ID of the fundraiser to which the contribution is made.

    Returns:
        - If the request method is POST:
            - If the contribution reference, amount, contributor name, phone number, contribution date,
              and contribution time are valid and can be extracted from the message, a JSON response
              with the status "success" and the saved contribution data is returned.
            - If any of the required information is missing or invalid, a JSON response with the status
              "error" and an error message is returned.
        - If the request method is GET:
            - The "fundraiser_success.html" template is rendered with the fundraiser object.

    Raises:
        - If there is an error saving the contribution to the database, a JSON response with the status
          "error" and the error message is returned.
    """
    fundraiser = Fundraiser.query.get_or_404(fundraiser_id)
    if request.method == "POST":
        message = request.form["message"]
        contribution_reference = re.search(r"\b[A-Z0-9]{10}\b", message)
        if not contribution_reference:
            return error("Invalid contribution reference", 400)
        contribution_reference = contribution_reference.group()

        amount = re.search(r"Ksh([\d,]+)\.", message)
        if not amount:
            return error("Invalid amount", 400)
        amount = amount.group(1).replace(",", "")

        contributor_name = re.search(r"from ([A-Z\s]+) \d", message)
        if not contributor_name:
            return error("Invalid contributor name", 400)
        contributor_name = contributor_name.group(1)

        phone_number = re.search(r"(\d+) on", message)
        if not phone_number:
            return error("Invalid phone number", 400)
        phone_number = phone_number.group(1)

        contribution_date = re.search(r"on (\d{1,2}/\d{1,2}/\d{2}) at", message)
        if not contribution_date:
            return error("Invalid contribution date", 400)
        contribution_date = datetime.strptime(
            contribution_date.group(1), "%d/%m/%y"
        ).date()

        contribution_time = re.search(r"at (\d{1,2}:\d{2} (?:AM|PM))", message)
        if not contribution_time:
            return error("Invalid contribution time", 400)
        contribution_time = datetime.strptime(contribution_time.group(1), "%I:%M %p").time()

        contribution = Contribution(
            fundraiser_id=fundraiser_id,
            contribution_reference=contribution_reference,
            contributor_name=contributor_name,
            phone_number=phone_number,
            amount=amount,
            contribution_date=contribution_date,
            contribution_time=contribution_time,
        )
        db.session.add(contribution)
        try:
            db.session.commit()
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

        return jsonify(
            {
                "status": "success",
                "message": "Contribution saved successfully!",
                "data": {
                    "funds_raised": fundraiser.funds_raised,
                    "fundraiser_id": fundraiser_id,
                    "contribution_reference": contribution_reference,
                    "amount": amount,
                    "contributor_name": contributor_name,
                    "phone_number": phone_number,
                    "contribution_date": contribution_date,
                    "contribution_time": contribution_time,
                },
            }
        )

    else:
        return render_template("fundraiser_success.html", fundraiser=fundraiser)

# Route to handle AJAX requests for fetching contributions
@app.route("/report_index")
@login_required
def report_index():
    """
    Retrieves the active fundraiser for the logged-in user and redirects to the report page.
    
    This function is a route handler for the "/report_index" URL. It is decorated with the `@login_required` decorator,
    which means that the user must be logged in to access this route.
    
    The function first calls the `has_active_fundraiser()` function to retrieve the ID of the active fundraiser for
    the logged-in user. If no active fundraiser is found, the function redirects the user to the "/fundraiser" URL.
    
    If an active fundraiser is found, the function fetches the fundraiser object using the `Fundraiser.query.get_or_404()`
    method and assigns it to the `fundraiser` variable.
    
    The function then retrieves the value of the "page" query parameter from the request. If the parameter is not present,
    the default value of 1 is used.
    
    Finally, the function redirects the user to the "/report" URL with the `fundraiser_id` and `page_number` as query parameters.
    
    Returns:
        A redirect response to the "/report" URL with the `fundraiser_id` and `page_number` as query parameters.
    """
    fundraiser_id = has_active_fundraiser()
    if fundraiser_id is None:
        return redirect(url_for("fundraiser"))

    fundraiser = Fundraiser.query.get_or_404(fundraiser_id)  # Fetch the fundraiser

    page_number = request.args.get("page", 1)
    return redirect(
        url_for("report", fundraiser_id=fundraiser.id, page_number=page_number) 
    )

"""
Retrieves all contributions for a specific fundraiser and renders a report template with the contributions.

Parameters:
    fundraiser_id (int): The ID of the fundraiser.

Returns:
    If the 'format' query parameter is 'json', returns a JSON response with a list of contributions.
    Otherwise, renders the 'report.html' template with the fundraiser and contributions data.
"""
# Report route to fetch contributions for a specific fundraiser
@app.route("/report/<int:fundraiser_id>")
@login_required
def report(fundraiser_id):
    # Fetch all contributions for the fundraiser
    fundraiser = Fundraiser.query.get_or_404(fundraiser_id)
    contributions = Contribution.query.filter_by(fundraiser_id=fundraiser_id).all()

    # Convert contributions to a list of dictionaries
    contributions_dict = [
        {
            "reference": contribution.contribution_reference,
            "name": contribution.contributor_name,
            "amount": currency_format(contribution.amount),
            "date": contribution.contribution_date.strftime("%d-%m-%Y"),
            "time": contribution.contribution_time.strftime("%H:%M:%S"),
            "timestamp": contribution.timestamp.strftime("%d-%m-%Y %H:%M:%S"),
        }
        for contribution in contributions
    ]

    if request.args.get("format") == "json":
        # Return JSON response if 'format' query parameter is 'json'
        return jsonify(items=contributions_dict)
    else:
        # Render the template with initial contributions
        return render_template(
            "report.html", fundraiser=fundraiser, contributions=contributions_dict
        )


if __name__ == "__main__":
    app.run(debug=True)
