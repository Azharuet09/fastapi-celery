FROM python:3.10-slim

# Create a non-root user
RUN useradd -ms /bin/bash celeryuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flower  # Explicitly install Flower

COPY . .

# Change ownership of the app directory
RUN chown -R celeryuser:celeryuser /app

# Switch to the non-root user
USER celeryuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
