FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Hugging Face requires port 7860
EXPOSE 7860

# Run FastAPI on 7860
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "7860"]
