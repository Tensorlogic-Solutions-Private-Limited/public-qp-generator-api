
# qn_generator_v2
Question generator without Odoo

# FastAPI OAuth2 & JWT Authentication

This is a FastAPI project implementing OAuth2 authentication with JWT and PostgreSQL.

## Setup Instructions

1. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

2. Configure your database in `.env` file:
    ```
    DATABASE_URL=postgresql://user:password@localhost/db
    ```

3. Start the server:
    ```sh
    uvicorn app.main:app --reload
    ```

## Endpoints

- `POST /register`: Register a new user
- `POST /login`: Authenticate and get a JWT token


