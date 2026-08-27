# Land Registration Management System

A full-stack Land Registration Management Information System built with **FastAPI**, **MongoDB**, **PyMongo**, and a web frontend.

The system manages land registration applications, applicants, parcels, survey tasks, registrar reviews, certificates, objections, and geospatial land information.

## Features

* Land registration application management
* Applicant profiles and application tracking
* Parcel management using GeoJSON
* Application workflow and status transitions
* Automatic surveyor assignment
* Survey task and milestone management
* Registrar review and approval
* Objection and document tracking
* Certificate issuance
* Interactive parcel map
* Analytics and management dashboards
* MongoDB geospatial indexing and queries

## Requirements

* Python 3
* MongoDB
* pip
* Modern web browser

## Installation

Clone the repository:

```bash
git clone https://github.com/Hareth5/Land-Registration-Management-System.git
cd Land-Registration-Management-System
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Database Setup

Make sure MongoDB is installed and running locally.

Create a `.env` file based on `.env.example` and configure your MongoDB connection.

Example:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=land_registration
```

Initialize the MongoDB collections and indexes:

```bash
python database/setup_database.py
```

Load the included sample data:

```bash
python database/sample_data.py
```

The sample data is optional, but recommended for testing and exploring the system after installation.

## Run

Start the FastAPI backend:

```bash
uvicorn main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI API documentation:

```text
http://127.0.0.1:8000/docs
```

Then open the frontend from the project frontend directory in your browser.

## Quick Setup

```bash
git clone https://github.com/Hareth5/Land-Registration-Management-System.git
cd Land-Registration-Management-System

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

python database/setup_database.py
python database/sample_data.py

uvicorn main:app --reload
```

Make sure MongoDB is running and your `.env` configuration is correct before starting the application.

## Team Members

- [ElyasNajeh](https://github.com/ElyasNajeh) — Elyas Ihmud
- [Hareth5](https://github.com/Hareth5)
- [Ahmad-Omaryeh](https://github.com/Ahmad-Omaryeh) — Ahmad Omariyeh
