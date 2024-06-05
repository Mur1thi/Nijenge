import json
import logging
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

# Configure logging to write to a file
logging.basicConfig(filename="Nijenge_app.log", level=logging.DEBUG)


# Load environment variables from .env file
load_dotenv()

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
    logging.info("Received contact form submission")
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
        logging.warning("Contact form submission with errors: %s", errors)
        return jsonify({"status": "error", "message": "\n".join(errors)})

    # Send the email
    try:
        subject = os.environ.get("SUBJECT")
        recipient = os.environ.get("RECIPIENT")
        body = f"Name: {name}\nEmail: {email}\nMessage: {message}"

        send_mail(subject, recipient, body)  # Call the send_mail function

        # Email sent successfully, return success response
        logging.info("Contact email sent successfully to %s", recipient)
        return jsonify({"status": "success", "message": "Email sent successfully!"})

    except Exception as e:
        logging.error(f"An error occurred while sending the email: {str(e)}")
        # Return error response with Toastr notification
        return jsonify({"status": "error", "message": f"An error occurred while sending the email"})


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

from flask import request, get_flashed_messages, flash, make_response, redirect, url_for


@app.route("/messages")
def get_messages():
    messages = get_flashed_messages(with_categories=True)

    if not messages:
        flash_message = request.cookies.get("flash_message")
        if flash_message:
            messages = [("success", flash_message)]

    return jsonify(messages=messages)


@app.route("/logout")
def logout():
    """Logs the user out by removing the user ID and name from the session."""

    # Remove the user ID and name from the session
    session.pop("user_id", None)  # Use pop() to avoid errors if key doesn't exist
    session.pop("name", None)  # Remove the name from the session

    # Redirect to the login page or another appropriate route
    flash("You have been logged out", "info")
    logging.info( "User %s has been logged out", session["username"])
    return redirect(url_for("index"))


from flask import flash, redirect, url_for


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        logging.info(
            "Login attempt for user: %s", username
        )

        try:
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                session["user_id"] = user.id
                session["username"] = user.username  # Store the username in the session
                name = user.username.split("@")[
                    0
                ]  # Extract the name before the '@' sign
                session["name"] = name  # Store the name in the session
                g.user = user  # Assign user to g for access in other routes
                logging.info("Successful login for user: %s", username)
                flash("Login successful", "success")

                # Redirect to index on successful login
                return redirect(url_for("index"))
            else:
                logging.warning("Failed login attempt for user: %s", username)
                flash("Invalid username or password", "error")
                return redirect(url_for("index", login_error="true"))
        except Exception as e:
            flash("There was an error logging in: " + str(e), "error")
            logging.error("Error during login: %s", str(e))
            return redirect(url_for("index", login_error="true"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Registers a new user.

    This function handles the registration of a new user. It is accessed via the "/register" route and supports both GET and POST requests.

    Parameters:
    - None

    Returns:
    - If the request method is POST:
        - If the provided email already exists in the database, a flash message is displayed and the user is redirected to the index page with a "#register-error" anchor.
        - If any of the password or confirmation password fields are empty, a flash message is displayed and the user is redirected to the index page with a "#register-error" anchor.
        - If the provided passwords do not match, a flash message is displayed and the user is redirected to the index page with a "#register-error" anchor.
        - If the registration is successful, a flash message is displayed, the user is logged in the system, and the user is redirected to the index page.
    - If the request method is GET:
        - The "register.html" template is rendered.

    Note:
    - The function assumes that the necessary imports and database setup have been performed.
    - The function uses the Flask framework and the SQLAlchemy ORM to interact with the database.
    - The function uses the `flash` function to display flash messages to the user.
    - The function uses the `logging` module to log information about registration attempts.
    """
    if request.method == "POST":
        username = request.form["username"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Email verification check
        if User.query.filter_by(username=username).first():
            flash("Email already exists. Please use a different email.", "error")
            logging.warning("Registration attempt with existing email: %s", username)
            return redirect(url_for("index") + "#register-error")

        # Password validation
        if not password or not confirm_password:
            flash("Password and confirmation password are required", "error")
            logging.warning("Password and confirmation password are required")
            return redirect(url_for("index") + "#register-error")
        if password != confirm_password:
            flash("Passwords do not match", "error")
            logging.warning("Passwords do not match for username: %s", username)
            return redirect(url_for("index") + "#register-error")

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        # Registration logic
        new_user = User()
        new_user.username = username
        new_user.password = hashed_password
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful", "success")
        logging.info("New user registered successfully: %s", username)
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/fundraiser", methods=["GET", "POST"])
@login_required  # Decorator to check for login status
def fundraiser():
    """
    A route handler for the "/fundraiser" URL. This function is decorated with the `@login_required` decorator,
    which means that the user must be logged in to access this route.
    
    The function checks if the user has an active fundraiser by calling the `has_active_fundraiser()` function.
    If the user has an active fundraiser, the function retrieves the fundraiser object using the `Fundraiser.query.filter_by()`
    method and assigns it to the `user_fundraiser` variable. If the `user_fundraiser` is not `None`, the function logs
    the fundraiser ID and renders the "fundraiser_success.html" template with the fundraiser ID and fundraiser object as
    parameters. If the `user_fundraiser` is `None`, the function logs a warning message and returns a string indicating
    that no active fundraiser was found for the user.
    
    If the user does not have an active fundraiser, the function redirects the user to the "create_fundraiser" route.
    
    If an exception occurs during the execution of the function, the function logs an error message and returns a string
    indicating that an error occurred while processing the request.
    
    Returns:
        - If the user has an active fundraiser, the function returns the rendered "fundraiser_success.html" template with
          the fundraiser ID and fundraiser object as parameters.
        - If the user does not have an active fundraiser, the function returns a string indicating that no active fundraiser
          was found for the user.
        - If an exception occurs, the function returns a string indicating that an error occurred while processing the request.
    """
    try:
        if has_active_fundraiser():
            # Redirect to fundraiser_success page if user has an active fundraiser
            user_fundraiser = Fundraiser.query.filter_by(user_id=g.user.id).first()
            if user_fundraiser is not None:
                logging.info(
                    "Fundraiser ID: %s", user_fundraiser.id
                )  # Log the fundraiser ID
                return render_template(
                    "fundraiser_success.html",
                    fundraiser_id=user_fundraiser.id,
                    fundraiser=user_fundraiser,
                )
            else:
                # Handle the case where user_fundraiser is None
                logging.warning("No active fundraiser found for the user")
                return "No active fundraiser found for the user"
        else:
            return create_fundraiser()
    except Exception as e:
        logging.error("Error in fundraiser route: %s", str(e))
        return "An error occurred while processing your request."


from flask import flash


@app.route("/create_fundraiser", methods=["GET", "POST"])
def create_fundraiser():
    """
    A route handler for the "/create_fundraiser" URL. This function handles both GET and POST requests.
    
    If the request method is POST, the function retrieves the form data for the fundraiser fields (name, description, end_date, target_funds) and converts the end_date to a datetime object.
    
    The function then checks if the user already has an active fundraiser by querying the database. If the user has an active fundraiser, the function displays an error message and redirects the user back to the create_fundraiser page.
    
    If the user does not have an active fundraiser, the function creates a new fundraiser object with the form data and adds it to the database. It then commits the changes and displays a success message.
    
    If an exception occurs during the process, the function logs an error message and displays an error message to the user.
    
    If the request method is GET, the function retrieves the fundraiser object for the current user from the database. If an exception occurs during the retrieval process, the function logs an error message and displays an error message to the user.
    
    Returns:
        - If the request method is POST and the fundraiser is created successfully, the function redirects the user to the fundraiser_success page.
        - If the request method is POST and an exception occurs, the function redirects the user back to the create_fundraiser page.
        - If the request method is GET and the fundraiser is retrieved successfully, the function renders the "fundraiser.html" template with the fundraiser object as a parameter.
        - If the request method is GET and an exception occurs, the function redirects the user to the index page.
    """
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
                flash(
                    "You already have an active fundraiser. Please complete or cancel it before creating a new one.",
                    "error",
                )
                logging.warning("User %s already has an active fundraiser.", g.user.id)
                return redirect(url_for("create_fundraiser"))

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

            flash("Fundraiser created successfully!", "success")
            logging.info("New fundraiser created successfully: %s", new_fundraiser.id)
            return redirect(
                url_for("fundraiser_success", fundraiser_id=new_fundraiser.id)
            )  # Redirect to success page

        except Exception as e:
            logging.error("Error while creating fundraiser: %s", str(e))
            flash(
                "An error occurred while creating the fundraiser. Please try again.",
                "error",
            )
            return redirect(url_for("create_fundraiser"))

    # Render the form for GET requests
    # Retrieve the fundraiser object
    try:
        fundraiser = Fundraiser.query.filter_by(user_id=g.user.id).first()
        logging.info("Rendering fundraiser form for user %s", g.user.id)
        return render_template("fundraiser.html", fundraiser=fundraiser)
    except Exception as e:
        logging.error("Error retrieving fundraiser for user %s: %s", g.user.id, str(e))
        flash(
            "An error occurred while retrieving fundraiser data. Please try again.",
            "error",
        )
        return redirect(url_for("index"))


from datetime import datetime
from flask import jsonify
import re  # Import regular expressions for robust parsing


@app.route("/fundraiser_success/<int:fundraiser_id>", methods=["GET", "POST"])
@login_required
def save_contribution(fundraiser_id):
    """
    Save a contribution for a fundraiser.

    This route handles both GET and POST requests to save a contribution for a fundraiser.

    Parameters:
        fundraiser_id (int): The ID of the fundraiser.

    Returns:
        If the request method is POST:
            If the contribution is successfully saved, returns a JSON response with the following fields:
                - status (str): The status of the response.
                - message (str): A success message.
                - data (dict): A dictionary containing the following fields:
                    - funds_raised (float): The total amount raised by the fundraiser.
                    - fundraiser_id (int): The ID of the fundraiser.
                    - contribution_reference (str): The reference number for the contribution.
                    - amount (float): The amount contributed.
                    - contributor_name (str): The name of the contributor.
                    - phone_number (str): The phone number of the contributor.
                    - contribution_date (str): The date of the contribution in the format 'YYYY-MM-DD'.
                    - contribution_time (str): The time of the contribution in the format 'HH:MM:SS'.
            If there is an error saving the contribution, returns a JSON response with the following fields:
                - status (str): The status of the response.
                - message (str): An error message.
        If the request method is GET:
            Renders the 'fundraiser_success.html' template with the fundraiser object.
            If there is an error rendering the template, returns a JSON response with the following fields:
                - status (str): The status of the response.
                - message (str): An error message.
    """
    try:
        fundraiser = Fundraiser.query.get_or_404(fundraiser_id)
    except Exception as e:
        logging.error(
            "Error retrieving fundraiser with ID %s: %s", fundraiser_id, str(e)
        )
        return jsonify({"status": "error", "message": "Fundraiser not found"})

    if request.method == "POST":
        try:
            message = request.form["message"]
            contribution_reference = re.search(r"\b[A-Z0-9]{10}\b", message)
            if not contribution_reference:
                logging.warning(
                    "Invalid contribution reference in message: %s", message
                )
                return error("Invalid contribution reference", 400)
            contribution_reference = contribution_reference.group()

            amount = re.search(r"Ksh([\d,]+)\.", message)
            if not amount:
                logging.warning("Invalid amount in message: %s", message)
                return error("Invalid amount", 400)
            amount = amount.group(1).replace(",", "")

            contributor_name = re.search(r"from ([A-Z\s]+) \d", message)
            if not contributor_name:
                logging.warning("Invalid contributor name in message: %s", message)
                return error("Invalid contributor name", 400)
            contributor_name = contributor_name.group(1)

            phone_number = re.search(r"(\d+) on", message)
            if not phone_number:
                logging.warning("Invalid phone number in message: %s", message)
                return error("Invalid phone number", 400)
            phone_number = phone_number.group(1)

            contribution_date = re.search(r"on (\d{1,2}/\d{1,2}/\d{2}) at", message)
            if not contribution_date:
                logging.warning("Invalid contribution date in message: %s", message)
                return error("Invalid contribution date", 400)
            contribution_date = datetime.strptime(
                contribution_date.group(1), "%d/%m/%y"
            ).date()

            contribution_time = re.search(r"at (\d{1,2}:\d{2} (?:AM|PM))", message)
            if not contribution_time:
                logging.warning("Invalid contribution time in message: %s", message)
                return error("Invalid contribution time", 400)
            contribution_time = datetime.strptime(
                contribution_time.group(1), "%I:%M %p"
            ).time()

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
                logging.error(
                    "Error committing contribution to the database: %s", str(e)
                )
                return jsonify({"status": "error", "message": str(e)})

            logging.info(
                "Contribution saved successfully for fundraiser ID %s with message: %s", fundraiser_id, message
            )
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
                        "contribution_date": contribution_date.strftime("%Y-%m-%d"),
                        "contribution_time": contribution_time.strftime(
                            "%H:%M:%S"
                        ),  # Convert time to string
                    },
                }
            )

        except Exception as e:
            logging.error("Error processing contribution: %s", str(e))
            return jsonify(
                {
                    "status": "error",
                    "message": "An error occurred while saving the contribution.",
                }
            )

    else:
        try:
            return render_template("fundraiser_success.html", fundraiser=fundraiser)
        except Exception as e:
            logging.error(
                "Error rendering fundraiser success template for fundraiser ID %s: %s",
                fundraiser_id,
                str(e),
            )
            return jsonify(
                {
                    "status": "error",
                    "message": "An error occurred while loading the page.",
                }
            )


# Route to handle AJAX requests for fetching contributions
@app.route("/report_index")
@login_required
def report_index():
    try:
        fundraiser_id = has_active_fundraiser()
        if fundraiser_id is None:
            logging.warning("No active fundraiser found for the user.")
            flash("Please create a fundraiser first", "warning")
            return redirect(url_for("fundraiser"))

        fundraiser = Fundraiser.query.get_or_404(fundraiser_id)  # Fetch the fundraiser
        logging.info("Active fundraiser found for user: %s", fundraiser_id)

        page_number = request.args.get("page", 1)
        return redirect(
            url_for("report", fundraiser_id=fundraiser.id, page_number=page_number)
        )
    except Exception as e:
        logging.error("Error in report_index function: %s", str(e))
        flash("An error occurred. Please try again later.", "error")
        return redirect(url_for("fundraiser"))


# Report route to fetch contributions for a specific fundraiser
@app.route("/report/<int:fundraiser_id>")
@login_required
def report(fundraiser_id):
    try:
        # Fetch all contributions for the fundraiser
        fundraiser = Fundraiser.query.get_or_404(fundraiser_id)
        contributions = Contribution.query.filter_by(fundraiser_id=fundraiser_id).all()
        logging.info("Fetched contributions for fundraiser ID: %s", fundraiser_id)

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
    except Exception as e:
        logging.error(
            "Error in report function for fundraiser ID %s: %s", fundraiser_id, str(e)
        )
        flash(
            "An error occurred while fetching the report. Please try again later.",
            "error",
        )
        return redirect(url_for("fundraiser"))


@app.route("/delete_fundraiser", methods=["POST"])
def delete_fundraiser():
    if "user_id" not in session:
        return jsonify(success=False, message="User not logged in.")

    user_id = session["user_id"]
    fundraiser = Fundraiser.query.filter_by(user_id=user_id).first()

    if not fundraiser:
        return jsonify(success=False, message="No active fundraiser found.")

    try:
        # Download contribution data before deleting (implement your own logic here)
        contributions = Contribution.query.filter_by(fundraiser_id=fundraiser.id).all()
        # Implement download logic, e.g., generate CSV and return as download

        # Delete contributions
        for contribution in contributions:
            db.session.delete(contribution)

        # Delete fundraiser
        db.session.delete(fundraiser)
        db.session.commit()

        return jsonify(
            success=True, message="Fundraiser and contributions deleted successfully."
        )
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e))


if __name__ == "__main__":
    app.run(debug=True)
