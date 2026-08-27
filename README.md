# Land Registration Management System

A local land-registration workflow application with a FastAPI backend, MongoDB
storage, and a browser-based administration interface.

## Technologies

- Python 3.11 or newer
- FastAPI and Uvicorn
- MongoDB and PyMongo
- HTML, CSS, and modern JavaScript
- Node.js 18 or newer for the dependency-free frontend server
- Leaflet/OpenStreetMap for map visualization

This repository is not a Java project, so a JDK and Maven are not required.

## Features

- Applicant and staff records
- Land-registration applications and status transitions
- Surveyor assignment, milestones, reports, and registrar review
- Notes, missing-document handling, objections, and certificates
- Dashboard, analytics, and zone-based map views

## Requirements

- Python 3.11 or newer
- MongoDB Community Server or a MongoDB Atlas cluster
- Node.js 18 or newer

## Fresh-clone setup

1. Create a Python virtual environment and install the dependencies from the
   repository root.

   PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

   macOS/Linux:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

2. Start MongoDB locally, or create an Atlas cluster. Copy the environment
   example and edit the new local file:

   PowerShell:

   ```powershell
   Copy-Item LandRegistrationAPI\.env.example LandRegistrationAPI\.env
   ```

   macOS/Linux:

   ```bash
   cp LandRegistrationAPI/.env.example LandRegistrationAPI/.env
   ```

   Required database settings:

   ```env
   MONGO_URI=mongodb://127.0.0.1:27017
   MONGO_DB_NAME=land_registration
   ```

   For Atlas, replace `MONGO_URI` with the complete `mongodb+srv://...`
   connection string and configure an Atlas database user and IP access entry.
   Keep credentials only in `LandRegistrationAPI/.env`; all `.env` files are
   ignored by Git. The older `MONGODB_URL` and `DATABASE_NAME` variable names
   remain accepted for compatibility.

3. Create the MongoDB collections, validators, and indexes. This command is
   idempotent and does not insert demo records:

   ```bash
   python database/setup_database.py
   ```

4. Optionally load fictional, interconnected demonstration data:

   ```bash
   python database/sample_data.py
   ```

   Re-running the sample script replaces only records tagged as this sample
   dataset. It does not delete unrelated records.

5. Start the FastAPI backend:

   ```bash
   cd LandRegistrationAPI
   python -m uvicorn app.main:app --reload
   ```

   The API is available at `http://127.0.0.1:8000`; Swagger documentation is at
   `http://127.0.0.1:8000/docs`.

6. In a second terminal, start the frontend using the project's Node command:

   ```bash
   cd LandRegistrationUI
   npm start
   ```

   Open `http://127.0.0.1:5173`. To use a different API location, set
   `API_BASE_URL` before running `npm start`. VS Code Live Server is also
   supported on port 5500.

## MongoDB structure

The setup script configures these collections:

- `land_applications`, `parcels`, `applicants`, and `staff_members`
- `survey_tasks`, `survey_reports`, and `performance_logs`
- `certificates`, `application_documents`, and `objections`

Indexes include the specification's unique application, parcel, applicant,
staff, and certificate identifiers; workflow/query indexes; relationship
indexes; and a `2dsphere` index on `parcels.geometry`.
The surveyor coverage GeoJSON field `staff_members.coverage.geo_fence` also has
a `2dsphere` index.

## Verification

Compile the backend and check frontend JavaScript syntax:

```bash
python -m compileall LandRegistrationAPI/app database
node --check LandRegistrationUI/server.cjs
```

The map page loads Leaflet and map tiles over the internet; all other frontend
assets are bundled in this repository.
