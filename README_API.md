# Complaints API

## Installation

- Create and activate a virtual environment.
#### Install dependencies:
-  pip install fastapi uvicorn sqlalchemy

### Configuration
- Set the DATABASE_URL environment variable.

- If DATABASE_URL is not provided, the application uses:
sqlite:///complaints.db

Do not commit database credentials to source control.

### Running
From the project root:
- uvicorn src.main:app --reload

#### Health Checks
- Liveness:
GET /health/live

- Readiness:
GET /health/ready

The readiness endpoint checks database availability.
OpenAPI

With the application running, interactive API documentation is available at:
/docs
