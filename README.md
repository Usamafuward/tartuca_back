# Tartuca Restaurant App - Backend API Service (`tartuca_back`)

This is the core server processing business logic, handling relational database storage, and serving RESTful APIs to both the User and Admin applications.

## 🚀 Features

* **Modular FastAPI Router Design**: Grouped by operational domains (authentication, menu items, reservations, orders, reviews, special offers, and gallery).
* **ORM & Database Modeling**: SQLAlchemy models with robust relation definitions for orders, items, reservations, and user profiles.
* **Database Migrations**: Integrated with Alembic to handle schema changes incrementally and seamlessly.
* **Authentication Protection**: Middleware security checking and validating Auth0 bearer tokens to isolate admin and customer scopes.
* **Automated Documentation**: Interactive API testing playground powered by Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## 🛠️ Setup Instructions

### 1. Prerequisites
Ensure you have the following installed:
- **Python 3.10+**
- **PostgreSQL Server** (Local or cloud-hosted like Aiven, Neon, or Supabase)

### 2. Environment Configuration
Create a `.env` file in this directory (`tartuca_back/`) and specify your configurations:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<dbname>
SECRET_KEY=YOUR_SECURE_RANDOM_SECRET_KEY
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_AUDIENCE=https://api.tartuca.com
```

### 3. Installation
Activate your virtual environment and install all packages:

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS/Linux Terminal:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Database Migrations
Initialize and upgrade your schema using Alembic:
```bash
alembic upgrade head
```

### 5. Seeding Dummy Data (Optional)
To pre-populate your menu, gallery, and initial reviews, run:
```bash
python generate_dummy_data.py
```

### 6. Running the API Server
Start the development server with Uvicorn:
```bash
uvicorn main:app --reload
```

The server will be available at `http://localhost:8000`. You can test endpoints live at `http://localhost:8000/docs`.

---

## 📂 Project Structure

```
tartuca_back/
├── alembic.ini          # Alembic migration runner configuration
├── main.py              # Main app entry point
├── requirements.txt     # Python package dependencies
├── generate_dummy_data.py # Seeding script
├── alembic/             # Folder containing database migrations
└── app/
    ├── __init__.py
    ├── crud.py          # Database operations helpers
    ├── database.py      # SQLAlchemy database engine connection configuration
    ├── models.py        # SQLAlchemy schema definitions
    ├── schemas.py       # Pydantic data serialization schemas
    └── routers/         # API Routers
        ├── admin.py
        ├── auth.py
        ├── gallery.py
        ├── menu.py
        ├── offers.py
        ├── orders.py
        ├── reservations.py
        └── reviews.py
```
