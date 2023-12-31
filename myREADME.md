# TOA
#### Video Demo:  https://youtu.be/prTN5PxmBTs
#### Description: 
Toa is a web application that helps track fundraisers and donations. I created this app to solve the problem of keeping track of digital mobile money fundraising donations, which is a common issue in Nairobi.

### File structure Overview
1. Instance: This folder contains the projects sqlite3 database.
2. Node_modules: This contains jspdf dependencies
3. Static: This folder contains the assets, css, and js folders
4. Templates: This folder contains all the html files used in this project
5. app.py: This file contains all the application routes and functions
5. models.py: This file contains all my database model classes and functions

### Contents
1. Instance: This is a sqlite database with 3 tables. 
   The contributions table contains data about all the digital payments done towards a fundraiser.
   The fundraiser table contains data about user created fundraisers. It contains information on the fundraiser
   The User table contains information about registered users and hashed passwords
2. node_modules