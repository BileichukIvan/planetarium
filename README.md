# Planetarium Ticket Booking System

Do you like learning new things about stars and planets? If so, this project is 100% for you. The Planetarium Ticket Booking System is designed to make visitors happy by allowing them to book tickets online for their favorite ShowSessions in the local Planetarium.

## Project Overview

This system facilitates the management of astronomy shows, show sessions, and ticket reservations. It is designed to be user-friendly for both administrators and customers, ensuring a seamless experience from booking a ticket to attending a show.

## Features

- **JWT authenticated**
- **Admin panel**: /admin/
- **Documentation**: located at /api/schema/swagger/
- **Managing Reservations and tickets**
- **Astronomy Shows**: Add and manage various astronomy shows with detailed descriptions.
- **Planetarium Domes**: Manage the details of different planetarium domes, including seating arrangements.
- **Show Sessions**: Schedule sessions for astronomy shows in different planetarium domes.
- **Ticket Booking**: Allow users to book seats for specific show sessions.
- **Reservations**: Users can reserve multiple tickets under a single reservation.

## Database Structure

Here’s an overview of the database structure:
![Database Structure](db_structure.png)


### Installing using GitHub

Install PostgresSQL and create db

   ```bash
   git clone https://github.com/BileichukIvan/planetarium.git
   cd planetarium_api
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   set DB_HOST=<your db hostname>
   set DB_NAME=<your db name>
   set DB_USER=<your db username>
   set DB_PASSWORD=<your db password>
   set POSTGRES_PORT=<your db port>
   python manage.py migrate
   python manage.py runserver
   ```


### Run with docker

Docker should be installed

```bash
   docker-compose build
   docker-compose up
```

### Getting access

- create user via /api/user/register/
- get access token via /api/user/token/


### Data upload

You can upload data from fixture using 

```python manage.py loaddata planetarium_api_db_data.json```
