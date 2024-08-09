from celery import Celery

# Initialize a new Celery application with the name 'tasks'
# broker-----> messaging between the producer and the consumer 
celery_app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
# backend responsible for storing the results of the tasks. Once a task is completed by a worker, the result is sent back to the backend.

# Update the configuration of the Celery app
celery_app.conf.update(
    result_expires=3600,  # Set the expiration time for task results to 3600 seconds (1 hour)
)

# Redis, an in-memory data structure store, Caching