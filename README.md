# Stock Trading Application

This is a FastAPI-based stock trading application with PostgreSQL database and Redis caching.

## Features

- User management (create user, get user details)
- Stock data management (create and retrieve stock data)
- Transaction handling (create transactions, retrieve user transactions)
- Redis caching for improved performance
- Docker containerization for easy deployment


## API Endpoints

- POST `/users/`: Create a new user
- GET `/users/{username}/`: Get user details
- POST `/stocks/`: Create new stock data
- GET `/stocks/`: Get all stocks
- GET `/stocks/{ticker}/`: Get stock by ticker
- POST `/transactions/`: Create a new transaction
- GET `/transactions/{transaction_id}/`: Get user transactions based on transaction_id
- GET `/transactions/{user_id}/`: Get user transactions based on user_id
- GET `/transactions/{user_id}/{start_timestamp}/{end_timestamp}/`: Get user transactions within a time range

## Project Structure

- `main.py`: FastAPI application and route definitions
- `models.py`: SQLAlchemy ORM models
- `schemas.py`: Pydantic models for request/response schemas
- `database.py`: Database connection and session management
- `Dockerfile`: Instructions for building the Docker image
- `docker-compose.yml`: Docker Compose configuration
- `requirements.txt`: Python dependencies

## Environment Variables

The following environment variables are used in the application from .env file:

- `DATABASE_URL`: PostgreSQL connection URL
- `REDIS_URL`: Redis connection URL

These are set in the `docker-compose.yml` file.


## Step 1: Create the Virtual Environment
First, you'll need to create a virtual environment for your project. This isolates your project’s dependencies from other projects on your machine. Use the following command:

For both Ubuntu and Windows:

python -m venv <your_environment_name>

## Step 2: Activate the Virtual Environment
Next, activate the virtual environment you just created. The activation command differs slightly between Ubuntu and Windows:
For Ubuntu:
source <your_environment_name>/bin/activate
For Windows:
<your_environment_name>\Scripts\Activate.Ps1

## Step 3: Install Required Packages
After activating your virtual environment, you need to install the necessary packages listed in your requirements.txt file. Use the following command:

For both Ubuntu and Windows:
pip install -r requirements.txt

## Step 4: Navigate to the app Folder
Once the packages are installed, navigate to the app folder to access your project files:

Command:
cd app/

## Step 5: Run the Application with Uvicorn
To start your FastAPI application using Uvicorn, use the following command. This command is the same for both Ubuntu and Windows:
uvicorn main:app --reload
Access the app: Open your browser and go to http://127.0.0.1:8000/docs to interact with the FastAPI app.

## Step 6: Run the Celery Worker
If your application uses Celery for task management, you can run the Celery worker with the following command:

Command (same for both Ubuntu and Windows):
celery -A tasks worker --loglevel=info
Monitor tasks: You can monitor tasks at http://127.0.0.1:5555/tasks.

## Step 7: Run Flower for Celery
Flower is a web-based tool for monitoring and administrating Celery clusters. To start Flower, run the following command:

Command (same for both Ubuntu and Windows):
celery -A tasks flower --loglevel=info
Access Flower: You can access the Flower dashboard at http://127.0.0.1:5555/tasks.