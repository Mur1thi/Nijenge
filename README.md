# Nijenge
#### Video Demo:  https://youtu.be/prTN5PxmBTs
#### Description: 
Nijenge is a web application to allow users to create crowdfunding campaigns and track donations. 

## Features

- User authentication (register, login, logout)
- Create and manage crowdfunding campaigns 
- Track donations and contributions
- View campaign contribution reports
- PDF export for contribution reports
- Mobile-friendly responsive design

## Tech Stack

- Flask
- SQLAlchemy
- SQLite
- Bootstrap
- Jinja

## Structure

```
fundraising-platform
├── app.py
├── models.py
├── forms.py
├── api.py
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── scripts.js 
│   │   └── Toastr.js
│   └── assets/
│       └── logo.png
├── templates/
│   ├── layout.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── fundraiser.html
│   ├── fundraiser_success.html 
│   └── report.html
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
├── requirements.txt
├── README.md
├── tests/
│   ├── conftest.py
│   ├── test_app.py
│   └── test_api.py 
├── venv/
└── .gitignore
```

## Main Files

- `app.py` - Flask application factory and routes
- `models.py` - Database models
- `forms.py` - WTForms for validation
- `api.py` - REST API endpoints 

## Folders

- `static/` - CSS, JS, images 
- `templates/` - Jinja templates
- `migrations/` - Schema migration config and scripts 
- `tests/` - pytest unit tests
- `venv/` - Python virtual environment

## Frontend

The frontend uses Bootstrap for styling and layout. Additional JS libraries used:

- jQuery - For AJAX requests and DOM manipulation
- Toastr - For notification messages 
- JSPDF - For generating PDF exports

The main frontend files are:

- `static/css/styles.css` - Custom CSS 
- `static/js/scripts.js` - Custom JS code 
- `templates/layout.html` - Base layout
- `templates/index.html` - Homepage
- `templates/login.html` - Login page
- `templates/register.html` - Registration page
- `templates/error.html` - Error page 

Frontend code handles:

- Navigation and layout
- Form submission and validation
- Displaying success/error messages (with Toastr)
- Logging in and out
- PDF report generation

## Authentication

The app uses built-in Flask sessions for authentication. Users can:

- Register a new account 
- Log in to an existing account
- Log out 

Passwords are hashed using `werkzeug.security` before storing in the database.

The `@login_required` decorator is used to protect views that require authentication.

## Campaigns

The `/fundraiser` page allows users to create a new crowdfunding campaign.

They can enter:

- Name 
- Description
- End date
- Target funds amount

This information is submitted to the `/fundraiser` endpoint which handles creation and saving the new campaign.

Once created, users are redirected to the campaign page.

## Campaign Page

`/fundraiser_success/<id>` displays the created campaign and allows updating contributions.

It shows:

- Name 
- Description
- End date
- Target funds

There is a form to enter a contribution message text. This is used to extract details like the contribution amount and contributor name.

The data is submitted to the `save_contribution` API endpoint.

The response from the API is used to display a success or error notification.

## Testing Campaigns

To manually test creating and updating campaigns:

1. Register a new account
2. Go to `/fundraiser` and create a new campaign 
3. Enter any test data for the fields
4. You'll be redirected to the campaign page
5. Try submitting a few test contribution messages and verify if they are saved correctly

Some example contribution messages:

```
You have received Ksh 1,000.00 from John Doe 0722333333 on 12/12/22 at 3:30 PM
You have received Ksh 2,345.67 from Jane Doe 0733444444 on 31/12/22 at 12:00 PM  
```

The endpoint parses these messages to extract the relevant details.

## Database

SQLAlchemy is used as the ORM for the SQLite database. The main models are:

- `User` - To represent a user account
- `Fundraiser` - Crowdfunding campaigns created by users
- `Contribution` - Donations made to a fundraiser

Database relationships, queries, inserts and updates are defined in `models.py`.

## Database Schema

The database uses SQLite and SQLAlchemy ORM. 

The main tables are:

### Users

Stores user accounts.

Columns:

- `id` - Primary key
- `username` - Unique username 
- `password` - Hashed password

### Fundraisers 

Stores fundraising campaigns created by users.

Columns: 

- `id` - Primary key
- `user_id` - Foreign key to users table 
- `name` - Name of fundraiser
- `description` - Longer description 
- `end_date` - Campaign end date
- `target_funds` - Fundraising target amount

### Contributions

Stores donations made to fundraisers.

Columns:

- `contribution_id` - Primary key
- `fundraiser_id` - Foreign key to fundraisers table
- `contribution_reference` - Payment reference code  
- `contributor_name` - Name of donor
- `phone_number` - Donor phone number
- `amount` - Donation amount 
- `contribution_date` - Date of donation
- `contribution_time` - Time of donation
- `timestamp` - Timestamp of insertion

## Migrations

Schema migrations are handled using Alembic.

To run migrations:

```
# Initialize migration config
alembic init migrations

# Generate a new migration
alembic revision --autogenerate -m "Create user table"

# Run migrations
alembic upgrade head
```

This allows safely making schema changes and deploying updates.

## API

The `save_contribution` endpoint provides a REST API to submit and save a new contribution via AJAX.

The response returns:

- `success` or `error` status
- message
- contribution data (if successful)

Frontend JS code handles calling this endpoint and displaying the response.

## Installation

1. Clone the repository

```
git clone https://github.com/Mur1thi/Nijenge.git
```

2. Create and activate a virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Run the application

```
flask run
```

The app will be served at `http://127.0.0.1:5000/`

## Usage

**Register a new user account**

Go to `/register` and enter a username and password.

**Login** 

Go to `/login` and enter your credentials.

**Create a campaign**

Go to `/fundraiser`, fill out the form and submit.

**View campaign contributions**

Go to `/report` to see a paginated list of contributions.

**Download contribution report** 

Click the "Download PDF" button on the `/report` page.


## Testing

Automated tests using `pytest`.

Run tests:

```
pytest
```

## Config Files

- `requirements.txt` - Python package dependencies
- `.gitignore` - Exclude files from Git
- `README.md` - Documentation
