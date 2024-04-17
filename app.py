import json
import math
import os
import smtplib
from pathlib import Path
import secrets
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
from flask_mail import Mail, Message
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
venv_cfg_path = Path(os.environ.get('VIRTUAL_ENV')) / 'pyvenv.cfg'

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
        subject = "Contact Form Submission"
        recipient = "elp1262017@gmail.com"  # Your recipient email
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

    with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as smtp:
        smtp.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))
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
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/fundraiser", methods=["GET", "POST"])
@login_required  # Decorator to check for login status
def fundraiser():
    if has_active_fundraiser():
        # Redirect to fundraiser_success page if user has an active fundraiser
        user_fundraiser = Fundraiser.query.filter_by(user_id=g.user.id).first()
        print("Fundraiser ID:", user_fundraiser.id)  # Print the fundraiser ID
        return render_template(
            "fundraiser_success.html",
            fundraiser_id=user_fundraiser.id,
            fundraiser=user_fundraiser,
        )
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
            console.log(str(e))
            return error(str(e), 500)  # Handle any errors

    # Render the form for GET requests
    # Retrieve the fundraiser object
    fundraiser = Fundraiser.query.filter_by(user_id=g.user.id).first()
    return render_template("fundraiser.html", fundraiser=fundraiser)


from datetime import datetime
import re  # Import regular expressions for robust parsing


@app.route("/fundraiser_success/<int:fundraiser_id>", methods=["GET", "POST"])
@login_required  # Ensures the user is logged in
def save_contribution(fundraiser_id):
    if request.method == "POST":
        message = request.form["message"]
        print(f"Message: {message}")

        contribution_reference = re.search(r"\b[A-Z0-9]{10}\b", message)
        print(f"Contribution Reference Match: {contribution_reference}")
        contribution_reference = contribution_reference.group()

        amount = re.search(r"Ksh([\d,]+)\.", message)
        print(f"Amount Match: {amount}")
        amount = amount.group(1)

        contributor_name = re.search(r"from ([A-Z\s]+) \d", message)
        print(f"Contributor Name Match: {contributor_name}")
        contributor_name = contributor_name.group(1).strip()

        phone_number = re.search(r"(\d+) on", message)
        print(f"Phone Number Match: {phone_number}")
        phone_number = phone_number.group(1)

        contribution_date = re.search(r"on (\d{1,2}/\d{1,2}/\d{2}) at", message)
        print(f"Contribution Date Match: {contribution_date}")
        contribution_date = datetime.strptime(
            contribution_date.group(1), "%d/%m/%y"
        ).date()

        contribution_time = re.search(r"at (\d{1,2}:\d{2} (?:AM|PM))", message)
        print(f"Contribution Time Match: {contribution_time}")
        contribution_time = str(
            datetime.strptime(contribution_time.group(1), "%I:%M %p").time()
        )

        # Create a new Contribution object
        contribution = Contribution(
            fundraiser_id=fundraiser_id,
            contribution_reference=contribution_reference,
            contributor_name=contributor_name,
            phone_number=phone_number,
            amount=amount.replace(",", ""),
            contribution_date=contribution_date,
            contribution_time=datetime.strptime(contribution_time, "%H:%M:%S").time(),
        )
        print(f"Fundraiser ID: {fundraiser_id}")
        print(f"Contribution Date: {contribution.contribution_date}")
        print(f"Contribution Time: {contribution.contribution_time}")
        print(f"Contribution Reference: {contribution.contribution_reference}")
        print(f"Contributor Name: {contribution.contributor_name}")
        print(f"Phone Number: {contribution.phone_number}")
        print(f"Amount: {contribution.amount}")
        # Add the new Contribution to the current database session
        db.session.add(contribution)

        # Try to commit the changes to save the new Contribution to the database
        try:
            db.session.commit()
        except Exception as e:
            return {"status": "error", "message": str(e)}

        return {
            "status": "success",
            "message": "Contribution saved successfully!",
            "data": {
                "fundraiser_id": fundraiser_id,
                "contribution_reference": contribution_reference,
                "amount": amount,
                "contributor_name": contributor_name,
                "phone_number": phone_number,
                "contribution_date": contribution_date,
                "contribution_time": contribution_time,
            },
        }
        # Render the form for a fresh Update request
        # Retrieve the fundraiser object

    else:
        # handle GET request...
        # Retrieve the fundraiser object
        fundraiser = Fundraiser.query.filter_by(user_id=g.user.id).first()
        return render_template("fundraiser_success.html", fundraiser=fundraiser)


@app.route("/report_index")
@login_required  # login is required for both creating fundraisers and viewing reports
def report_index():
    fundraiser_id = has_active_fundraiser()  # Get the fundraiser ID if it exists
    if fundraiser_id is None:
        return redirect(url_for("fundraiser"))

    # Get a default page number or retrieve it from a query parameter
    page_number = request.args.get("page", 1)

    return redirect(
        url_for("report", fundraiser_id=fundraiser_id, page_number=page_number)
    )


@app.route("/report/<int:fundraiser_id>/page/<int:page_number>")
@login_required
def report(fundraiser_id, page_number):
    try:
        if fundraiser_id == 0:
            return redirect(
                url_for("fundraiser")
            )  # Call create_fundraiser() when fundraiser_id is 0

        fundraiser = Fundraiser.query.get_or_404(fundraiser_id)

        # Pagination vars
        per_page = 10
        start = (page_number - 1) * per_page

        # Query contributions
        contributions = Contribution.query.filter_by(fundraiser_id=fundraiser_id)

        # Execute paginated query
        results = contributions.limit(per_page).offset(start).all()

        # Convert results to dicts and pass them to template
        contributions_dicts = [contribution.to_dict() for contribution in results]
        # Calculate total pages
        total_contributions = contributions.count()
        total_pages = math.ceil(total_contributions / per_page)

        # Render template
        return render_template(
            "report.html",
            fundraiser=fundraiser,
            contributions=contributions_dicts,
            total_pages=total_pages,
            current_page=page_number,
        )
    except Exception as e:
        # Handle errors appropriately, e.g., log the error and return a user-friendly message
        # Log the error for debugging and troubleshooting
        app.logger.error(f"Error generating report: {str(e)}")
        # Return a user-friendly error message or redirect to an error page
        return error(
            "An error occurred while generating the report. Please try again later.",
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)
